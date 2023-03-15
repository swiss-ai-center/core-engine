import re
from typing import List, TypedDict
from pydantic.class_validators import validator
from sqlmodel import Field, Relationship, Column, JSON
from common.models import CoreModel
from uuid import UUID, uuid4
from pipeline_elements.enums import PipelineElementType, InOutType
from pipelines.models import Pipeline


class DataInIdentifier(TypedDict):
    """
    Data in identifier
    """
    identifier: str
    in_or_out: InOutType
    field: str


class PipelineElementEntry(CoreModel):
    """
    Entry element in a pipeline
    """
    data_in_identifier: List[DataInIdentifier] | None = Field(sa_column=Column(JSON), default=None, nullable=True)
    data_out_identifier: List[DataInIdentifier] | None = Field(sa_column=Column(JSON), default=None, nullable=True)

    # Needed for Column(JSON) to work
    class Config:
        arbitrary_types_allowed = True


class PipelineElementService(CoreModel):
    """
    A service in a pipeline
    """
    service_id: UUID | None = Field(default=None, nullable=True, foreign_key="services.id")
    data_in_identifier: List[DataInIdentifier] | None = Field(sa_column=Column(JSON), default=None, nullable=True)
    data_out_identifier: List[DataInIdentifier] | None = Field(sa_column=Column(JSON), default=None, nullable=True)

    # Needed for Column(JSON) to work
    class Config:
        arbitrary_types_allowed = True


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

    @validator("identifier")
    def identifier_format(cls, v):
        if not re.match(r"[a-z\-]+", v):
            raise ValueError("Identifier must be in kebab-case format. Example: my-pipeline-element-identifier")
        return v


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
