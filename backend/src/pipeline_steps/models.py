import re
from typing import List, Optional
from sqlmodel import Field, Relationship, Column, JSON
from common.models import CoreModel
from uuid import UUID, uuid4
from services.models import Service
from pydantic_settings import SettingsConfigDict
from pydantic import field_validator


class PipelineStepBase(CoreModel):
    """
    Base class for a step in a Pipeline
    This model is used in subclasses
    """
    model_config = SettingsConfigDict(arbitrary_types_allowed=True)

    identifier: str
    needs: Optional[List[str]] = Field(sa_column=Column(JSON), default=None)
    condition: Optional[str] = None
    inputs: List[str] = Field(sa_column=Column(JSON))

    @field_validator("identifier")
    def identifier_format(cls, v):
        if not re.match(r"[a-z\-]+", v):
            raise ValueError(
                "Identifier must be in kebab-case format. Example: my-pipeline-step-identifier"
            )
        return v


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
    pipeline_id: Optional[UUID] = Field(foreign_key="pipelines.id")
    pipeline: "Pipeline" = Relationship(back_populates="steps")  # noqa F821
    pipeline_executions: List["PipelineExecution"] = Relationship(
        sa_relationship_kwargs={"cascade": "delete"},
        back_populates="current_pipeline_step",
    )  # noqa F821
    service_id: Optional[UUID] = Field(foreign_key="services.id")
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


from pipelines.models import Pipeline  # noqa E402
from pipeline_executions.models import PipelineExecution  # noqa E402

PipelineStep.model_rebuild()
