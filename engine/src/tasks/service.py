from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session, select, desc
from database import get_session
from common_code.logger.logger import Logger, get_logger
from uuid import UUID
from http_client import HttpClient
from tasks.models import Task, TaskUpdate, TaskStatus
from common.exceptions import NotFoundException
from pipeline_executions.service import PipelineExecutionsService
from pipeline_executions.models import PipelineExecution, FileKeyReference
from pipeline_steps.models import PipelineStep
from pipelines.models import Pipeline
from services.models import Service, ServiceTask
from config import Settings, get_settings
from httpx import HTTPError


class TasksService:
    def __init__(
            self,
            logger: Logger = Depends(get_logger),
            session: Session = Depends(get_session),
            http_client: HttpClient = Depends(),
            pipeline_executions_service: PipelineExecutionsService = Depends(),
            settings: Settings = Depends(get_settings),
    ):
        self.logger = logger
        self.logger.set_source(__name__)
        self.session = session
        self.http_client = http_client
        self.pipeline_executions_service = pipeline_executions_service
        self.settings = settings

    def find_many(self, skip: int = 0, limit: int = 100, order_by: str = "name", order: str = "desc"):
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
        self.logger.debug(f"Got status {status} from service {task.service.url}")
        task.status = status

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task

    def update(self, task_id: UUID, task: TaskUpdate):
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
        task_data = task.dict(exclude_unset=True)
        self.logger.debug(f"Updating task {task_id} with data: {task_data}")

        for key, value in task_data.items():
            setattr(current_task, key, value)

        self.session.add(current_task)
        self.session.commit()
        self.session.refresh(current_task)
        self.logger.debug(f"Updated task with id {current_task.id}")
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

    def end_pipeline_execution(self, pipeline_execution: PipelineExecution):
        """
        End the pipeline execution
        :param pipeline_execution: The pipeline execution to end
        """
        pipeline_execution.current_pipeline_step_id = None
        pipeline_execution.files = None

    def set_error_state(self, pipeline_execution: PipelineExecution, task_id: UUID):
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

    def skip_remaining_tasks(self, pipeline_execution: PipelineExecution):
        """
        Skip remaining tasks in the pipeline execution
        :param pipeline_execution: The pipeline execution to skip remaining tasks for
        """
        for task in pipeline_execution.tasks:
            if task.status != TaskStatus.ERROR:
                task.status = TaskStatus.SKIPPED

    async def launch_next_step_in_pipeline(self, task: Task):
        """
        Launch the next step in the pipeline
        :param task: The task that has been completed
        """

        # TODO: Manage conditions and skipping if condition is not met
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
        if current_pipeline_step == pipeline.steps[-1]:
            self.end_pipeline_execution(pipeline_execution)
        else:
            next_pipeline_step_id = pipeline.steps[pipeline.steps.index(current_pipeline_step) + 1].id

            # Get the next pipeline step
            next_pipeline_step = self.session.get(PipelineStep, next_pipeline_step_id)
            pipeline_execution.current_pipeline_step_id = next_pipeline_step_id

            # Get the next pipeline service
            next_service = self.session.get(Service, next_pipeline_step.service_id)

            # Get the task of the next pipeline step
            query = self.session.query(Task).join(PipelineExecution).join(Service).where(
                (Task.pipeline_execution_id == pipeline_execution.id) & (
                        PipelineExecution.id == pipeline_execution.id) & (
                        Service.id == next_pipeline_step.service_id)
            )
            task = query.first()

            # Get the files for the next pipeline step
            task_files = []
            for file_input in next_pipeline_step.inputs:
                for file in pipeline_execution.files:
                    if file["reference"] == file_input:
                        task_files.append(file["file_key"])
                        break

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
                res = await self.http_client.post(f"{next_service.url}/compute", json=jsonable_encoder(service_task))

                if res.status_code != 200:
                    raise HTTPException(status_code=res.status_code, detail=res.text)

                self.logger.debug(f"Launched next step in pipeline with id {pipeline_execution.id}")

            except HTTPException as e:
                self.logger.warning(f"Service {next_service.name} returned an error: {str(e)}")

                # Set task to error
                self.set_error_state(pipeline_execution, service_task.task.id)

                # Skip all remaining tasks
                self.skip_remaining_tasks(pipeline_execution)

                # End the pipeline execution
                self.end_pipeline_execution(pipeline_execution)

            except HTTPError as e:
                self.logger.error(f"Sending request to the service {next_service.name} failed: {str(e)}")

                # Set task to error
                self.set_error_state(pipeline_execution, service_task.task.id)

                # Skip all remaining tasks
                self.skip_remaining_tasks(pipeline_execution)

                # End the pipeline execution
                self.end_pipeline_execution(pipeline_execution)

        self.session.add(pipeline_execution)
        self.session.commit()
        self.session.refresh(pipeline_execution)
        self.logger.debug(f"Pipeline execution updated with data: {pipeline_execution}")
        return pipeline_execution
