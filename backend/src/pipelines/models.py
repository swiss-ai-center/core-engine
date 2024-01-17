from typing import List
from uuid import UUID, uuid4
from pydantic import BaseModel
from sqlmodel import SQLModel, Relationship, Field, Column, JSON
from common_code.common.models import FieldDescription, ExecutionUnitTag
from common.models import CoreModel
from execution_units.enums import ExecutionUnitStatus
from pipeline_steps.models import PipelineStep, PipelineStepCreate
from pydantic_settings import SettingsConfigDict


class PipelineBase(CoreModel):
    """
    Base class for a Pipeline
    This model is used in subclasses
    """
    model_config = SettingsConfigDict(arbitrary_types_allowed=True)

    name: str = Field(nullable=False)
    slug: str = Field(nullable=False, unique=True)
    summary: str = Field(nullable=False)
    description: str | None = Field(default=None, nullable=True)
    status: ExecutionUnitStatus = Field(
        default=ExecutionUnitStatus.AVAILABLE, nullable=False
    )
    data_in_fields: List[FieldDescription] | None = Field(
        sa_column=Column(JSON), default=None
    )
    data_out_fields: List[FieldDescription] | None = Field(
        sa_column=Column(JSON), default=None
    )
    tags: List[ExecutionUnitTag] | None = Field(sa_column=Column(JSON), default=None)


class Pipeline(PipelineBase, table=True):
    """
    Pipeline model
    This model is the one that is stored in the database
    """
    __tablename__ = "pipelines"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pipeline_executions: List["PipelineExecution"] = Relationship(
        sa_relationship_kwargs={"cascade": "delete"},
        back_populates="pipeline"
    )  # noqa F821
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
    name: str | None = None
    summary: str | None = None
    description: str | None = None
    status: ExecutionUnitStatus | None = None
    steps: List[PipelineStepCreate] | None = None


class PipelinesWithCount(BaseModel):
    """
    Pipelines with count
    This model is used to return a list of filtered pipelines with the count of all pipelines matching a filter
    """
    count: int
    pipelines: List[PipelineRead]


from pipeline_executions.models import PipelineExecution  # noqa E402

Pipeline.model_rebuild()
