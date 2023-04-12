from typing import List
from sqlmodel import Field, Column, JSON, Relationship
from common.models import CoreModel
from common_code.common.models import FieldDescription
from execution_units.enums import ExecutionUnitStatus
from uuid import UUID, uuid4
from database import Base


class ExecutionUnit(Base, CoreModel):
    """
    ExecutionUnit model
    """
    __tablename__ = "execution_units"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(nullable=False)
    slug: str = Field(nullable=False, unique=True)
    summary: str = Field(nullable=False)
    description: str | None = Field(default=None, nullable=True)
    status: ExecutionUnitStatus = Field(default=ExecutionUnitStatus.AVAILABLE, nullable=False)
    data_in_fields: List[FieldDescription] | None = Field(sa_column=Column(JSON), default=None, nullable=True)
    data_out_fields: List[FieldDescription] | None = Field(sa_column=Column(JSON), default=None, nullable=True)
    pipeline_steps: List["PipelineStep"] = Relationship(back_populates="execution_unit")  # noqa F821

    # Needed for Column(JSON) to work
    class Config:
        arbitrary_types_allowed = True


from pipeline_steps.models import PipelineStep  # noqa E402

ExecutionUnit.update_forward_refs()
