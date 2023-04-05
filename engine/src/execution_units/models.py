from typing import List
from sqlmodel import Field, Column, JSON, Relationship
from common.models import CoreModel
from common_code.common.models import FieldDescription
from execution_units.enums import ExecutionUnitStatus, ExecutionUnitType
from uuid import UUID, uuid4


class ExecutionUnitBase(CoreModel):
    """
    Base class for ExecutionUnit
    This model is used in subclasses
    """
    name: str = Field(nullable=False)
    slug: str = Field(nullable=False, unique=True)
    summary: str = Field(nullable=False)
    description: str | None = Field(default=None, nullable=True)
    status: ExecutionUnitStatus = Field(default=ExecutionUnitStatus.AVAILABLE, nullable=False)
    data_in_fields: List[FieldDescription] | None = Field(sa_column=Column(JSON), default=None, nullable=True)
    data_out_fields: List[FieldDescription] | None = Field(sa_column=Column(JSON), default=None, nullable=True)

    # Needed for Column(JSON) to work
    class Config:
        arbitrary_types_allowed = True


class ExecutionUnit(ExecutionUnitBase, table=True):
    """
    ExecutionUnit model
    """
    __tablename__ = "execution_units"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    type: ExecutionUnitType = Field(nullable=False)
    pipeline_steps: List["PipelineStep"] = Relationship(back_populates="execution_units")  # noqa F821

    __mapper_args__ = {
        "polymorphic_identity": "execution_unit",
        "polymorphic_on": "type"
    }
