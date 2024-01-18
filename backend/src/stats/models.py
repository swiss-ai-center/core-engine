from typing import List
from uuid import UUID
from tasks.models import TaskStatus
from pydantic import BaseModel


class StatusCount(BaseModel):
    """
    Status count
    """

    status: TaskStatus
    count: int


class ServiceStats(BaseModel):
    """
    Stats of a service
    """
    service_id: UUID
    service_name: str
    total: int
    status: List[StatusCount]


class StatsBase(BaseModel):
    """
    Base class for Stats
    This model contain counts of status of tasks grouped by service and a total count of status
    """
    total: int
    summary: List[StatusCount]
    services: List[ServiceStats]
