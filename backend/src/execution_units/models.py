# from typing import List, Optional
# from sqlmodel import Field, Column, JSON
# from common.models import CoreModel
# from common_code.common.models import FieldDescription, ExecutionUnitTag
# from execution_units.enums import ExecutionUnitStatus


# class ExecutionUnitBase(CoreModel):
#     """
#     ExecutionUnit model
#     """
#     model_config = SettingsConfigDict(arbitrary_types_allowed=True)

#     name: str
#     slug: str = Field(unique=True)
#     summary: str
#     description: Optional[str] = None
#     status: ExecutionUnitStatus = ExecutionUnitStatus.AVAILABLE
#     )
#     data_in_fields: Optional[List[FieldDescription]] = Field(sa_column=Column(JSON), default=None)
#     data_out_fields: Optional[List[FieldDescription]] = Field(sa_column=Column(JSON), default=None)
#     tags: Optional[List[ExecutionUnitTag]] = Field(sa_column=Column(JSON), default=None)
