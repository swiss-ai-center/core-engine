from typing import List, Optional
from sqlmodel import Field, JSON, Column, SQLModel, Relationship
from tasks.enums import TaskStatus
from common.models import CoreModel
from uuid import UUID, uuid4
from services.models import Service
from pydantic_settings import SettingsConfigDict


class TaskBase(CoreModel):
    """
    Base class for Task
    This model is used in subclasses
    """
    model_config = SettingsConfigDict(arbitrary_types_allowed=True)

    data_in: Optional[List[str]] = Field(sa_column=Column(JSON), default=None)
    data_out: Optional[List[str]] = Field(sa_column=Column(JSON), default=None)
    status: TaskStatus = TaskStatus.PENDING
    service_id: UUID = Field(foreign_key="services.id")
    pipeline_execution_id: Optional[UUID] = Field(default=None, foreign_key="pipeline_executions.id")


class Task(TaskBase, table=True):
    """
    Task model
    This model is the one that is stored in the database
    """

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    service: Service = Relationship(back_populates="tasks")
    pipeline_execution: Optional["PipelineExecution"] = Relationship(back_populates="tasks")


class TaskRead(TaskBase):
    """
    Task read model
    This model is used to return a task to the user
    """

    id: UUID


class TaskReadWithServiceAndPipeline(TaskRead):
    """
    Task read model with service
    This model is used to return a task to the user with the service
    """

    service: Service
    pipeline_execution: Optional["PipelineExecution"]


class TaskCreate(TaskBase):
    """
    Task create model
    This model is used to create a task
    """

    pass


class TaskUpdate(SQLModel):
    """
    Task update model
    This model is used to update a task
    """

    data_out: List[str]
    status: Optional[TaskStatus]


from pipeline_executions.models import PipelineExecution  # noqa: E402

Task.model_rebuild()
TaskReadWithServiceAndPipeline.model_rebuild()
