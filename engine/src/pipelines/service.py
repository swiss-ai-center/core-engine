from fastapi import Depends, FastAPI, UploadFile
from inspect import Parameter, Signature
from makefun import with_signature

from execution_units.enums import ExecutionUnitStatus
from services.models import Service
from storage.service import StorageService
from sqlmodel import Session, select, desc
from database import get_session
from common_code.logger.logger import Logger, get_logger
from common_code.common.enums import FieldDescriptionType
from uuid import UUID
from pipeline_steps.models import PipelineStep
from pipelines.models import Pipeline, PipelineUpdate, PipelineCreate, PipelineRead
from common.exceptions import NotFoundException, InconsistentPipelineException
import graphlib
from pipeline_executions.models import PipelineExecution, PipelineExecutionReadWithPipelineAndTasks
from pipeline_executions.service import PipelineExecutionsService
from tasks.enums import TaskStatus
from tasks.models import TaskUpdate
from tasks.service import TasksService

REGISTERED_PIPELINES_TAG = "Registered Pipelines"


class PipelinesService:
    def __init__(
            self,
            logger: Logger = Depends(get_logger),
            storage: StorageService = Depends(),
            session: Session = Depends(get_session),
            pipeline_executions_service: PipelineExecutionsService = Depends(),
            tasks_service: TasksService = Depends(),
    ):
        self.logger = logger
        self.logger.set_source(__name__)
        self.storage = storage
        self.session = session
        self.pipeline_executions_service = pipeline_executions_service
        self.tasks_service = tasks_service

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

    def create(self, pipeline: PipelineCreate, app: FastAPI):
        """
        Create a pipeline
        :param pipeline: Pipeline to create
        :return: Created pipeline
        """
        self.logger.debug("Creating pipeline")

        pipeline_steps_create = pipeline.steps
        pipeline_steps = []
        pipeline = Pipeline.from_orm(pipeline)

        for pipeline_step in pipeline_steps_create:
            new_pipeline_step = PipelineStep(
                pipeline_id=pipeline.id,
                identifier=pipeline_step.identifier,
                needs=pipeline_step.needs,
                condition=pipeline_step.condition,
                inputs=pipeline_step.inputs,
                service_id=pipeline_step.service_id,
            )
            pipeline_step_create = PipelineStep.from_orm(new_pipeline_step)
            pipeline_steps.append(pipeline_step_create)
        pipeline.steps = pipeline_steps

        # Check if pipeline is consistent
        if not self.check_pipeline_consistency(pipeline):
            raise InconsistentPipelineException("Pipeline is not consistent")

        for step in pipeline.steps:
            self.session.add(step)

        self.session.add(pipeline)

        # Add slug to FastAPI
        self.logger.debug("Adding route to FastAPI")
        self.enable_pipeline(app, pipeline)

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
        pipeline_executions_list = self.session.exec(
            select(PipelineExecution).where(PipelineExecution.pipeline_id == pipeline_id)
        ).all()
        current_pipeline_steps = current_pipeline.steps
        pipeline_data = pipeline.dict(exclude_unset=True)
        self.logger.debug(f"Updating pipeline {pipeline_id} with data: {pipeline_data}")
        steps_updated = False
        if "steps" in pipeline_data:
            steps_updated = True
            pipeline_steps = []
            self.logger.debug("Updating steps")
            for step in pipeline_data["steps"]:
                if "condition" not in step:
                    condition = None
                else:
                    condition = step["condition"]
                if "needs" not in step:
                    needs = None
                else:
                    needs = step["needs"]
                new_step = PipelineStep(
                    pipeline_id=current_pipeline.id,
                    identifier=step["identifier"],
                    needs=needs,
                    condition=condition,
                    inputs=step["inputs"],
                )
                pipeline_steps.append(new_step)
            del pipeline_data["steps"]
            current_pipeline.steps = pipeline_steps
        for key, value in pipeline_data.items():
            setattr(current_pipeline, key, value)

        # Check if pipeline is consistent
        if not self.check_pipeline_consistency(current_pipeline):
            raise InconsistentPipelineException("Pipeline is not consistent")

        if steps_updated:
            # Check if there are pipeline_executions that are linked to the pipeline
            self.logger.debug(f"Checking if there are pipeline_executions linked to pipeline {pipeline_id}")
            for pipeline_execution in pipeline_executions_list:
                for task in pipeline_execution.tasks:
                    # Update the tasks to set pipeline_execution_id to None and status to ARCHIVED
                    self.logger.debug(f"Updating task {task.id} with pipeline_execution_id to None "
                                      f"and status to ARCHIVED")
                    self.tasks_service.update(
                        task.id,
                        TaskUpdate(status=TaskStatus.ARCHIVED, pipeline_execution_id=None)
                    )
                # Delete the pipeline_execution
                self.logger.debug(f"Deleting pipeline_execution {pipeline_execution.id}")
                self.pipeline_executions_service.delete(pipeline_execution.id)

            # Delete the steps
            self.logger.debug(f"Deleting current steps for pipeline {pipeline_id}")
            for step in current_pipeline_steps:
                self.logger.debug(f"Deleting step {step.id}")
                self.session.delete(step)

        self.session.add(current_pipeline)
        self.session.commit()
        self.session.refresh(current_pipeline)
        self.logger.debug(f"Updated pipeline with id {current_pipeline.id}")
        return current_pipeline

    def delete(self, pipeline_id: UUID, app: FastAPI):
        """
        Delete a pipeline
        :param pipeline_id: Pipeline id
        :param app: FastAPI reference
        """
        self.logger.debug("Delete pipeline")
        current_pipeline = self.session.get(Pipeline, pipeline_id)
        if not current_pipeline:
            raise NotFoundException("Pipeline Not Found")
        self.session.delete(current_pipeline)
        # Delete the route from FastAPI
        for route in app.routes:
            if route.path == f"/{current_pipeline.slug}":
                app.routes.remove(route)
                self.logger.debug(f"Route {route.path} removed from FastAPI app")
                app.openapi_schema = None
                break
        self.session.commit()
        self.logger.debug(f"Deleted pipeline with id {current_pipeline.id}")

    def enable_pipeline(self, app: FastAPI, pipeline: Pipeline):
        is_pipeline_route_present = False

        for route in app.routes:
            if route.path == f"/{pipeline.slug}":
                is_pipeline_route_present = True
                break

        # Add the route to the app if not present
        if not is_pipeline_route_present:
            # Create the `handler` signature from pipeline's `data_in_fields`
            handler_params = []
            for data_in_field in pipeline.data_in_fields:
                handler_params.append(
                    Parameter(
                        data_in_field["name"],
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=UploadFile,
                    )
                )

            pipeline_id = pipeline.id

            @with_signature(Signature(handler_params))
            async def handler(*args, **kwargs: UploadFile):
                """
                This function represents a pipeline function.
                It handles the files described by the pipeline, upload them to the S3 bucket
                and create the tasks for each step of the pipeline. It also creates a
                pipeline_execution.
                """
                # TODO: Implement the handler
                self.logger.debug(f"Received request for pipeline {pipeline_id}")
                return PipelineExecutionReadWithPipelineAndTasks(
                    id=UUID("00000000-0000-0000-0000-000000000000"),
                    pipeline_id=UUID("00000000-0000-0000-0000-000000000000"),
                    status=ExecutionUnitStatus.AVAILABLE,
                    pipeline=PipelineRead(
                        id=UUID("00000000-0000-0000-0000-000000000000"),
                        name="Test",
                        slug="test",
                        description="Test",
                        summary="Test",
                        data_in_fields=[],
                        data_out_fields=[],
                        steps=[],
                    ),
                    tasks=[],
                )

            app.add_api_route(
                f"/{pipeline.slug}",
                handler,
                methods=["POST"],
                summary=pipeline.summary,
                description=pipeline.description,
                tags=[REGISTERED_PIPELINES_TAG],
                responses={
                    400: {"detail": "Invalid Content Type"},
                    500: {"detail": "Internal Server Error"},
                },
                response_model=PipelineExecutionReadWithPipelineAndTasks
            )
            app.openapi_schema = None

    def check_pipeline_consistency(self, pipeline: Pipeline):
        """
        Check if a pipeline is consistent
        :param pipeline: Pipeline to check
        :return: True if pipeline is consistent, False otherwise
        """
        self.logger.debug("Check pipeline consistency")

        steps = pipeline.steps

        graph = {}
        for step in steps:
            identifier = step.identifier
            needs = step.needs

            graph[identifier] = needs

        # Create the graph from the structure
        ts = graphlib.TopologicalSorter(graph)

        # Check if the graph is valid
        try:
            ts.prepare()
        except Exception:
            raise InconsistentPipelineException("The graph is not valid.")

        # Iterate over the graph
        predecessors = set()
        while ts.is_active():
            node_group = ts.get_ready()

            # Iterate over the nodes that are ready
            for node in node_group:
                # Store the node in the predecessors
                predecessors.add(node)

                # Find the step definition in all the available steps
                step_found = None
                for step in steps:
                    if step.identifier == node:
                        step_found = step
                        break

                if not step_found:
                    raise InconsistentPipelineException(f"The step {node} is not defined.")

                inputs = step_found.inputs

                # Check if the inputs of the step are available
                used_identifiers = []
                for index, input_elem in enumerate(inputs):
                    input_split = input_elem.split('.')

                    if len(input_split) != 2:
                        raise InconsistentPipelineException(
                            f"The input {input_elem} is not valid. It should be in the format '<identifier>.<variable>'"
                        )

                    identifier, variable = input_split
                    used_identifiers.append(identifier)

                    if identifier == step_found.identifier:
                        raise InconsistentPipelineException(
                            f"The identifier {identifier} is the same as the current step.")

                    # Check if the identifier is the pipeline
                    if identifier == "pipeline":
                        # Check if the variable is available in the pipeline
                        variables_found = [v for v in pipeline.data_in_fields if v["name"] == variable]
                    else:
                        # Check if the identifier is a predecessor
                        if identifier not in predecessors:
                            raise InconsistentPipelineException(
                                f"The identifier {identifier} is not a predecessor of the current step."
                            )

                        # Check if identifier exists in the steps
                        steps_found = [s for s in steps if s.identifier == identifier]

                        if len(steps_found) == 0:
                            raise InconsistentPipelineException(
                                f"The identifier {identifier} does not exist in the steps.")
                        elif len(steps_found) > 1:
                            raise InconsistentPipelineException(
                                f"The identifier {identifier} is set multiple times in the steps.")

                        execution_unit = self.session.get(Service, steps_found[0].service_id)
                        if not execution_unit:
                            raise NotFoundException("Execution Unit Not Found")

                        # Check if the variable is available in the execution unit
                        variables_found = [v for v in execution_unit.data_out_fields if v["name"] == variable]

                    if len(variables_found) == 0:
                        raise InconsistentPipelineException(
                            f"The variable {variable} is not available in the execution unit.")
                    elif len(variables_found) > 1:
                        raise InconsistentPipelineException(
                            f"The variable {variable} is set multiple times in the execution unit.")

                    variable_types_to_check = [v["type"] for v in variables_found][0]

                    # Get the data_in_fields of the current step
                    current_execution_unit = self.session.get(Service, step_found.service_id)
                    if not current_execution_unit:
                        raise NotFoundException("Execution Unit Not Found")

                    # Check if the type of the variable is compatible with the input of the remote execution unit
                    input_types = current_execution_unit.data_in_fields[index]["type"]

                    # For each input type, create a FieldDescriptionType
                    input_types = [FieldDescriptionType(v) for v in input_types]

                    # Compare variable_types_to_check with input_types without checking the order
                    if not sorted(variable_types_to_check) == sorted(input_types):
                        raise InconsistentPipelineException(
                            f"The type of the variable {variable} is not compatible with the input type of the "
                            f"remote execution unit. "
                            f"Variable type: {variable_types_to_check}, "
                            f"Input type: {input_types}")

                # Check if all the identifiers in the needs are used in the inputs
                for need in step_found.needs:
                    if need not in used_identifiers:
                        self.logger.debug(
                            f"WARNING: The identifier {need} is not used in the inputs of the current step "
                            f"({node}). It should be removed from the needs.")

            # Mark the nodes as done
            ts.done(*node_group)

        self.logger.debug("Pipeline is consistent")
        return True
