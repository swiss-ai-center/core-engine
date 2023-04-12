from typing import List
from uuid import UUID
from sqlmodel import SQLModel, Relationship, Field
from execution_units.models import ExecutionUnit
from execution_units.enums import ExecutionUnitStatus, ExecutionUnitType
from pipeline_steps.models import PipelineStep, PipelineStepCreate


class Pipeline(ExecutionUnit):
    """
    Pipeline model
    This model is the one that is stored in the database
    """
    __tablename__ = "pipelines"

    id: UUID = Field(foreign_key="execution_units.id", primary_key=True)
    pipeline_executions: List["PipelineExecution"] = Relationship(back_populates="pipeline")  # noqa F821
    steps: List[PipelineStep] = Relationship(back_populates="pipeline")  # noqa F821

    __mapper_args__ = {
        "polymorphic_identity": ExecutionUnitType.PIPELINE
    }


class PipelineRead(Pipeline):
    """
    Pipeline read model
    This model is used to return a pipeline to the user
    """
    id: UUID


class PipelineReadWithPipelineStepsAndTasks(PipelineRead):
    """
    Pipeline read model with service
    This model is used to return a pipeline to the user with the service
    """
    steps: List[PipelineStep]


class PipelineCreate(Pipeline):
    """
    Pipeline create model
    This model is used to create a pipeline
    """
    steps: List[PipelineStepCreate]


class PipelineUpdate(SQLModel):
    """
    Pipeline update model
    This model is used to update a pipeline
    """
    name: str | None
    summary: str | None
    description: str | None
    status: ExecutionUnitStatus | None
    steps: List[PipelineStepCreate] | None


from pipeline_executions.models import PipelineExecution  # noqa E402

Pipeline.update_forward_refs()
