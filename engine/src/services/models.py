from typing import List
from uuid import UUID, uuid4
from pydantic import BaseModel, AnyHttpUrl
from sqlmodel import Field, SQLModel, Relationship
from common_code.common.models import FieldDescription
from execution_units.enums import ExecutionUnitType, ExecutionUnitStatus
from execution_units.models import ExecutionUnitBase


class ServiceBase(ExecutionUnitBase):
    """
    Base class for Service
    This model is used in subclasses
    """
    url: AnyHttpUrl = Field(nullable=False)


class Service(ServiceBase, table=True):
    """
    Service model
    This model is the one that is stored in the database
    """
    __tablename__ = "services"
    id: UUID = Field(default_factory=uuid4, primary_key=True, foreign_key="execution_units.id")
    tasks: List["Task"] = Relationship(back_populates="service")  # noqa F821

    __mapper_args__ = {
        "polymorphic_identity": ExecutionUnitType.SERVICE
    }


class ServiceRead(ServiceBase):
    """
    Service read model
    This model is used to return a service to the user
    """
    id: UUID


class ServiceReadWithTasks(ServiceRead):
    """
    Service read model with tasks
    This model is used to return a service to the user with the tasks
    """
    tasks: "List[TaskRead]"


class ServiceCreate(ServiceBase):
    """
    Service create model
    This model is used to create a service
    """
    pass


class ServiceUpdate(SQLModel):
    """
    Service update model
    This model is used to update a service
    """
    name: str | None
    slug: str | None
    url: AnyHttpUrl | None
    summary: str | None
    description: str | None
    status: ExecutionUnitStatus | None
    data_in_fields: List[FieldDescription] | None
    data_out_fields: List[FieldDescription] | None


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
    task: "TaskRead"
    callback_url: AnyHttpUrl


class ServiceTask(ServiceTaskBase):
    """
    Service task
    This model is sent to the service with the information
    related to S3 as well as the task to execute
    """
    pass


from tasks.models import Task, TaskRead  # noqa E402

Service.update_forward_refs()
ServiceTaskBase.update_forward_refs(task=TaskRead)
ServiceReadWithTasks.update_forward_refs(tasks=List[TaskRead])
