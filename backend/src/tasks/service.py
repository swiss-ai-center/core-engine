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
from pipeline_steps.models import PipelineStep
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
                if connection:
                    if connection.websocket:
                        await asyncio.ensure_future(
                            self.connection_manager.send_json(message, task_id))
                    else:
                        self.logger.debug(
                            f"Task {task_id} has no client to send message to. Probably using API.")
                else:
                    self.logger.debug(
                        f"Task {task_id} has no client to send message to. Probably using API.")
                if self.connection_manager.find_by_linked_id(task_id):
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
        Launch the next step in the pipeline
        :param task: The task that has been completed
        """

        # TODO: How to handle parallel steps?

        self.logger.debug("Launch next step in pipeline")

        pipeline_execution = self.session.get(PipelineExecution, task.pipeline_execution_id)

        # Check if pipeline execution exists
        if not pipeline_execution:
            raise NotFoundException("Pipeline Execution Not Found")

        # Check if task status is completed
        if task.status != TaskStatus.FINISHED:
            self.logger.error(f"Task {task.id} status is {task.status}. Expected status is {TaskStatus.FINISHED}")

        current_pipeline_step = self.session.get(PipelineStep, pipeline_execution.current_pipeline_step_id)

        # Check if pipeline step exists
        if not current_pipeline_step:
            raise NotFoundException("Current Pipeline Step Not Found")

        pipeline = self.session.get(Pipeline, current_pipeline_step.pipeline_id)

        # Check if pipeline exists
        if not pipeline:
            raise NotFoundException("Associated Pipeline Not Found")

        # Get Service associated with task
        service = self.session.get(Service, task.service_id)

        # Check if service exists
        if not service:
            raise NotFoundException("Associated Service Not Found")

        # Use task.data_out to append pipeline_execution.files
        if task.data_out:
            # Make a copy of pipeline_execution.files. This will allow SQLModel to detect changes.
            files = pipeline_execution.files.copy()

            # Append new files to files
            for index, file in enumerate(task.data_out):
                service_data_out_field_name = service.data_out_fields[index]["name"]
                reference = f"{current_pipeline_step.identifier}.{service_data_out_field_name}"
                files.append(FileKeyReference(reference=reference, file_key=file))

            # Set back the new files to pipeline_execution.files
            pipeline_execution.files = files

        # Check if current pipeline step is the last one
        if current_pipeline_step.id == pipeline.steps[-1].id:
            # send message to client
            self.logger.debug(f"Sending task {task} to client")
            message = create_message(task)
            # change message text to "Execution finished"
            message.message.text = "Execution finished"
            # send end message to client
            await self.send_message(message, pipeline_execution, task, general_status=TaskStatus.FINISHED)
            # end the pipeline execution
            end_pipeline_execution(pipeline_execution)
        else:
            should_post_task = True
            next_pipeline_step_id = pipeline.steps[pipeline.steps.index(current_pipeline_step) + 1].id

            # Get the next pipeline step
            next_pipeline_step = self.session.get(PipelineStep, next_pipeline_step_id)
            pipeline_execution.current_pipeline_step_id = next_pipeline_step_id

            # Get the next pipeline service
            next_service = self.session.get(Service, next_pipeline_step.service_id)

            # Get the task of the next pipeline step
            sql_statement = select(Task).join(PipelineExecution).join(Service).where(
                (Task.pipeline_execution_id == pipeline_execution.id) &
                (PipelineExecution.id == pipeline_execution.id) &
                (Service.id == next_pipeline_step.service_id)
            )

            # Execute the query using exec() and fetch the first result
            task = self.session.exec(sql_statement).first()

            # Get the files for the next pipeline step
            task_files = []
            for file_input in next_pipeline_step.inputs:
                for file in pipeline_execution.files:
                    if file["reference"] == file_input:
                        task_files.append(file["file_key"])
                        break

            # Check if a condition is set for the pipeline step
            if next_pipeline_step.condition:
                condition = next_pipeline_step.condition
                files_mapping = {}
                # Extract the files needed from the condition
                # If files found, download the required files (text and JSON only) from S3 and update the condition
                # to match a variable to a file
                for file in pipeline_execution.files:
                    # Get the file key
                    file_key = file["file_key"]

                    # Get the file reference
                    file_reference = file["reference"]

                    # Get the file extension
                    file_extension = file_key.split(".")[-1]

                    # Check if file key is in task_files
                    if file_key in task_files:
                        file_reference_one_word = re.sub(r"[-.]", "_", file_reference)

                        # Check if file is a text file
                        if file_extension == "txt":
                            try:
                                # Download the file from S3
                                file_content = await self.storage_service.get_file_as_bytes(file_key)

                                # Add the file to the files mapping
                                files_mapping[file_reference_one_word] = file_content.decode("utf-8")

                                # Update the condition
                                condition = condition.replace(
                                    file_reference,
                                    file_reference_one_word
                                )
                            except Exception as e:
                                self.logger.error(f"Could not download file {file_key} from S3.: {e}")

                        # Check if file is a JSON file
                        elif file_extension == "json":
                            try:
                                # Download the file from S3
                                file_content = await self.storage_service.get_file_as_bytes(file_key)

                                # Add the file to the files mapping as a JSON object
                                files_mapping[file_reference_one_word] = json.loads(file_content.decode("utf-8"))

                                # Update the condition
                                condition = condition.replace(
                                    file_reference,
                                    file_reference_one_word
                                )
                            except Exception as e:
                                self.logger.error(f"Could not download file {file_key} from S3.: {e}")
                        else:
                            self.logger.warning(f"File {file_key} is not a text or JSON file. "
                                                f"It will not be used in the condition.")

                # Evaluate the condition
                condition_clean = sanitize(condition)
                if not eval(condition_clean, {}, files_mapping):
                    self.logger.info(f"Condition {condition_clean} evaluated to False. "
                                     f"Skipping the end of pipeline.")
                    # Set the current task as SKIPPED
                    task.status = TaskStatus.SKIPPED
                    task.data_in = task_files

                    # Update the task
                    self.session.add(task)
                    self.session.commit()
                    self.session.refresh(task)

                    # Send message to client
                    self.logger.debug(f"Sending task {task} to client")
                    message = create_message(task)
                    await self.send_message(message, pipeline_execution, task, general_status=TaskStatus.FINISHED)
                    # Set remaining tasks as SKIPPED
                    # TODO: Check if this is the right behavior
                    self.skip_remaining_tasks(pipeline_execution)

                    # End the pipeline execution
                    end_pipeline_execution(pipeline_execution)

                    should_post_task = False

            if should_post_task:
                # Update the task
                task.data_in = task_files
                task.service_id = next_service.id
                task.status = TaskStatus.PENDING
                self.session.add(task)

                # Create the service task
                service_task = ServiceTask(
                    s3_access_key_id=self.settings.s3_access_key_id,
                    s3_secret_access_key=self.settings.s3_secret_access_key,
                    s3_region=self.settings.s3_region,
                    s3_host=self.settings.s3_host,
                    s3_bucket=self.settings.s3_bucket,
                    task=task,
                    callback_url=f"{self.settings.host}/tasks/{task.id}"
                )

                # Submit the service task to the remote service
                try:
                    res = await self.http_client.post(
                        f"{next_service.url}/compute",
                        json=jsonable_encoder(service_task)
                    )

                    if res.status_code != 200:
                        raise HTTPException(status_code=res.status_code, detail=res.text)

                    self.logger.debug(f"Sending task {task} to client")
                    message = create_message(task)

                    await self.send_message(message, pipeline_execution, task)

                    self.logger.debug(f"Launched next step in pipeline with id {pipeline_execution.id}")

                except HTTPException as e:
                    self.logger.warning(f"Service {next_service.name} returned an error: {str(e)}")

                    # Set task to error
                    set_error_state(pipeline_execution, service_task.task.id)

                    # Skip all remaining tasks
                    self.skip_remaining_tasks(pipeline_execution)

                    # End the pipeline execution
                    end_pipeline_execution(pipeline_execution)

                    # Send message to client
                    self.logger.debug(f"Sending task {task} to client")
                    message = create_message(task)
                    await self.send_message(message, pipeline_execution, task, general_status=TaskStatus.ERROR)

                except HTTPError as e:
                    self.logger.error(f"Sending request to the service {next_service.name} failed: {str(e)}")

                    # Set task to error
                    set_error_state(pipeline_execution, service_task.task.id)

                    # Skip all remaining tasks
                    self.skip_remaining_tasks(pipeline_execution)

                    # End the pipeline execution
                    end_pipeline_execution(pipeline_execution)

                    # Send message to client
                    self.logger.debug(f"Sending task {task} to client")
                    message = create_message(task)
                    await self.send_message(message, pipeline_execution, task, general_status=TaskStatus.ERROR)

        self.session.add(pipeline_execution)
        self.session.commit()
        self.session.refresh(pipeline_execution)
        self.logger.debug(f"Pipeline execution updated with data: {pipeline_execution}")
        return pipeline_execution
