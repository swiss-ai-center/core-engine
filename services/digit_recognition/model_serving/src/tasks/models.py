from typing import List
from pydantic.main import BaseModel
from .enums import TaskStatus
from uuid import UUID


class TaskBase(BaseModel):
    """
    Task model
    """
    data_in: List[str] | None
    data_out: List[str] | None
    status: TaskStatus | None
    service_id: UUID
    pipeline_id: UUID | None


class TaskRead(TaskBase):
    """
    Task read model
    """
    id: UUID


class TaskUpdate(BaseModel):
    """
    Task update model
    This model is used to update a task
    """
    service: str | None
    url: str | None
    data_out: List[str] | None
    status: TaskStatus | None


class ServiceTaskBase(BaseModel):
    """
    Base class for Service task
    This model is used in subclasses
    """
    s3_access_key_id: str
    s3_secret_access_key: str
    s3_region: str
    s3_host: str
    s3_bucket: str
    task: TaskRead


class ServiceTask(ServiceTaskBase):
    """
    Service task
    This model is sent from the engine with the information
    """
    pass
