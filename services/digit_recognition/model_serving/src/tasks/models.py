from typing import List

from pydantic.main import BaseModel

from .enums import TaskStatus
from uuid import UUID


class Task(BaseModel):
    """
    Task model
    """
    id: UUID
    data_in: List[str] | None
    data_out: List[str] | None
    status: TaskStatus
    s3_access_key: str
    s3_secret_access_key: str
    s3_region: str
    s3_host: str
