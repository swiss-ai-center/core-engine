from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, field_validator, field_serializer
from sqlmodel import SQLModel, Relationship, Field, Column
from common_code.common.models import FieldDescription, ExecutionUnitTag
from common.models import CoreModel, PydanticJSON
from execution_units.enums import ExecutionUnitStatus
from pipeline_steps.models import PipelineStep, PipelineStepCreate
from pydantic_settings import SettingsConfigDict


class PipelineBase(CoreModel):
    """
    Base class for a Pipeline
    This model is used in subclasses
    """
    model_config = SettingsConfigDict(arbitrary_types_allowed=True)

    name: str
    slug: str = Field(unique=True)
    summary: str
    description: Optional[str] = None
    status: ExecutionUnitStatus = ExecutionUnitStatus.AVAILABLE
    data_in_fields: Optional[List[FieldDescription]] = Field(sa_column=Column(PydanticJSON), default=None)
    data_out_fields: Optional[List[FieldDescription]] = Field(sa_column=Column(PydanticJSON), default=None)
    tags: Optional[List[ExecutionUnitTag]] = Field(sa_column=Column(PydanticJSON), default=None)

    @field_validator('data_in_fields', 'data_out_fields', mode='before')
    @classmethod
    def validate_field_descriptions(cls, v):
        if v is None:
            return v
        return [FieldDescription(**item) if isinstance(item, dict) else item for item in v]

    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        if v is None:
            return v
        return [ExecutionUnitTag(**item) if isinstance(item, dict) else item for item in v]

    @field_serializer('data_in_fields', 'data_out_fields', when_used='json')
    def serialize_field_descriptions(self, v):
        if v is None:
            return v
        return [item.model_dump(mode='json') if hasattr(item, 'model_dump') else item for item in v]

    @field_serializer('tags', when_used='json')
    def serialize_tags(self, v):
        if v is None:
            return v
        return [item.model_dump(mode='json') if hasattr(item, 'model_dump') else item for item in v]


class Pipeline(PipelineBase, table=True):
    """
    Pipeline model
    This model is the one that is stored in the database
    """
    __tablename__ = "pipelines"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pipeline_executions: List["PipelineExecution"] = Relationship(
        sa_relationship_kwargs={"cascade": "delete, save-update"},
        back_populates="pipeline"
    )  # noqa F821
    steps: List[PipelineStep] = Relationship(
        sa_relationship_kwargs={"cascade": "delete, save-update, delete-orphan"},
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
    name: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ExecutionUnitStatus] = None
    steps: Optional[List[PipelineStepCreate]] = None


class PipelinesWithCount(BaseModel):
    """
    Pipelines with count
    This model is used to return a list of filtered pipelines with the count of all pipelines matching a filter
    """
    count: int
    pipelines: List[PipelineRead]


from pipeline_executions.models import PipelineExecution  # noqa E402

Pipeline.model_rebuild()
