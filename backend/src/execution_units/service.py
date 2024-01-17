# from fastapi import Depends
# from sqlmodel import Session, select, desc
# from database import get_session
# from common_code.logger.logger import Logger, get_logger
# from uuid import UUID
# from common.exceptions import NotFoundException, UnprocessableEntityException
# from pipelines.models import Pipeline, PipelineUpdate
# from services.models import Service, ServiceUpdate
# from execution_units.models import ExecutionUnitBase
#
#
# class ExecutionUnitsService:
#     def __init__(
#             self,
#             logger: Logger = Depends(get_logger),
#             session: Session = Depends(get_session),
#     ):
#         self.logger = logger
#         self.logger.set_source(__name__)
#         self.session = session
#
#     def find_many(self, skip: int = 0, limit: int = 100):
#         """
#         Find many execution units
#         :param skip: number of execution units to skip
#         :param limit: number of execution units to return
#         :return: list of execution units
#         """
#         self.logger.debug("Find many execution units")
#         self.session.exec(
#             select(ExecutionUnit)
#             .order_by(desc(ExecutionUnit.created_at))
#             .offset(skip)
#             .limit(limit)
#         ).all()
#
#     def find_one(self, execution_unit_id: UUID):
#         """
#         Find one execution unit
#         :param execution_unit_id: id of execution unit to find
#         :return: execution unit
#         """
#         self.logger.debug("Find execution unit")
#
#         return self.session.get(ExecutionUnit, execution_unit_id)
#
#     def create(self, execution_unit: Service | Pipeline):
#         """
#         Create an execution unit
#         :param execution_unit: execution unit to create
#         :return: created execution unit
#         """
#         self.logger.debug("Creating execution unit")
#
#         self.session.add(execution_unit)
#         self.session.commit()
#         self.session.refresh(execution_unit)
#         self.logger.debug(f"Created execution unit with id {execution_unit.id}")
#
#         return execution_unit
#
#     def update(
#             self,
#             execution_unit_id: UUID,
#             execution_unit: PipelineUpdate,
#     ):
#         """
#         Update an execution unit
#         :param execution_unit_id: id of execution unit to update
#         :param execution_unit: execution unit to update
#         :return: updated execution unit
#         """
#         self.logger.debug("Update execution unit")
#         current_execution_unit = self.session.get(ExecutionUnit, execution_unit_id)
#
#         if not current_execution_unit:
#             raise NotFoundException("Execution Unit Not Found")
#
#         # Check if is a pipeline update
#         if isinstance(current_execution_unit, PipelineUpdate):
#             # Check if pipeline steps exist in the database
#             # cast to
#             for step in execution_unit.steps:
#
#         execution_unit_data = execution_unit.model_dump(exclude_unset=True)
#         self.logger.debug(f"Updating execution unit {execution_unit_id} with data: {execution_unit_data}")
#         for key, value in execution_unit_data.items():
#             setattr(current_execution_unit, key, value)
#         self.session.add(current_execution_unit)
#         self.session.commit()
#         self.session.refresh(current_execution_unit)
#         self.logger.debug(f"Updated execution unit with id {current_execution_unit.id}")
#         return current_execution_unit
#
#     def delete(self, execution_unit_id: UUID):
#         """
#         Delete an execution unit
#         :param execution_unit_id: id of execution unit to delete
#         """
#         self.logger.debug("Delete execution unit")
#         execution_unit = self.session.get(ExecutionUnit, execution_unit_id)
#         if not execution_unit:
#             raise NotFoundException("Execution Unit Not Found")
#         self.session.delete(execution_unit)
#         self.session.commit()
#         self.logger.debug(f"Deleted execution unit with id {execution_unit.id}")
