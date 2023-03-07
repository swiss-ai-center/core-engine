import re
from typing import List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from common.models import CoreModel
from uuid import UUID, uuid4
from pydantic.class_validators import validator
from .enums import PipelineElementType

if TYPE_CHECKING:
    from tasks.models import Task, TaskRead


class PipelineElementBase(CoreModel):
    """
    Base class for an element in a Pipeline
    This model is used in subclasses

    id: the pipeline element
    next: the next pipeline element
    """
    type: PipelineElementType = Field(default=PipelineElementType.SERVICE, nullable=False)
    slug: str = Field(nullable=False)
    pipeline_id: UUID | None = Field(default=None, nullable=True, foreign_key="pipeline.id")

    # Needed for a PipelineElementService
    service_id: UUID | None = Field(default=None, nullable=True, foreign_key="service.id")

    # Needed for a PipelineElementBranch
    condition: str | None = Field(default=None, nullable=True)
    then: str | None = Field(default=None, nullable=True)

    # Needed for a PipelineElementWait
    wait_on: List[str] | None = Field(default=None, nullable=True)

    @validator("slug")
    def slug_format(cls, v):
        if not re.match(r"[a-z\-]+", v):
            raise ValueError("Slug must be in kebab-case format. Example: my-service")
        return v


class PipelineElement(PipelineElementBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    next: UUID | None = Field(default=None, foreign_key="pipelineelement.id")


class PipelineBase(CoreModel):
    """
    Base class for Pipeline
    This model is used in subclasses
    """
    name: str = Field(nullable=False)
    summary: str = Field(nullable=False)
    description: str | None = Field(default=None, nullable=True)


class Pipeline(PipelineBase, table=True):
    """
    Pipeline model
    This model is the one that is stored in the database
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tasks: List["Task"] = Relationship(back_populates="pipeline")  # noqa F821


class PipelineRead(PipelineBase):
    """
    Pipeline read model
    This model is used to return a pipeline to the user
    """
    id: UUID


class PipelineReadWithPipelineElementAndTask(PipelineRead):
    """
    Pipeline read model with service
    This model is used to return a pipeline to the user with the service
    """
    pipeline_elements: List[PipelineElement]
    tasks: List["TaskRead"]


class PipelineCreate(PipelineBase):
    """
    Pipeline create model
    This model is used to create a pipeline
    """
    pipeline_elements: List[UUID]
    pass


class PipelineUpdate(SQLModel):
    """
    Pipeline update model
    This model is used to update a pipeline
    """
    name: str | None
    url: str | None
    summary: str | None
    description: str | None
