from typing import List
from sqlmodel import Field, SQLModel, Relationship, Column, JSON
from common.models import CoreModel
from uuid import UUID, uuid4
from common_code.common.models import FieldDescription
from pipelines.enums import PipelineStatus


class PipelineBase(CoreModel):
    """
    Base class for Pipeline
    This model is used in subclasses
    """
    name: str = Field(nullable=False)
    slug: str = Field(nullable=False, unique=True)
    summary: str = Field(nullable=False)
    description: str | None = Field(default=None, nullable=True)
    status: PipelineStatus = Field(default=PipelineStatus.AVAILABLE, nullable=False)
    data_in_fields: List[FieldDescription] | None = Field(sa_column=Column(JSON), default=None, nullable=True)
    data_out_fields: List[FieldDescription] | None = Field(sa_column=Column(JSON), default=None, nullable=True)

    # Needed for Column(JSON) to work
    class Config:
        arbitrary_types_allowed = True


class Pipeline(PipelineBase, table=True):
    """
    Pipeline model
    This model is the one that is stored in the database
    """
    __tablename__ = "pipelines"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pipeline_elements: List["PipelineElement"] = Relationship(back_populates="pipeline") # noqa F821
    pipeline_executions: List["PipelineExecution"] = Relationship(back_populates="pipeline") # noqa F821


class PipelineRead(PipelineBase):
    """
    Pipeline read model
    This model is used to return a pipeline to the user
    """
    id: UUID


class PipelineReadWithPipelineElementsAndTasks(PipelineRead):
    """
    Pipeline read model with service
    This model is used to return a pipeline to the user with the service
    """
    pipeline_elements: "List[PipelineElement]"


class PipelineCreate(PipelineBase):
    """
    Pipeline create model
    This model is used to create a pipeline
    """
    pipeline_elements: "List[PipelineElementCreate]"


class PipelineUpdate(SQLModel):
    """
    Pipeline update model
    This model is used to update a pipeline
    """
    name: str | None
    summary: str | None
    description: str | None
    status: PipelineStatus | None


from pipeline_elements.models import PipelineElement, PipelineElementCreate # noqa E402
Pipeline.update_forward_refs()
PipelineBase.update_forward_refs()
PipelineCreate.update_forward_refs(pipeline_elements=List[PipelineElementCreate])
PipelineReadWithPipelineElementsAndTasks.update_forward_refs(pipeline_elements=List[PipelineElement])
