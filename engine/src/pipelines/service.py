from fastapi import Depends

from pipeline_elements.enums import PipelineElementType
from storage.service import StorageService
from sqlmodel import Session, select, desc
from database import get_session
from common_code.logger.logger import Logger, get_logger
from uuid import UUID
from pipelines.models import Pipeline, PipelineUpdate, PipelineCreate
from common.exceptions import NotFoundException, InconsistentPipelineException


class PipelinesService:
    def __init__(
            self,
            logger: Logger = Depends(get_logger),
            storage: StorageService = Depends(),
            session: Session = Depends(get_session),
    ):
        self.logger = logger
        self.logger.set_source(__name__)
        self.storage = storage
        self.session = session

    def find_many(self, skip: int = 0, limit: int = 100):
        """
        Find many pipelines
        :param skip: Skip the first n pipelines
        :param limit: Limit the number of pipelines
        :return: List of pipelines
        """
        self.logger.debug("Find many pipelines")
        return self.session.exec(select(Pipeline).order_by(desc(Pipeline.created_at)).offset(skip).limit(limit)).all()

    def find_one(self, pipeline_id: UUID):
        """
        Find one pipeline
        :param pipeline_id: Pipeline id
        :return: Pipeline
        """
        self.logger.debug("Find pipeline")

        return self.session.get(Pipeline, pipeline_id)

    def create(self, pipeline: Pipeline):
        """
        Create a pipeline
        :param pipeline: Pipeline to create
        :return: Created pipeline
        """
        self.logger.debug("Creating pipeline")

        self.session.add(pipeline)
        self.session.commit()
        self.session.refresh(pipeline)
        self.logger.debug(f"Created pipeline with id {pipeline.id}")

        return pipeline

    def update(self, pipeline_id: UUID, pipeline: PipelineUpdate):
        """
        Update a pipeline
        :param pipeline_id: Pipeline id
        :param pipeline: Pipeline to update
        :return: Updated pipeline
        """
        self.logger.debug("Update pipeline")
        current_pipeline = self.session.get(Pipeline, pipeline_id)
        if not current_pipeline:
            raise NotFoundException("Pipeline Not Found")
        pipeline_data = pipeline.dict(exclude_unset=True)
        self.logger.debug(f"Updating pipeline {pipeline_id} with data: {pipeline_data}")
        for key, value in pipeline_data.items():
            setattr(current_pipeline, key, value)
        self.session.add(current_pipeline)
        self.session.commit()
        self.session.refresh(current_pipeline)
        self.logger.debug(f"Updated pipeline with id {current_pipeline.id}")
        return current_pipeline

    def delete(self, pipeline_id: UUID):
        """
        Delete a pipeline
        :param pipeline_id: Pipeline id
        """
        self.logger.debug("Delete pipeline")
        current_pipeline = self.session.get(Pipeline, pipeline_id)
        if not current_pipeline:
            raise NotFoundException("Pipeline Not Found")
        self.session.delete(current_pipeline)
        self.session.commit()
        self.logger.debug(f"Deleted pipeline with id {current_pipeline.id}")

    def check_pipeline_consistency(self, pipeline: PipelineCreate):
        """
        Check if a pipeline is consistent
        :param pipeline: Pipeline to check
        :return: True if pipeline is consistent, False otherwise
        """
        self.logger.debug("Check pipeline consistency")

        # Check if pipeline has at least one element
        if len(pipeline.pipeline_elements) == 0:
            self.logger.error("Pipeline has no elements")
            raise InconsistentPipelineException("Pipeline has no elements")

        # Check if pipeline has one and only one type start element
        start_element = [element for element in pipeline.pipeline_elements if element.type == PipelineElementType.START]
        if len(start_element) == 0:
            self.logger.error("Pipeline has no start element")
            raise InconsistentPipelineException("Pipeline has no start element")
        elif len(start_element) > 1:
            self.logger.error("Pipeline has more than one start element")
            raise InconsistentPipelineException("Pipeline has more than one start element")

        # Check if pipeline has one and only one type end element
        end_element = [element for element in pipeline.pipeline_elements if element.type == PipelineElementType.END]
        if len(end_element) == 0:
            self.logger.error("Pipeline has no end element")
            raise InconsistentPipelineException("Pipeline has no end element")
        elif len(end_element) > 1:
            self.logger.error("Pipeline has more than one end element")
            raise InconsistentPipelineException("Pipeline has more than one end element")

        used_elements = [start_element[0]]
        current_element = start_element[0]
        while current_element.type != PipelineElementType.END:
            # Check if pipeline has no loop (each element is only used once)
            next_element_array = [element for element
                                  in pipeline.pipeline_elements
                                  if element.identifier == current_element.next]
            if len(next_element_array) != 1:
                self.logger.error("Pipeline has an element with a next element that does not exist")
                raise InconsistentPipelineException("Pipeline has an element with a next element that does not exist")
            next_element = next_element_array[0]
            if next_element in used_elements:
                self.logger.error(f"Pipeline has a loop. Element {next_element.identifier} is referenced twice")
                raise InconsistentPipelineException(f"Pipeline has a loop. Element {next_element.identifier} "
                                                    f"is referenced twice")
            used_elements.append(next_element)
            current_element = next_element

            # Check if chain of elements is consistent (input and output of each element are consistent)
            for field in current_element.data_in_fields:
                reference_element, reference_in_out, reference_field = field["reference"].split(".")

                if reference_element == "pipeline":
                    for pipeline_field in pipeline.data_in_fields:
                        if reference_in_out == "data_in_fields":
                            if pipeline_field["name"] == reference_field:
                                if pipeline_field["type"] != field["type"]:
                                    self.logger.error(
                                        "Pipeline has an element with an input field that does not have the same type")
                                    raise InconsistentPipelineException(
                                        "Pipeline has an element with an input field that does not have the same type")
                            else:
                                self.logger.error(
                                    f"Pipeline has an element with an input field that does not exist: "
                                    f"{reference_field}")
                                raise InconsistentPipelineException(
                                    f"Pipeline has an element with an input field that does not exist: "
                                    f"{reference_field}")

                        else:
                            if pipeline_field["name"] == reference_field:
                                if pipeline_field["type"] != field["type"]:
                                    self.logger.error(
                                        "Pipeline has an element with an input field that does not have the same type")
                                    raise InconsistentPipelineException(
                                        "Pipeline has an element with an input field that does not have the same type")
                            else:
                                self.logger.error(
                                    f"Pipeline has an element with an input field that does not exist: "
                                    f"{reference_field}")
                                raise InconsistentPipelineException(
                                    f"Pipeline has an element with an input field that does not exist: "
                                    f"{reference_field}")
                else:
                    for element in pipeline.pipeline_elements:
                        if element.identifier == reference_element:
                            if reference_in_out == "data_out_fields":
                                for element_field in element.data_out_fields:
                                    if element_field["name"] == reference_field:
                                        if element_field["type"] != field["type"]:
                                            self.logger.error(
                                                f"Pipeline has an element with an input field "
                                                f"that does not have the same type {element_field.type} {field.type}")
                                            raise InconsistentPipelineException(
                                                f"Pipeline has an element with an input field "
                                                f"that does not have the same type {element_field.type} {field.type}")
                                    else:
                                        self.logger.error(
                                            f"Pipeline has an element with an input field that does not exist: "
                                            f"{reference_field}")
                                        raise InconsistentPipelineException(
                                            f"Pipeline has an element with an input field that does not exist: "
                                            f"{reference_field}")
                            else:
                                self.logger.error(
                                    f"Pipeline element cannot have an input field that references an input field "
                                    f"(except pipeline entry): {reference_field}")
                                raise InconsistentPipelineException(
                                    f"Pipeline element cannot have an input field that references an input field "
                                    f"(except pipeline entry): {reference_field}")

            # Check if pipeline has no dead end (each element is used at least once)
            if next_element.type == PipelineElementType.END:
                # Subtract list of used elements from list of all elements
                unused_elements = [element for element in pipeline.pipeline_elements if element not in used_elements]
                if len(unused_elements) > 0:
                    self.logger.error(f"Pipeline has one or more dead ends: {unused_elements}")
                    raise InconsistentPipelineException(f"Pipeline has one or more dead ends: {unused_elements}")

            current_element = next_element
        return True
