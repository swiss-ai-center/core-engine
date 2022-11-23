from typing import List
from sqlmodel import Field, JSON, Column, SQLModel
from .enums import TaskStatus
from common.models import CoreModel
from uuid import UUID, uuid4


class TaskBase(CoreModel):
    """
    Base class for Task
    used in subclasses
    """
    # TODO: change service type to Service
    service: str = Field(nullable=False)
    url: str = Field(nullable=False)
    data_in: List[str] | None = Field(sa_column=Column(JSON), default=None, nullable=True)
    data_out: List[str] | None = Field(sa_column=Column(JSON), default=None, nullable=True)
    status: TaskStatus = Field(default=TaskStatus.PENDING, nullable=False)

    # Needed for Column(JSON) to work
    class Config:
        arbitrary_types_allowed = True


class Task(TaskBase, table=True):
    """
    Task model
    the one that is stored in the database
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)


class TaskRead(TaskBase):
    """
    Task read model
    This model is used to return a task to the user
    """
    id: UUID


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
    service: str | None
    url: str | None
    data_out: List[str] | None
    status: TaskStatus | None
