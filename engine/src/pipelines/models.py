from typing import List
from sqlmodel import Field, SQLModel, Relationship
from common.models import CoreModel
from uuid import UUID, uuid4
from pipeline_elements.models import PipelineElement


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
    tasks: List["Task"] = Relationship(back_populates="pipeline") # noqa F821


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
    tasks: "List[TaskRead]"


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


from tasks.models import Task, TaskRead # noqa E402
Pipeline.update_forward_refs()
PipelineReadWithPipelineElementAndTask.update_forward_refs(tasks=List[TaskRead])
