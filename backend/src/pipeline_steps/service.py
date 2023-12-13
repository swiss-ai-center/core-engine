from fastapi import Depends
from sqlmodel import Session, select, desc
from database import get_session
from common_code.logger.logger import Logger, get_logger
from uuid import UUID
from pipeline_steps.models import PipelineStep


class PipelineStepsService:
    def __init__(
        self,
        logger: Logger = Depends(get_logger),
        session: Session = Depends(get_session),
    ):
        self.logger = logger
        self.logger.set_source(__name__)
        self.session = session

    def find_many(self, skip: int = 0, limit: int = 100, order_by: str = "name", order: str = "desc"):
        """
        Find many pipeline steps
        :param skip: number of pipeline steps to skip
        :param limit: number of pipeline steps to return
        :param order_by: field to order by
        :param order: order to sort by
        :return: list of pipeline steps
        """
        self.logger.debug("Find many pipeline steps")
        if order == "desc":
            return self.session.exec(
                select(PipelineStep)
                .order_by(desc(order_by))
                .offset(skip)
                .limit(limit)
            ).all()
        else:
            return self.session.exec(
                select(PipelineStep).order_by(order_by).offset(skip).limit(limit)
            ).all()

    def find_one(self, pipeline_step_id: UUID):
        """
        Find one pipeline step
        :param pipeline_step_id: id of pipeline step to find
        :return: pipeline step
        """
        self.logger.debug("Find pipeline step")

        return self.session.get(PipelineStep, pipeline_step_id)
