from fastapi import Depends
from sqlmodel import Session, select, desc
from database import get_session
from common_code.logger.logger import Logger, get_logger
from uuid import UUID
from pipeline_elements.models import PipelineElement
from pipeline_executions.models import PipelineExecution, PipelineExecutionUpdate
from common.exceptions import NotFoundException, UnprocessableEntityException
from pipelines.models import Pipeline


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
        self.logger.debug("Find many pipeline executions")
        return self.session.exec(
            select(PipelineExecution)
            .order_by(desc(PipelineExecution.created_at))
            .offset(skip)
            .limit(limit)
        ).all()

    def create(self, pipeline_execution: PipelineExecution):
        self.logger.debug("Creating pipeline execution")

        self.session.add(pipeline_execution)
        self.session.commit()
        self.session.refresh(pipeline_execution)
        self.logger.debug(f"Created pipeline execution with id {pipeline_execution.id}")

        return pipeline_execution

    def find_one(self, pipeline_execution_id: UUID):
        self.logger.debug("Find pipeline execution")

        return self.session.get(PipelineExecution, pipeline_execution_id)

    def update(
        self,
        pipeline_execution_id: UUID,
        pipeline_execution: PipelineExecutionUpdate,
    ):
        self.logger.debug("Update pipeline execution")
        current_pipeline_execution = self.session.get(PipelineExecution, pipeline_execution_id)

        if not current_pipeline_execution:
            raise NotFoundException("Pipeline Element Not Found")

        # Check if the pipeline element is in the pipeline object
        current_pipeline_element = self.session.get(PipelineElement, pipeline_execution.pipeline_element)
        if current_pipeline_element is not None:
            pipeline = self.session.get(Pipeline, current_pipeline_element.pipeline_id)
            if not pipeline:
                raise NotFoundException("Associated Pipeline Not Found")
            if current_pipeline_element not in pipeline.pipeline_elements:
                raise UnprocessableEntityException("Pipeline element not part of the pipeline")

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
        self.logger.debug("Delete pipeline execution")
        pipeline_execution = self.session.get(PipelineExecution, pipeline_execution_id)
        if not pipeline_execution:
            raise NotFoundException("Pipeline Element Not Found")
        self.session.delete(pipeline_execution)
        self.session.commit()
        self.logger.debug(f"Deleted pipeline execution with id {pipeline_execution.id}")
