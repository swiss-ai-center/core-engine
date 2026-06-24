import re
from typing import List, Optional
from sqlmodel import Field, Relationship, Column, JSON
from common.models import CoreModel
from uuid import UUID, uuid4
from services.models import Service
from pydantic_settings import SettingsConfigDict
from pydantic import field_validator, model_validator


class PipelineStepBase(CoreModel):
    model_config = SettingsConfigDict(arbitrary_types_allowed=True)

    identifier: str
    needs: Optional[List[str]] = Field(sa_column=Column(JSON), default=None)
    condition: Optional[str] = None
    inputs: List[str] = Field(sa_column=Column(JSON))
    group_identifier: Optional[str] = None
    source_pipeline_slug: Optional[str] = None

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
    id: UUID
    pipeline: "Pipeline"


class PipelineStepCreate(PipelineStepBase):
    service_slug: Optional[str] = None
    pipeline_slug: Optional[str] = None

    @model_validator(mode="after")
    def exactly_one_unit(self):
        has_service = self.service_slug is not None
        has_pipeline = self.pipeline_slug is not None
        if has_service == has_pipeline:
            raise ValueError("Exactly one of service_slug or pipeline_slug must be set.")
        return self


class PipelineStepUpdate(PipelineStepBase):
    service_slug: Optional[str] = None
    pipeline_slug: Optional[str] = None

    @model_validator(mode="after")
    def exactly_one_unit(self):
        has_service = self.service_slug is not None
        has_pipeline = self.pipeline_slug is not None
        if has_service == has_pipeline:
            raise ValueError("Exactly one of service_slug or pipeline_slug must be set.")
        return self


from pipelines.models import Pipeline  # noqa E402
from pipeline_executions.models import PipelineExecution  # noqa E402

PipelineStep.model_rebuild()
