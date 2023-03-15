from typing import List
from sqlmodel import Field, Relationship, SQLModel
from common.models import CoreModel
from uuid import UUID, uuid4
from pipeline_elements.models import PipelineElement
from pipeline_executions.enums import PipelineExecutionStatus
from pipelines.models import Pipeline


class PipelineExecutionBase(CoreModel):
    """
    Base class for a Pipeline Execution
    This model is used in subclasses
    """
    status: PipelineExecutionStatus = Field(nullable=False)
    pipeline_id: UUID | None = Field(default=None, nullable=True, foreign_key="pipelines.id")
    current_pipeline_element_id: UUID | None = Field(default=None, nullable=True, foreign_key="pipeline_elements.id")


class PipelineExecution(PipelineExecutionBase, table=True):
    __tablename__ = "pipeline_executions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pipeline: Pipeline = Relationship(back_populates="pipeline_executions")
    current_pipeline_element: PipelineElement = Relationship(back_populates="pipeline_executions")
    tasks: List["Task"] = Relationship(back_populates="pipeline_execution")


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
    pipeline: Pipeline
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
    status: PipelineExecutionStatus | None
    current_pipeline_element_id: UUID | None
    tasks: List["Task"] | None


from tasks.models import Task, TaskRead # noqa F401
PipelineExecution.update_forward_refs()
PipelineExecutionReadWithPipelineAndTasks.update_forward_refs(tasks=List[TaskRead])
PipelineExecutionUpdate.update_forward_refs(tasks=List[Task])
