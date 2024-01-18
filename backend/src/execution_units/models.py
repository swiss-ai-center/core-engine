# from typing import List
# from sqlmodel import Field, Column, JSON
# from common.models import CoreModel
# from common_code.common.models import FieldDescription, ExecutionUnitTag
# from execution_units.enums import ExecutionUnitStatus


# class ExecutionUnitBase(CoreModel):
#     """
#     ExecutionUnit model
#     """

#     name: str = Field(nullable=False)
#     slug: str = Field(nullable=False, unique=True)
#     summary: str = Field(nullable=False)
#     description: str | None = Field(default=None, nullable=True)
#     status: ExecutionUnitStatus = Field(
#         default=ExecutionUnitStatus.AVAILABLE, nullable=False
#     )
#     data_in_fields: List[FieldDescription] | None = Field(
#         sa_column=Column(JSON), default=None
#     )
#     data_out_fields: List[FieldDescription] | None = Field(
#         sa_column=Column(JSON), default=None
#     )
#     tags: List[ExecutionUnitTag] | None = Field(sa_column=Column(JSON), default=None)

#     # Needed for Column(JSON) to work
#     class Config:
#         arbitrary_types_allowed = True
