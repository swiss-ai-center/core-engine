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

    @validator("slug")
    def slug_format(cls, v):
        if not re.match(r"[a-z\-]+", v):
            raise ValueError("Slug must be in kebab-case format. Example: my-service")
        return v


class PipelineElement(PipelineElementBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    next: UUID | None = Field(default=None, foreign_key="pipelineelement.id")


class PipelineElementService(PipelineElement, table=True):
    """
    This pipeline element is a service

    node_type: the type of the pipeline element
    service: the service
    """
    service_id: UUID = Field(nullable=False, foreign_key="service.id")

    @validator("type")
    def slug_format(cls, v):
        if v != PipelineElementType.SERVICE:
            raise ValueError("Type must be a service")
        return v


class PipelineElementBranch(PipelineElement, table=True):
    """
    This pipeline element is a branch

    node_type: the type of the pipeline element
    condition: the condition to check
    then: the next pipeline element if the condition is true
    """
    condition: str
    then: str

    @validator("type")
    def slug_format(cls, v):
        if v != PipelineElementType.BRANCH:
            raise ValueError("Type must be a branch")
        return v


class PipelineElementWait(PipelineElement, table=True):
    """
    This pipeline element is a wait

    node_type: the type of the pipeline element
    wait_on: the list of pipeline elements to wait on
    """
    wait_on: List[str]

    @validator("type")
    def slug_format(cls, v):
        if v != PipelineElementType.WAIT:
            raise ValueError("Type must be a wait")
        return v


class PipelineElementWaitRead(PipelineElementWait):
    """
    This pipeline element is a wait to keep trace of the execution of the pipeline

    finished: the list of pipeline elements that are finished
    """
    finished: List[str]


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
