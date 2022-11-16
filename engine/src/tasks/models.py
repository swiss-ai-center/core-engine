from sqlmodel import Field
from .enums import TaskStatus
from common.models import CoreModel


class Task(CoreModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    status: TaskStatus


class TaskRead(CoreModel):
    id: int
    status: TaskStatus


class TaskCreate(CoreModel):
    status: TaskStatus
