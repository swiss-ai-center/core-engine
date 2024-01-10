from sqlmodel import Field, JSON, Column, SQLModel, Relationship
from common.models import CoreModel
from uuid import UUID, uuid4
from tasks.models import Task, TaskRead
from typing import List, Union
from typing_extensions import TypedDict


class FileKeyReference(TypedDict):
    """
    File key reference model
    """

    reference: str
    file_key: str


class PipelineExecutionBase(CoreModel):
    """
    Base class for a Pipeline Execution
    This model is used in subclasses
    """

    pipeline_id: UUID | None = Field(
        default=None, nullable=True, foreign_key="pipelines.id"
    )
    current_pipeline_step_id: UUID | None = Field(
        default=None, nullable=True, foreign_key="pipeline_steps.id"
    )

    # Needed for Column(JSON) to work
    class Config:
        arbitrary_types_allowed = True


class PipelineExecution(PipelineExecutionBase, table=True):
    """
    Pipeline Execution model
    This model is the one that is stored in the database
    """

    __tablename__ = "pipeline_executions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pipeline: "Pipeline" = Relationship(back_populates="pipeline_executions")
    current_pipeline_step: Union["PipelineStep", None] = Relationship(
        back_populates="pipeline_executions"
    )
    tasks: List[Task] = Relationship(
        sa_relationship_kwargs={"cascade": "delete"},
        back_populates="pipeline_execution",
    )
    files: List[FileKeyReference] | None = Field(sa_column=Column(JSON), default=None)


class PipelineExecutionRead(PipelineExecutionBase):
    """
    Pipeline Execution read model
    This model is used to return a pipeline execution to the user
    """

    id: UUID


class PipelineExecutionReadWithPipelineAndTasks(PipelineExecutionRead):
    """
    Pipeline Execution read model with pipeline and tasks
    This model is used to return a pipeline execution to the user
    """

    pipeline: "Pipeline"
    tasks: List[TaskRead]


class PipelineExecutionCreate(PipelineExecutionBase):
    """
    Pipeline Execution create model
    This model is used to create a pipeline execution
    """

    pass


class PipelineExecutionUpdate(SQLModel):
    """
    Pipeline Execution update model
    This model is used to update a pipeline execution
    """

    current_pipeline_step_id: UUID | None
    tasks: List[Task] | None


from pipeline_steps.models import PipelineStep  # noqa F401
from pipelines.models import Pipeline  # noqa F401

PipelineExecution.update_forward_refs()
PipelineExecutionReadWithPipelineAndTasks.update_forward_refs()
