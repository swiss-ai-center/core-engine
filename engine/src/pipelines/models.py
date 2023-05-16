from typing import List
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Relationship, Field
from execution_units.models import ExecutionUnitBase
from execution_units.enums import ExecutionUnitStatus
from pipeline_steps.models import PipelineStep, PipelineStepCreate


class PipelineBase(ExecutionUnitBase):
    """
    Base class for a Pipeline
    This model is used in subclasses
    """
    pass


class Pipeline(PipelineBase, table=True):
    """
    Pipeline model
    This model is the one that is stored in the database
    """
    __tablename__ = "pipelines"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pipeline_executions: List["PipelineExecution"] = Relationship(back_populates="pipeline")  # noqa F821
    steps: List[PipelineStep] = Relationship(
        sa_relationship_kwargs={"cascade": "delete"},
        back_populates="pipeline"
    )  # noqa F821


class PipelineRead(PipelineBase):
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


class PipelineCreate(PipelineBase):
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
