from typing import List, Union
from sqlmodel import Field, JSON, Column, SQLModel, Relationship
from tasks.enums import TaskStatus
from common.models import CoreModel
from uuid import UUID, uuid4
from services.models import Service


class TaskBase(CoreModel):
    """
    Base class for Task
    This model is used in subclasses
    """

    data_in: List[str] | None = Field(sa_column=Column(JSON), default=None)
    data_out: List[str] | None = Field(sa_column=Column(JSON), default=None)
    status: TaskStatus = Field(default=TaskStatus.PENDING, nullable=False)
    service_id: UUID = Field(nullable=False, foreign_key="services.id")
    pipeline_execution_id: UUID | None = Field(
        default=None, nullable=True, foreign_key="pipeline_executions.id"
    )

    # Needed for Column(JSON) to work
    class Config:
        arbitrary_types_allowed = True


class Task(TaskBase, table=True):
    """
    Task model
    This model is the one that is stored in the database
    """

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    service: Service = Relationship(back_populates="tasks")
    pipeline_execution: Union["PipelineExecution", None] = Relationship(
        back_populates="tasks"
    )


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
    pipeline_execution: Union["PipelineExecution", None]


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
    status: TaskStatus | None


from pipeline_executions.models import PipelineExecution  # noqa: E402

Task.update_forward_refs()
TaskReadWithServiceAndPipeline.update_forward_refs()
