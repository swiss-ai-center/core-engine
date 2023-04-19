from fastapi import Depends
from sqlmodel import Session, select, desc
from database import get_session
from common_code.logger.logger import Logger, get_logger
from uuid import UUID
from pipeline_steps.models import PipelineStep
from pipeline_executions.models import PipelineExecution, PipelineExecutionUpdate, FileKeyReference
from common.exceptions import NotFoundException, UnprocessableEntityException
from pipelines.models import Pipeline
from tasks.models import Task
from services.models import Service


class PipelineExecutionsService:
    def __init__(
        self,
        logger: Logger = Depends(get_logger),
        session: Session = Depends(get_session),
    ):
        self.logger = logger
        self.logger.set_source(__name__)
        self.session = session

    def find_many(self, skip: int = 0, limit: int = 100):
        """
        Find many pipeline executions
        :param skip: number of pipeline executions to skip
        :param limit: number of pipeline executions to return
        :return: list of pipeline executions
        """
        self.logger.debug("Find many pipeline executions")
        return self.session.exec(
            select(PipelineExecution)
            .order_by(desc(PipelineExecution.created_at))
            .offset(skip)
            .limit(limit)
        ).all()

    def find_one(self, pipeline_execution_id: UUID):
        """
        Find one pipeline execution
        :param pipeline_execution_id: id of pipeline execution to find
        :return: pipeline execution
        """
        self.logger.debug("Find pipeline execution")

        return self.session.get(PipelineExecution, pipeline_execution_id)

    def create(self, pipeline_execution: PipelineExecution):
        """
        Create a pipeline execution
        :param pipeline_execution: pipeline execution to create
        :return: created pipeline execution
        """
        self.logger.debug("Creating pipeline execution")

        self.session.add(pipeline_execution)
        self.session.commit()
        self.session.refresh(pipeline_execution)
        self.logger.debug(f"Created pipeline execution with id {pipeline_execution.id}")

        return pipeline_execution

    def update(
        self,
        pipeline_execution_id: UUID,
        pipeline_execution: PipelineExecutionUpdate,
    ):
        """
        Update a pipeline execution
        :param pipeline_execution_id: id of pipeline execution to update
        :param pipeline_execution: pipeline execution to update
        :return: updated pipeline execution
        """
        self.logger.debug("Update pipeline execution")
        current_pipeline_execution = self.session.get(PipelineExecution, pipeline_execution_id)

        if not current_pipeline_execution:
            raise NotFoundException("Pipeline Step Not Found")

        # Check if the pipeline step is in the pipeline object
        current_pipeline_step = self.session.get(PipelineStep, pipeline_execution.current_pipeline_step_id)
        if current_pipeline_step is not None:
            pipeline = self.session.get(Pipeline, current_pipeline_step.pipeline_id)
            if not pipeline:
                raise NotFoundException("Associated Pipeline Not Found")
            if current_pipeline_step not in pipeline.steps:
                raise UnprocessableEntityException("Pipeline step not part of the pipeline")

        pipeline_execution_data = pipeline_execution.dict(exclude_unset=True)
        self.logger.debug(f"Updating pipeline execution {pipeline_execution_id} with data: {pipeline_execution_data}")
        for key, value in pipeline_execution_data.items():
            setattr(current_pipeline_execution, key, value)
        self.session.add(current_pipeline_execution)
        self.session.commit()
        self.session.refresh(current_pipeline_execution)
        self.logger.debug(f"Updated pipeline execution with id {current_pipeline_execution.id}")
        return current_pipeline_execution

    def delete(self, pipeline_execution_id: UUID):
        """
        Delete a pipeline execution
        :param pipeline_execution_id: id of pipeline execution to delete
        """
        self.logger.debug("Delete pipeline execution")
        pipeline_execution = self.session.get(PipelineExecution, pipeline_execution_id)
        if not pipeline_execution:
            raise NotFoundException("Pipeline Step Not Found")
        self.session.delete(pipeline_execution)
        self.session.commit()
        self.logger.debug(f"Deleted pipeline execution with id {pipeline_execution.id}")

    def launch_next_step_in_pipeline(self, task: Task):
        """
        Launch the next step in the pipeline
        :param task: last finished task from current pipeline step
        """
        self.logger.debug("Launch next step in pipeline")
        
        pipeline_execution = self.session.get(PipelineExecution, task.pipeline_execution_id)
        
        # Check if pipeline execution exists
        if not pipeline_execution:
            raise NotFoundException("Pipeline Execution Not Found")
        
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
            files = []
            for file in task.data_out:
                # TODO: handle file key reference
                reference = f"{current_pipeline_step.identifier}."
                files.append(FileKeyReference(reference=reference, key=file))
            pipeline_execution.files.extend(files)
        
        # Check if current pipeline step is the last one
        if current_pipeline_step == pipeline.steps[-1]:
            # TODO: handle end of pipeline
            pass
        else:
            pipeline_execution.current_pipeline_step_id = pipeline.steps[
                pipeline.steps.index(current_pipeline_step) + 1
            ].id
            
        self.session.add(pipeline_execution)
        self.session.commit()
        self.session.refresh(pipeline_execution)
        self.logger.debug(f"Launched next step in pipeline with id {pipeline_execution.id}")
        return pipeline_execution