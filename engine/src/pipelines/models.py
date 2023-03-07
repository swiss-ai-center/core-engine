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
    pipeline_id: UUID | None = Field(default=None, nullable=True, foreign_key="pipelines.id")

    @validator("slug")
    def slug_format(cls, v):
        if not re.match(r"[a-z\-]+", v):
            raise ValueError("Slug must be in kebab-case format. Example: my-service")
        return v


class PipelineElementService(PipelineElementBase):
    """
    A service in a pipeline
    """
    service_id: UUID | None = Field(default=None, nullable=True, foreign_key="services.id")


class PipelineElementBranch(PipelineElementBase):
    """
    A branch in a pipeline
    """
    condition: str | None = Field(default=None, nullable=True)
    then: str | None = Field(default=None, nullable=True)


class PipelineElementWait(PipelineElementBase):
    """
    A wait in a pipeline
    """
    wait_on: List[str] | None = Field(default=None, nullable=True)


class PipelineElement(
    PipelineElementService,
    PipelineElementBranch,
    PipelineElementWait,
    table=True,
):
    __tablename__ = "pipeline_elements"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    next: UUID | None = Field(default=None, foreign_key="pipeline_elements.id")


class PipelineElementServiceRead(PipelineElementService):
    id: UUID
    next: UUID | None


class PipelineElementBranchRead(PipelineElementBranch):
    id: UUID
    next: UUID | None


class PipelineElementWaitRead(PipelineElementWait):
    id: UUID
    next: UUID | None


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
    __tablename__ = "pipelines"

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
    pass
    pipeline_elements: List[PipelineElement]
    tasks: List["TaskRead"]


class PipelineCreate(PipelineBase):
    """
    Pipeline create model
    This model is used to create a pipeline
    """
    pipeline_elements: List[UUID]


class PipelineUpdate(SQLModel):
    """
    Pipeline update model
    This model is used to update a pipeline
    """
    name: str | None
    url: str | None
    summary: str | None
    description: str | None
