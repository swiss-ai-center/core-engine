from sqlmodel import Field, JSON, Column, SQLModel, Relationship
from common.models import CoreModel
from uuid import UUID, uuid4
from typing import List, Optional
from typing_extensions import TypedDict
from pydantic_settings import SettingsConfigDict


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
    model_config = SettingsConfigDict(arbitrary_types_allowed=True)

    pipeline_id: Optional[UUID] = Field(default=None, foreign_key="pipelines.id")
    current_pipeline_step_id: Optional[UUID] = Field(default=None, foreign_key="pipeline_steps.id")


class PipelineExecution(PipelineExecutionBase, table=True):
    """
    Pipeline Execution model
    This model is the one that is stored in the database
    """

    __tablename__ = "pipeline_executions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pipeline: "Pipeline" = Relationship(back_populates="pipeline_executions")
    current_pipeline_step: Optional["PipelineStep"] = Relationship(
        back_populates="pipeline_executions"
    )
    tasks: List["Task"] = Relationship(
        sa_relationship_kwargs={"cascade": "delete"},
        back_populates="pipeline_execution",
    )
    files: Optional[List[FileKeyReference]] = Field(sa_column=Column(JSON), default=None)


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
    tasks: List["TaskRead"]


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

    current_pipeline_step_id: Optional[UUID] = None
    tasks: Optional[List["Task"]] = None


from pipeline_steps.models import PipelineStep  # noqa E402
from pipelines.models import Pipeline  # noqa E402
from tasks.models import Task, TaskRead  # noqa E402

PipelineExecution.model_rebuild()
PipelineExecutionReadWithPipelineAndTasks.model_rebuild()
PipelineExecutionUpdate.model_rebuild()
