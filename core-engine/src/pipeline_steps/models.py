import re
from typing import List
from pydantic.class_validators import validator
from sqlmodel import Field, Relationship, Column, JSON
from common.models import CoreModel
from uuid import UUID, uuid4
from services.models import Service


class PipelineStepBase(CoreModel):
    """
    Base class for a step in a Pipeline
    This model is used in subclasses
    """
    identifier: str = Field(nullable=False)
    needs: List[str] | None = Field(sa_column=Column(JSON), default=None, nullable=True)
    condition: str | None = Field(default=None, nullable=True)
    inputs: List[str] = Field(sa_column=Column(JSON), nullable=False)

    @validator("identifier")
    def identifier_format(cls, v):
        if not re.match(r"[a-z\-]+", v):
            raise ValueError("Identifier must be in kebab-case format. Example: my-pipeline-step-identifier")
        return v

    class Config:
        arbitrary_types_allowed = True


class PipelineStep(
    PipelineStepBase,
    table=True,
):
    """
    Pipeline Step model
    This model is the one that is stored in the database
    """
    __tablename__ = "pipeline_steps"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pipeline_id: UUID | None = Field(foreign_key="pipelines.id")
    pipeline: "Pipeline" = Relationship(back_populates="steps") # noqa F821
    pipeline_executions: List["PipelineExecution"] = Relationship(
        back_populates="current_pipeline_step"
    )  # noqa F821
    service_id: UUID = Field(nullable=False, foreign_key="services.id")
    service: Service = Relationship(back_populates="pipeline_steps")


class PipelineStepRead(PipelineStepBase):
    """
    Pipeline Step read model
    This model is used to return a pipeline step to the user
    """
    id: UUID
    pipeline: "Pipeline"


class PipelineStepCreate(PipelineStepBase):
    """
    Pipeline Step create model
    This model is used to create a pipeline step
    """
    service_slug: str


class PipelineStepUpdate(PipelineStepBase):
    """
    Pipeline Step update model
    This model is used to update a pipeline step
    """
    service_slug: str


from pipelines.models import Pipeline  # noqa F401
from pipeline_executions.models import PipelineExecution  # noqa F401

PipelineStep.update_forward_refs(pipeline=Pipeline, pipeline_executions=PipelineExecution)
