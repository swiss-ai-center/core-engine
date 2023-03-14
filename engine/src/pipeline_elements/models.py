import re
from typing import List
from sqlmodel import Field, Relationship
from common.models import CoreModel
from uuid import UUID, uuid4
from pydantic.class_validators import validator
from pipeline_elements.enums import PipelineElementType
from pipelines.models import Pipeline


class PipelineElementService(CoreModel):
    """
    A service in a pipeline
    """
    service_id: UUID | None = Field(default=None, nullable=True, foreign_key="services.id")


class PipelineElementBranch(CoreModel):
    """
    A branch in a pipeline
    """
    condition: str | None = Field(default=None, nullable=True)
    then: str | None = Field(default=None, nullable=True)


class PipelineElementWait(CoreModel):
    """
    A wait in a pipeline
    """
    wait_on: List[str] | None = Field(default=None, nullable=True)
    finished: List[str] | None = Field(default=None, nullable=True)


class PipelineElementBase(
    PipelineElementService,
    PipelineElementBranch,
    PipelineElementWait,
):
    """
    Base class for an element in a Pipeline
    This model is used in subclasses
    """
    type: PipelineElementType = Field(nullable=False)
    slug: str = Field(nullable=False)

    @validator("slug")
    def slug_format(cls, v):
        if not re.match(r"[a-z\-]+", v):
            raise ValueError("Slug must be in kebab-case format. Example: my-service")
        return v


class PipelineElement(
    PipelineElementBase,
    table=True,
):
    __tablename__ = "pipeline_elements"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pipeline_id: UUID | None = Field(default=None, nullable=True, foreign_key="pipelines.id")
    pipeline: Pipeline = Relationship(back_populates="pipeline_elements")
    next: UUID | None = Field(default=None, foreign_key="pipeline_elements.id")


class PipelineElementRead(PipelineElementBase):
    id: UUID
    next: UUID | None


class PipelineElementCreate(PipelineElementBase):
    pass


class PipelineElementUpdate(PipelineElementBase):
    next: UUID | None
