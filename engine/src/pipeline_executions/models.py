from typing import List
from sqlmodel import Field, Relationship, SQLModel
from common.models import CoreModel
from uuid import UUID, uuid4
from tasks.models import Task, TaskRead


class PipelineExecutionBase(CoreModel):
    """
    Base class for a Pipeline Execution
    This model is used in subclasses
    """
    pipeline_id: UUID | None = Field(default=None, nullable=True, foreign_key="pipelines.id")
    current_pipeline_step_id: UUID | None = Field(default=None, nullable=True, foreign_key="pipeline_steps.id")


class PipelineExecution(PipelineExecutionBase, table=True):
    """
    Pipeline Execution model
    This model is the one that is stored in the database
    """
    __tablename__ = "pipeline_executions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pipeline: "Pipeline" = Relationship(back_populates="pipeline_executions")
    current_pipeline_step: "PipelineStep" = Relationship(back_populates="pipeline_executions")
    tasks: List[Task] = Relationship(back_populates="pipeline_execution")


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


from pipeline_steps.models import PipelineStep # noqa F401
from pipelines.models import Pipeline # noqa F401

PipelineExecution.update_forward_refs()
PipelineExecutionReadWithPipelineAndTasks.update_forward_refs(pipeline=Pipeline)
