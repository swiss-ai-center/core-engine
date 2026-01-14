import asyncio
import json
import re
from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session, select, desc
from connection_manager.connection_manager import ConnectionManager, get_connection_manager
from connection_manager.models import Message, MessageType, MessageSubject, MessageToSend
from database import get_session
from common_code.logger.logger import Logger, get_logger
from uuid import UUID
from http_client import HttpClient
from storage.service import StorageService
from tasks.models import Task, TaskUpdate, TaskStatus
from common.exceptions import NotFoundException, CouldNotSendJsonException
from pipeline_executions.service import PipelineExecutionsService
from pipeline_executions.models import PipelineExecution, FileKeyReference
from pipelines.models import Pipeline
from services.models import Service, ServiceTask
from config import Settings, get_settings
from httpx import HTTPError


def create_message(task: Task) -> Message:
    """
    Create a message from a task
    :param task: The task to create the message from
    :return: The message
    """
    if task.status == TaskStatus.SCHEDULED or \
            task.status == TaskStatus.PENDING or \
            task.status == TaskStatus.ARCHIVED or \
            task.status == TaskStatus.FETCHING or \
            task.status == TaskStatus.SAVING:
        message_type = MessageType.INFO
        message_text = f"Task for {task.service.slug} created"
    elif task.status == TaskStatus.PROCESSING or \
            task.status == TaskStatus.FINISHED:
        message_type = MessageType.SUCCESS
        if task.status == TaskStatus.PROCESSING:
            message_text = f"Task for {task.service.slug} processing"
        else:
            message_text = f"Task for {task.service.slug} finished"
    elif task.status == TaskStatus.ERROR:
        message_type = MessageType.ERROR
        message_text = f"Task for {task.service.slug} failed"
        if task.error_message is not None:
            message_text += f"\n\n {task.error_message}"
    elif task.status == TaskStatus.SKIPPED:
        message_type = MessageType.INFO
        message_text = f"Task for {task.service.slug} skipped due to condition evaluation"
    else:
        message_type = MessageType.WARNING
        message_text = f"Task for {task.service.slug} unknown status"
    return Message(
        message={
            "text": message_text,
            "data": task.model_dump(),
        },
        type=message_type, subject=MessageSubject.EXECUTION
    )


def end_pipeline_execution(pipeline_execution: PipelineExecution):
    """
    End the pipeline execution
    :param pipeline_execution: The pipeline execution to end
    """
    pipeline_execution.current_pipeline_step_id = None
    pipeline_execution.files = None


def set_error_state(pipeline_execution: PipelineExecution, task_id: UUID):
    """
    Set the pipeline execution task to error state
    :param pipeline_execution: The pipeline execution to set error state for
    :param task_id: The task id to set error state for
    """
    # Set the pipeline execution task to error state and skip remaining tasks

    for task in pipeline_execution.tasks:
        if task.id == task_id:
            task.status = TaskStatus.ERROR
            break


def sanitize(condition: str):
    """
    Sanitize the condition
    :param condition: The condition to sanitize
    :return: The sanitized condition
    """
    # sanitize condition for eval
    condition = condition.replace("==", "==")
    condition = condition.replace("&&", "and")
    condition = condition.replace("||", "or")
    condition = condition.replace("!", "not ")
    return condition


class TasksService:
    def __init__(
            self,
            logger: Logger = Depends(get_logger),
            session: Session = Depends(get_session),
            http_client: HttpClient = Depends(),
            pipeline_executions_service: PipelineExecutionsService = Depends(),
            settings: Settings = Depends(get_settings),
            storage_service: StorageService = Depends(),
            connection_manager: ConnectionManager = Depends(get_connection_manager),
    ):
        self.logger = logger
        self.logger.set_source(__name__)
        self.session = session
        self.http_client = http_client
        self.pipeline_executions_service = pipeline_executions_service
        self.settings = settings
        self.storage_service = storage_service
        self.connection_manager = connection_manager

    def find_many(self, skip: int = 0, limit: int = 100, order_by: str = "updated_at", order: str = "desc"):
        """
        Find many tasks
        :param skip: number of tasks to skip
        :param limit: number of tasks to return
        :param order_by: field to order by
        :param order: order to sort by
        :return: list of tasks
        """
        self.logger.debug("Find many tasks")

        if order == "desc":
            return self.session.exec(select(Task).order_by(desc(order_by)).offset(skip).limit(limit)).all()
        else:
            return self.session.exec(select(Task).order_by(order_by).offset(skip).limit(limit)).all()

    def create(self, task: Task):
        """
        Create task
        :param task: task to create
        :return: created task
        """
        self.logger.debug("Creating task")

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        self.logger.debug(f"Created task with id {task.id}")

        return task

    def find_one(self, task_id: UUID):
        """
        Find one task
        :param task_id: id of task to find
        :return: task
        """
        self.logger.debug("Find task")

        return self.session.get(Task, task_id)

    async def get_status_from_service(self, task: Task):
        """
        Get task status from service
        :param task: task to get status for
        :return: task with status
        """
        self.logger.debug("Get task status from service")
        status = await self.http_client.get(f"{task.service.url}/tasks/{task.id}/status")
        status = json.loads(status.content.decode("utf-8"))

        task.status = status["status"]
        self.logger.debug(f"Got status {task.status} from service {task.service.url}")

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task

    async def update(self, task_id: UUID, task: TaskUpdate):
        """
        Update task
        :param task_id: id of task to update
        :param task: task data to update
        :return: updated task
        """
        self.logger.debug("Update task")
        current_task = self.session.get(Task, task_id)
        if not current_task:
            raise NotFoundException("Task Not Found")
        task_data = task.model_dump(exclude_unset=True)
        self.logger.debug(f"Updating task {task_id} with data: {task_data}")

        for key, value in task_data.items():
            setattr(current_task, key, value)

        self.session.add(current_task)
        self.session.commit()
        self.session.refresh(current_task)
        self.logger.debug(f"Updated task with id {current_task.id}")

        self.logger.debug(f"Sending task {current_task} to client")
        message = create_message(current_task)
        if current_task.pipeline_execution_id:
            await self.send_message(message, current_task.pipeline_execution, current_task)
        else:
            try:
                connection = self.connection_manager.find_by_linked_id(task_id)
                if connection and connection.websocket:
                    await asyncio.ensure_future(self.connection_manager.send_json(message, task_id))
                else:
                    self.logger.debug(f"Task {task_id} has no client to send message to. Probably using API.")
            except CouldNotSendJsonException as e:
                self.logger.error(f"Could not send task {current_task} to client: {e}")
                self.connection_manager.message_queue.add(
                    MessageToSend(message=message, linked_id=task_id))

        return current_task

    def delete(self, task_id: UUID):
        """
        Delete task
        :param task_id: id of task to delete
        """
        self.logger.debug("Delete task")
        current_task = self.session.get(Task, task_id)
        if not current_task:
            raise NotFoundException("Task Not Found")
        self.session.delete(current_task)
        self.session.commit()
        self.logger.debug(f"Deleted task with id {current_task.id}")

    async def send_message(self, message: Message, pipeline_execution: PipelineExecution, task: Task,
                           general_status: TaskStatus = None):
        if general_status:
            message.message.data["general_status"] = general_status
        try:
            connection = self.connection_manager.find_by_linked_id(pipeline_execution.id)
            if connection:
                if connection.websocket:
                    await asyncio.ensure_future(
                        self.connection_manager.send_json(message, pipeline_execution.id))
                else:
                    self.logger.debug(
                        f"Pipeline execution {pipeline_execution.id} has no client to send message "
                        f"to. Probably using API.")
            else:
                self.logger.debug(
                    f"Pipeline execution {pipeline_execution.id} has no client to send message to. "
                    f"Probably using API.")
        except CouldNotSendJsonException as e:
            self.logger.error(f"Could not send task {task} to client: {e}")
            self.connection_manager.message_queue.add(
                MessageToSend(message=message, linked_id=pipeline_execution.id))

    def skip_remaining_tasks(self, pipeline_execution: PipelineExecution):
        """
        Skip remaining tasks in the pipeline execution
        :param pipeline_execution: The pipeline execution to skip remaining tasks for
        """
        for task in pipeline_execution.tasks:
            if task.status == TaskStatus.SCHEDULED:
                task.status = TaskStatus.SKIPPED
            self.session.add(task)
        self.session.commit()

    async def stop_pipeline_execution(self, task: Task):
        """
        Stop pipeline execution
        :param task: The task to stop the pipeline execution for
        """
        self.logger.debug("Stop pipeline execution")
        pipeline_execution = self.session.get(PipelineExecution, task.pipeline_execution_id)
        if not pipeline_execution:
            raise NotFoundException("Pipeline Execution Not Found")

        message = create_message(task)
        message.message.text = "Execution stopped"
        message.message.data["general_status"] = TaskStatus.ERROR

        await self.send_message(message, pipeline_execution, task)

        self.skip_remaining_tasks(pipeline_execution)
        end_pipeline_execution(pipeline_execution)

        self.session.add(pipeline_execution)
        self.session.commit()
        self.logger.debug(f"Stopped pipeline execution with id {pipeline_execution.id}")

    async def launch_next_step_in_pipeline(self, task: Task):
        """
        Launch the next step(s) in the pipeline
        :param task: The task that has been completed
        """

        self.logger.debug("Launch next step(s) in pipeline")

        pipeline_execution = self.session.get(PipelineExecution, task.pipeline_execution_id)
        if not pipeline_execution:
            raise NotFoundException("Pipeline Execution Not Found")

        # Expect FINISHED or SKIPPED to trigger downstream work
        if task.status not in {TaskStatus.FINISHED, TaskStatus.SKIPPED}:
            self.logger.error(
                f"Task {task.id} status is {task.status}. Expected {TaskStatus.FINISHED} or {TaskStatus.SKIPPED}"
            )

        # Find task index in execution
        try:
            task_index = next(i for i, t in enumerate(pipeline_execution.tasks) if t.id == task.id)
        except StopIteration:
            raise NotFoundException("Associated Task in Pipeline Execution Not Found")

        # Get pipeline and steps
        pipeline = self.session.get(Pipeline, pipeline_execution.pipeline_id)
        if not pipeline:
            raise NotFoundException("Associated Pipeline Not Found")

        current_pipeline_step = pipeline.steps[task_index]

        # Append produced files (if any) from finished task
        service = self.session.get(Service, task.service_id)
        if not service:
            raise NotFoundException("Associated Service Not Found")

        if task.status == TaskStatus.FINISHED and task.data_out:
            files = list(pipeline_execution.files or [])
            for index, file_key in enumerate(task.data_out):
                # service.data_out_fields can be a list of dicts or pydantic models; use name accordingly
                field_def = service.data_out_fields[index]
                field_name = field_def["name"] if isinstance(field_def, dict) else getattr(field_def, "name",
                                                                                           f"out_{index}")
                reference = f"{current_pipeline_step.identifier}.{field_name}"
                files.append(FileKeyReference(reference=reference, file_key=file_key))
            pipeline_execution.files = files

        # Pipeline finished if all tasks are in a final state
        final_states = {TaskStatus.FINISHED, TaskStatus.SKIPPED}
        if all(t.status in final_states for t in pipeline_execution.tasks):
            self.logger.debug(f"Sending task {task} to client")
            message = create_message(task)
            message.message.text = "Execution finished"
            await self.send_message(message, pipeline_execution, task, general_status=TaskStatus.FINISHED)
            end_pipeline_execution(pipeline_execution)
            self.session.add(pipeline_execution)
            self.session.commit()
            self.session.refresh(pipeline_execution)
            self.logger.debug(f"Pipeline execution finished with id: {pipeline_execution.id}")
            return pipeline_execution

        # Build completed identifiers set
        completed_identifiers = {
            pipeline.steps[idx].identifier
            for idx, t in enumerate(pipeline_execution.tasks)
            if t.status in final_states
        }

        # Find steps ready to start: task still SCHEDULED and all needs satisfied
        ready_indices = []
        for idx, step in enumerate(pipeline.steps):
            if pipeline_execution.tasks[idx].status != TaskStatus.SCHEDULED:
                continue
            needs = step.needs or []
            if all(n in completed_identifiers for n in needs):
                ready_indices.append(idx)

        # Collect coroutines to post ready tasks concurrently
        post_coroutines = []
        post_context = []  # tuples: (next_task, next_service)

        # Helper to get reference/file\_key from FileKeyReference or dict
        def get_ref(fkr) -> str | None:
            return getattr(fkr, "reference", None) if not isinstance(fkr, dict) else fkr.get("reference")

        def get_key(fkr) -> str | None:
            return getattr(fkr, "file_key", None) if not isinstance(fkr, dict) else fkr.get("file_key")

        for idx in ready_indices:
            next_step = pipeline.steps[idx]
            next_task = pipeline_execution.tasks[idx]

            # Resolve input files by matching references already present in pipeline\_execution.files
            task_files = []
            for file_input in next_step.inputs or []:
                for f in (pipeline_execution.files or []):
                    if get_ref(f) == file_input:
                        fk = get_key(f)
                        if fk:
                            task_files.append(fk)
                        break

            # Evaluate condition if present
            if next_step.condition:
                condition = next_step.condition
                files_mapping = {}
                for f in (pipeline_execution.files or []):
                    fk = get_key(f)
                    ref = get_ref(f)
                    if not fk or not ref or fk not in task_files:
                        continue
                    alias = re.sub(r"[-.]", "_", ref)
                    ext = fk.rsplit(".", 1)[-1].lower() if "." in fk else ""
                    try:
                        content_bytes = await self.storage_service.get_file_as_bytes(fk)
                        if ext == "txt":
                            files_mapping[alias] = content_bytes.decode("utf-8")
                            condition = condition.replace(ref, alias)
                        elif ext == "json":
                            files_mapping[alias] = json.loads(content_bytes.decode("utf-8"))
                            condition = condition.replace(ref, alias)
                        else:
                            self.logger.debug(f"Condition input {fk} ignored (unsupported ext \'{ext}\')")
                    except Exception as e:
                        self.logger.error(f"Could not download file {fk} from storage: {e}")

                condition_clean = sanitize(condition)
                if not eval(condition_clean, {}, files_mapping):
                    self.logger.info(
                        f"Condition {condition_clean} evaluated to False for step {next_step.identifier}. Skipping."
                    )
                    next_task.status = TaskStatus.SKIPPED
                    next_task.data_in = task_files
                    self.session.add(next_task)
                    self.session.commit()
                    self.session.refresh(next_task)

                    # notify client about skipped task
                    self.logger.debug(f"Sending task {next_task} to client")
                    message = create_message(next_task)
                    await self.send_message(message, pipeline_execution, next_task, general_status=TaskStatus.FINISHED)
                    continue

            # Prepare task to run
            next_task.data_in = task_files
            next_task.service_id = next_step.service_id
            next_task.status = TaskStatus.PENDING
            self.session.add(next_task)
            self.session.commit()
            self.session.refresh(next_task)

            # Prepare service task payload and request
            next_service = self.session.get(Service, next_step.service_id)
            service_task = ServiceTask(
                s3_access_key_id=self.settings.s3_access_key_id,
                s3_secret_access_key=self.settings.s3_secret_access_key,
                s3_region=self.settings.s3_region,
                s3_host=self.settings.s3_host,
                s3_bucket=self.settings.s3_bucket,
                task=next_task,
                callback_url=f"{self.settings.host}/tasks/{next_task.id}"
            )

            post_coroutines.append(
                self.http_client.post(f"{next_service.url}/compute", json=jsonable_encoder(service_task)))
            post_context.append((next_task, next_service))

        # Fire all ready tasks concurrently
        if post_coroutines:
            results = await asyncio.gather(*post_coroutines, return_exceptions=True)
            for (res, (launched_task, launched_service)) in zip(results, post_context):
                try:
                    if isinstance(res, Exception):
                        raise res
                    if res.status_code != 200:
                        raise HTTPException(status_code=res.status_code, detail=res.text)

                    # notify client that task is launched
                    self.logger.debug(f"Sending task {launched_task} to client")
                    message = create_message(launched_task)
                    await self.send_message(message, pipeline_execution, launched_task)

                except (HTTPException, HTTPError, Exception) as e:
                    # On error, mark error and terminate pipeline
                    self.logger.error(f"Sending request to the service {launched_service.name} failed: {str(e)}")
                    set_error_state(pipeline_execution, launched_task.id)
                    self.skip_remaining_tasks(pipeline_execution)
                    end_pipeline_execution(pipeline_execution)

                    self.logger.debug(f"Sending task {launched_task} to client")
                    message = create_message(launched_task)
                    await self.send_message(message, pipeline_execution, launched_task, general_status=TaskStatus.ERROR)

                    self.session.add(pipeline_execution)
                    self.session.commit()
                    self.session.refresh(pipeline_execution)
                    return pipeline_execution

        # Persist pipeline\_execution updates
        self.session.add(pipeline_execution)
        self.session.commit()
        self.session.refresh(pipeline_execution)
        self.logger.debug(f"Pipeline execution updated with data: {pipeline_execution}")
        return pipeline_execution
