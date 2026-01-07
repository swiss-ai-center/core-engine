from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, AnyHttpUrl, field_validator, field_serializer, TypeAdapter
from sqlmodel import SQLModel, Relationship, Field, Column, String
from common_code.common.models import FieldDescription, ExecutionUnitTag
from common.models import CoreModel, PydanticJSON
from execution_units.enums import ExecutionUnitStatus
from pydantic_settings import SettingsConfigDict


class ServiceBase(CoreModel):
    """
    Base class for a Service.
    Uses PydanticJSON to handle DB serialization of complex objects.
    """
    model_config = SettingsConfigDict(arbitrary_types_allowed=True)

    name: str
    slug: str = Field(unique=True)
    summary: str
    description: Optional[str] = None
    status: ExecutionUnitStatus = ExecutionUnitStatus.AVAILABLE

    # Updated to use PydanticJSON
    data_in_fields: Optional[List[FieldDescription]] = Field(
        sa_column=Column(PydanticJSON),
        default=None
    )
    data_out_fields: Optional[List[FieldDescription]] = Field(
        sa_column=Column(PydanticJSON),
        default=None
    )
    tags: Optional[List[ExecutionUnitTag]] = Field(
        sa_column=Column(PydanticJSON),
        default=None
    )

    url: AnyHttpUrl = Field(sa_column=Column(String))
    docs_url: Optional[AnyHttpUrl] = Field(
        sa_column=Column(String),
        default="https://docs.swiss-ai-center.ch/reference/core-concepts/service"
    )
    has_ai: Optional[bool] = False

    @field_validator('data_in_fields', 'data_out_fields', mode='before')
    @classmethod
    def validate_field_descriptions(cls, v):
        if v is None:
            return v
        return [FieldDescription(**item) if isinstance(item, dict) else item for item in v]

    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        if v is None:
            return v
        return [ExecutionUnitTag(**item) if isinstance(item, dict) else item for item in v]

    @field_serializer('data_in_fields', 'data_out_fields', when_used='json')
    def serialize_field_descriptions(self, v):
        if v is None:
            return v
        return [item.model_dump(mode='json') if hasattr(item, 'model_dump') else item for item in v]

    @field_serializer('tags', when_used='json')
    def serialize_tags(self, v):
        if v is None:
            return v
        return [item.model_dump(mode='json') if hasattr(item, 'model_dump') else item for item in v]

    @field_validator('url', 'docs_url', mode='before')
    @classmethod
    def validate_urls(cls, v):
        if v is None or isinstance(v, AnyHttpUrl):
            return v
        return TypeAdapter(AnyHttpUrl).validate_python(v)


class Service(ServiceBase, table=True):
    """
    Service model
    This model is the one that is stored in the database
    """

    __tablename__ = "services"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tasks: List["Task"] = Relationship(
        sa_relationship_kwargs={"cascade": "delete"}, back_populates="service"
    )  # noqa F821
    pipeline_steps: List["PipelineStep"] = Relationship(
        back_populates="service"
    )  # noqa F821


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

    name: Optional[str] = None
    slug: Optional[str] = None
    url: Optional[AnyHttpUrl] = None
    docs_url: Optional[AnyHttpUrl] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ExecutionUnitStatus] = None
    data_in_fields: Optional[List[FieldDescription]] = None
    data_out_fields: Optional[List[FieldDescription]] = None
    tags: Optional[List[ExecutionUnitTag]] = None
    has_ai: Optional[bool] = None


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


class ServicesWithCount(BaseModel):
    """
    Services with count
    This model is used to return a list of filtered services with the count of all services matching a filter
    """

    count: int
    services: List[ServiceRead]


from pipeline_steps.models import PipelineStep  # noqa E402
from tasks.models import Task, TaskRead  # noqa E402

Service.model_rebuild()
ServiceTask.model_rebuild()
ServiceTaskBase.model_rebuild()
ServiceReadWithTasks.model_rebuild()
