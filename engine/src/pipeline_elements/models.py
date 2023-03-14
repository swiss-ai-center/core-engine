import re
from typing import List
from sqlmodel import Field
from common.models import CoreModel
from uuid import UUID, uuid4
from pydantic.class_validators import validator
from pipeline_elements.enums import PipelineElementType


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
