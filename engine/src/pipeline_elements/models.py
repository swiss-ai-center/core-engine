from typing import List
from sqlmodel import Field, Relationship
from common.models import CoreModel
from uuid import UUID, uuid4
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
    otherwise: str | None = Field(default=None, nullable=True)


class PipelineElementBase(
    PipelineElementService,
    PipelineElementBranch,
):
    """
    Base class for an element in a Pipeline
    This model is used in subclasses
    """
    type: PipelineElementType = Field(nullable=False)
    identifier: str = Field(nullable=False)


class PipelineElement(
    PipelineElementBase,
    table=True,
):
    """
    Pipeline Element model
    This model is the one that is stored in the database
    """
    __tablename__ = "pipeline_elements"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pipeline_id: UUID | None = Field(default=None, nullable=True, foreign_key="pipelines.id")
    pipeline: Pipeline = Relationship(back_populates="pipeline_elements")
    pipeline_executions: List["PipelineExecution"] = Relationship(
        back_populates="current_pipeline_element")  # noqa F821


class PipelineElementRead(PipelineElementBase):
    """
    Pipeline Element read model
    This model is used to return a pipeline element to the user
    """
    id: UUID


class PipelineElementCreate(PipelineElementBase):
    """
    Pipeline Element create model
    This model is used to create a pipeline element
    """
    pass


class PipelineElementUpdate(PipelineElementBase):
    """
    Pipeline Element update model
    This model is used to update a pipeline element
    """
    pass


from pipeline_executions.models import PipelineExecution # noqa F401
PipelineElement.update_forward_refs(pipeline_executions=List[PipelineExecution])
