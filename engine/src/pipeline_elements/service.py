from fastapi import Depends
from sqlmodel import Session, select, desc
from database import get_session
from common_code.logger.logger import Logger, get_logger
from uuid import UUID
from pipeline_elements.models import PipelineElement, PipelineElementUpdate
from pipeline_elements.enums import PipelineElementType
from common.exceptions import NotFoundException, UnprocessableEntityException


class PipelineElementsService:
    def __init__(
        self,
        logger: Logger = Depends(get_logger),
        session: Session = Depends(get_session),
    ):
        self.logger = logger
        self.logger.set_source(__name__)
        self.session = session

    def find_many(self, skip: int = 0, limit: int = 100):
        """
        Find many pipeline elements
        :param skip: number of pipeline elements to skip
        :param limit: number of pipeline elements to return
        :return: list of pipeline elements
        """
        self.logger.debug("Find many pipeline elements")
        return self.session.exec(
            select(PipelineElement)
            .order_by(desc(PipelineElement.created_at))
            .offset(skip)
            .limit(limit)
        ).all()

    def find_one(self, pipeline_element_id: UUID):
        """
        Find one pipeline element
        :param pipeline_element_id: id of pipeline element to find
        :return: pipeline element
        """
        self.logger.debug("Find pipeline element")

        return self.session.get(PipelineElement, pipeline_element_id)

    def create(self, pipeline_element: PipelineElement):
        """
        Create a pipeline element
        :param pipeline_element: pipeline element to create
        :return: created pipeline element
        """
        self.logger.debug("Creating pipeline element")

        if pipeline_element.type == PipelineElementType.SERVICE:
            if pipeline_element.service_id is None:
                raise UnprocessableEntityException(
                    "'service_id' is required when creating a "
                    "PipelineElement of type 'service'",
                )

            pipeline_element = PipelineElement(
                type=pipeline_element.type,
                identifier=pipeline_element.identifier,
                service_id=pipeline_element.service_id,
            )
        elif pipeline_element.type == PipelineElementType.BRANCH:
            if pipeline_element.condition is None:
                raise UnprocessableEntityException(
                    "'condition' is required when creating a "
                    "PipelineElement of type 'branch'",
                )
            elif pipeline_element.then is None and pipeline_element.otherwise is None:
                raise UnprocessableEntityException(
                    "either 'then' or 'otherwise' is required when creating a "
                    "PipelineElement of type 'branch'",
                )

            pipeline_element = PipelineElement(
                type=pipeline_element.type,
                identifier=pipeline_element.identifier,
                condition=pipeline_element.condition,
                then=pipeline_element.then,
                otherwise=pipeline_element.otherwise,
            )

        self.session.add(pipeline_element)
        self.session.commit()
        self.session.refresh(pipeline_element)
        self.logger.debug(f"Created pipeline element with id {pipeline_element.id}")

        return pipeline_element

    def update(
        self,
        pipeline_element_id: UUID,
        pipeline_element: PipelineElementUpdate,
    ):
        """
        Update a pipeline element
        :param pipeline_element_id: id of pipeline element to update
        :param pipeline_element: pipeline element to update
        :return: updated pipeline element
        """
        self.logger.debug("Update pipeline element")
        current_pipeline_element = self.session.get(PipelineElement, pipeline_element_id)

        if not current_pipeline_element:
            raise NotFoundException("Pipeline Element Not Found")

        current_pipeline_element.identifier = pipeline_element.identifier
        current_pipeline_element.type = pipeline_element.type
        current_pipeline_element.next = pipeline_element.then
        current_pipeline_element.otherwise = pipeline_element.otherwise
        # current_pipeline_element.pipeline_id = pipeline_element.pipeline_id
        current_pipeline_element.service_id = None
        current_pipeline_element.condition = None
        current_pipeline_element.then = None
        current_pipeline_element.wait_on = None

        if pipeline_element.type == PipelineElementType.SERVICE:
            if pipeline_element.service_id is None:
                raise UnprocessableEntityException(
                    "'service_id' is required when updating a "
                    "PipelineElement of type 'service'",
                )

            current_pipeline_element.service_id = pipeline_element.service_id
        elif pipeline_element.type == PipelineElementType.BRANCH:
            if pipeline_element.condition is None:
                raise UnprocessableEntityException(
                    "'condition' is required when updating a "
                    "PipelineElement of type 'branch'",
                )
            elif pipeline_element.then is None and pipeline_element.otherwise is None:
                raise UnprocessableEntityException(
                    "either 'then' or 'otherwise' is required when updating a "
                    "PipelineElement of type 'branch'",
                )
            then_element = self.session.get(PipelineElement, pipeline_element.then)
            if not then_element:
                raise NotFoundException("'Then' Pipeline Element Not Found")
            current_pipeline_element.condition = pipeline_element.condition
            current_pipeline_element.then = then_element
            current_pipeline_element.otherwise = pipeline_element.otherwise

        self.session.add(current_pipeline_element)
        self.session.commit()
        self.session.refresh(current_pipeline_element)
        self.logger.debug(f"Updated pipeline element with id {current_pipeline_element.id}")
        return current_pipeline_element

    def delete(self, pipeline_element_id: UUID):
        """
        Delete a pipeline element
        :param pipeline_element_id: id of pipeline element to delete
        """
        self.logger.debug("Delete pipeline element")
        pipeline_element = self.session.get(PipelineElement, pipeline_element_id)
        if not pipeline_element:
            raise NotFoundException("Pipeline Element Not Found")
        self.session.delete(pipeline_element)
        self.session.commit()
        self.logger.debug(f"Deleted pipeline element with id {pipeline_element.id}")
