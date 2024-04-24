import json
import re
import graphlib
from fastapi import FastAPI, UploadFile, Depends, HTTPException
from fastapi.responses import JSONResponse
from inspect import Parameter, Signature
from makefun import with_signature
from execution_units.enums import ExecutionUnitStatus
from services.models import Service, ServiceTask
from storage.service import StorageService
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Session, select, desc, col, or_, and_, cast
from database import get_session
from common_code.logger.logger import Logger, get_logger
from common_code.common.models import ExecutionUnitTag
from common_code.common.enums import FieldDescriptionType, ExecutionUnitTagName, ExecutionUnitTagAcronym
from uuid import UUID
from pipeline_steps.models import PipelineStep
from pipelines.models import Pipeline, PipelineUpdate, PipelineCreate
from common.exceptions import NotFoundException, InconsistentPipelineException, ConflictException
from pipeline_executions.models import FileKeyReference, PipelineExecution, PipelineExecutionReadWithPipelineAndTasks
from pipeline_executions.service import PipelineExecutionsService
from tasks.enums import TaskStatus
from tasks.models import Task, TaskUpdate
from tasks.service import TasksService, sanitize
from config import Settings, get_settings
from services.service import ServicesService
from httpx import HTTPError
from http_client import HttpClient
from fastapi.encoders import jsonable_encoder

REGISTERED_PIPELINES_TAG = "Registered Pipelines"


class PipelinesService:
    def __init__(
            self,
            logger: Logger = Depends(get_logger),
            storage_service: StorageService = Depends(),
            session: Session = Depends(get_session),
            pipeline_executions_service: PipelineExecutionsService = Depends(),
            tasks_service: TasksService = Depends(),
            settings: Settings = Depends(get_settings),
            services_service: ServicesService = Depends(),
            http_client: HttpClient = Depends(),
    ):
        self.logger = logger
        self.logger.set_source(__name__)
        self.session = session
        self.pipeline_executions_service = pipeline_executions_service
        self.tasks_service = tasks_service
        self.settings = settings
        self.services_service = services_service
        self.storage_service = storage_service
        self.http_client = http_client

    def get_count(self, statement: select):
        """
        Get the number of pipelines from a statement.
        :return: The number of pipelines.
        """
        self.logger.debug("Get the number of pipelines.")
        count = self.session.exec(statement)
        return len([pipeline for pipeline in count])

    def create_statement(
            self,
            search: str | None,
            order_by: str | None,
            order: str | None,
            tags: str | None,
            status: str = None,
    ) -> select:
        """
        Create a statement to find many pipelines.
        :param search: The search string.
        :param order_by: The field to order by.
        :param order: The order direction.
        :param tags: The tags to filter by.
        :param status: The status to filter by.
        :return: The statement.
        """
        filter_statement = or_(
            Pipeline.status == ExecutionUnitStatus.AVAILABLE,
            Pipeline.status == ExecutionUnitStatus.UNAVAILABLE,
            Pipeline.status == ExecutionUnitStatus.DISABLED,
        )

        if status:
            filter_statement = Pipeline.status == status

        if search:
            filter_statement = and_(
                filter_statement,
                or_(
                    col(Pipeline.name).ilike(f"%{search}%"),
                    col(Pipeline.description).ilike(f"%{search}%"),
                    col(Pipeline.slug).ilike(f"%{search}%"),
                    col(Pipeline.summary).ilike(f"%{search}%")
                ),
            )

        if tags:
            tags_acronyms_string = tags.split(",")
            # from tag acronym to tag acronym enum
            tags_acronyms_string = [ExecutionUnitTagAcronym(tag_acronym) for tag_acronym in tags_acronyms_string]
            # get the key of the enum for each acronym
            tags_enums = [tag_acronym.name for tag_acronym in tags_acronyms_string]
            # create the list of tag acronyms
            tags_acronyms = [ExecutionUnitTagAcronym[tag_name] for tag_name in tags_enums]
            # create the list of tag names
            tags_names = [ExecutionUnitTagName[tag_name] for tag_name in tags_enums]
            # create the list of tags
            tags_list = [ExecutionUnitTag(name=tag_name, acronym=tag_acronym) for tag_name, tag_acronym in
                         zip(tags_names, tags_acronyms)]

            if self.session.bind.dialect.name == "postgresql":
                tags_filter = cast(Pipeline.tags, JSONB).contains(cast(jsonable_encoder(tags_list), JSONB))
            else:
                tags_filter = and_(*[Pipeline.tags.contains(tag) for tag in tags_list])

            filter_statement = and_(
                Pipeline.tags.is_not(None),
                filter_statement,
                tags_filter
            )

        statement = select(Pipeline).where(
            filter_statement
        )

        if order == "desc":
            statement = statement.order_by(desc(order_by))
        else:
            statement = statement.order_by(order_by)

        return statement

    def find_many_with_total_count(
            self,
            search: str = "",
            skip: int = 0,
            limit: int = 100,
            order_by: str = "name",
            order: str = "asc",
            tags: str = None,
            status: str = None
    ):
        """
        Find many pipelines with total count.
        :param search: The search string.
        :param skip: The number of pipelines to skip.
        :param limit: The maximum number of pipelines to return.
        :param order_by: The field to order by.
        :param order: The order (asc or desc).
        :param tags: The tags to filter by.
        :param status: The status to filter by.
        :return: The list of filtered pipelines and the total count.
        """
        self.logger.debug("Find many pipelines with total count.")

        statement = self.create_statement(search, order_by, order, tags, status)

        statement_to_count = statement

        statement = statement.offset(skip).limit(limit)

        pipelines = self.session.exec(statement).all()

        total_count = self.get_count(statement_to_count)

        return total_count, pipelines

    def find_many(
            self,
            search: str = "",
            skip: int = 0,
            limit: int = 100,
            order_by: str = "name",
            order: str = "asc",
            tags: str = None,
            status: str = None
    ):
        """
        Find many pipelines.
        :param search: The search string.
        :param skip: The number of pipelines to skip.
        :param limit: The maximum number of pipelines to return.
        :param order_by: The field to order by.
        :param order: The order (asc or desc).
        :param tags: The tags to filter by.
        :param status: The status to filter by.
        :return: The list of pipelines.
        """
        self.logger.debug("Find many pipelines")

        statement = self.create_statement(search, order_by, order, tags, status)

        statement = statement.offset(skip).limit(limit)

        pipelines = self.session.exec(statement).all()

        return pipelines

    def find_one(self, pipeline_id: UUID):
        """
        Find one pipeline
        :param pipeline_id: Pipeline id
        :return: Pipeline
        """
        self.logger.debug("Find pipeline")

        return self.session.get(Pipeline, pipeline_id)

    def find_one_by_slug(self, pipeline_slug: str):
        """
        Find a pipeline by its slug.
        :param pipeline_slug:
        :return: The pipeline if found, None otherwise
        """
        self.logger.debug(f"Find pipeline with slug {pipeline_slug}")

        return self.session.exec(select(Pipeline).where(Pipeline.slug == pipeline_slug)).first()

    def create(self, pipeline: PipelineCreate, app: FastAPI):
        """
        Create a pipeline
        :param pipeline: Pipeline to create
        :param app: FastAPI app
        :return: Created pipeline
        """
        self.logger.debug("Creating pipeline")

        found_pipeline = self.session.exec(select(Pipeline).where(Pipeline.slug == pipeline.slug)).first()

        # Check if pipeline already exists
        if found_pipeline:
            raise ConflictException(f"Pipeline with slug '{found_pipeline.slug}' already exists.")

        # Backup the pipeline steps
        pipeline_steps = pipeline.steps

        # Set the pipeline steps to an empty list - will be filled later
        pipeline.steps = []

        # Create the pipeline
        pipeline = Pipeline.model_validate(pipeline)
        self.session.add(pipeline)
        self.session.flush()
        self.session.refresh(pipeline)

        # Create the pipeline steps
        for step in pipeline_steps:

            service = self.services_service.find_one_by_slug(step.service_slug)

            if not service:
                raise NotFoundException(f"Service with slug '{step.service_slug}' not found.")

            new_pipeline_step = PipelineStep(
                identifier=step.identifier,
                needs=step.needs,
                condition=step.condition,
                inputs=step.inputs,
                pipeline=pipeline,
                service=service,
            )

            pipeline_step = PipelineStep.model_validate(new_pipeline_step)
            self.session.add(pipeline_step)
            self.session.flush()

        # Check if pipeline is consistent
        try:
            self.check_pipeline_consistency(pipeline)
        except InconsistentPipelineException as e:
            self.session.rollback()
            raise e

        self.logger.debug("Pipeline is consistent")
        self.session.commit()
        self.session.refresh(pipeline)

        # Add slug to FastAPI
        self.logger.debug("Adding route to FastAPI")
        self.enable_pipeline(app, pipeline)
        self.logger.debug(f"Created pipeline with id {pipeline.id}")

        return pipeline

    def update(self, app: FastAPI, pipeline_id: UUID, pipeline: PipelineUpdate):
        """
        Update a pipeline
        :param app: FastAPI app
        :param pipeline_id: Pipeline id
        :param pipeline: Pipeline to update
        :return: Updated pipeline
        """
        self.logger.debug("Update pipeline")

        # Get the current pipeline
        current_pipeline = self.session.get(Pipeline, pipeline_id)

        if not current_pipeline:
            raise NotFoundException("Pipeline Not Found")

        old_pipeline_slug = current_pipeline.slug

        # Dump the model data
        pipeline_data = pipeline.model_dump(exclude_unset=True)

        # Update Pipeline attributes
        for key, value in pipeline_data.items():
            if key == "steps":
                continue
            setattr(current_pipeline, key, value)

        # Update/Add/Delete Steps
        existing_step_identifiers = {step.identifier for step in current_pipeline.steps}
        updated_step_ids = set()

        for step_data in pipeline_data["steps"]:
            step_identifier = step_data.get("identifier")
            if step_identifier in existing_step_identifiers:
                # Update existing step
                step = self.session.exec(
                    select(PipelineStep).where(
                        and_(PipelineStep.pipeline_id == pipeline_id, PipelineStep.identifier == step_identifier)
                    )
                ).first()
                # Get the service
                service = self.services_service.find_one_by_slug(step_data["service_slug"])
                if not service:
                    raise NotFoundException(f"Service with slug '{step_data['service_slug']}' not found.")
                step.service = service
                for key, value in step_data.items():
                    if key == "service_slug":
                        continue
                    setattr(step, key, value)
                updated_step_ids.add(step_identifier)
            else:
                # Get the service
                service = self.services_service.find_one_by_slug(step_data["service_slug"])
                if not service:
                    raise NotFoundException(f"Service with slug '{step_data['service_slug']}' not found.")
                step_data["service"] = service
                # Remove the service_slug key
                step_data.pop("service_slug")
                # Add new step
                new_step = PipelineStep(**step_data, pipeline_id=pipeline_id)
                self.session.add(new_step)
                updated_step_ids.add(new_step.id)

        # Delete steps that are no longer present
        steps_to_delete = existing_step_identifiers - updated_step_ids
        for step_identifier in steps_to_delete:
            step = self.session.exec(
                select(PipelineStep).where(
                    and_(PipelineStep.pipeline_id == pipeline_id, PipelineStep.identifier == step_identifier)
                )
            ).first()
            self.session.delete(step)

        # Save the updated pipeline
        self.session.add(current_pipeline)
        self.session.flush()
        self.session.refresh(current_pipeline)

        # Check if pipeline is consistent
        try:
            self.check_pipeline_consistency(current_pipeline)
        except InconsistentPipelineException as e:
            self.session.rollback()
            raise e

        # Update the pipeline execution tasks to archive them
        pipeline_executions = self.session.exec(
            select(PipelineExecution).where(PipelineExecution.pipeline_id == pipeline_id)
        ).all()

        for pipeline_execution in pipeline_executions:
            for task in pipeline_execution.tasks:
                # Update the tasks to set pipeline_execution_id to None and status to ARCHIVED
                self.logger.debug(
                    f"Updating task {task.id} with pipeline_execution_id to None "
                    f"and status to ARCHIVED"
                )
                self.tasks_service.update(
                    task.id,
                    TaskUpdate(status=TaskStatus.ARCHIVED, pipeline_execution_id=None, data_out=[])
                )

            # Delete the pipeline_execution
            self.logger.debug(f"Deleting pipeline_execution {pipeline_execution.id}")
            self.pipeline_executions_service.delete(pipeline_execution.id)

        self.session.commit()

        # Update OpenAPI route
        self.remove_route(app, old_pipeline_slug)
        self.enable_pipeline(app, current_pipeline)
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
        self.remove_route(app, current_pipeline.slug)
        self.session.commit()
        self.logger.debug(f"Deleted pipeline with id {current_pipeline.id}")

    def remove_route(self, app: FastAPI, slug: str):
        """
        Remove a route from FastAPI
        :param app: FastAPI reference
        :param slug: Slug of the route to remove
        """
        for route in app.routes:
            if route.path == f"/{slug}":
                app.routes.remove(route)
                self.logger.debug(f"Route {route.path} removed from FastAPI app")
                app.openapi_schema = None
                break

    def enable_pipelines(self, app: FastAPI):
        """
        Enable all pipelines
        :param app: FastAPI reference
        """
        pipelines = self.session.exec(select(Pipeline)).all()

        for pipeline in pipelines:
            self.enable_pipeline(app, pipeline)

    def enable_pipeline(self, app: FastAPI, pipeline: Pipeline):
        """
        Enable a pipeline
        :param app: FastAPI reference
        :param pipeline: Pipeline to enable
        """
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
            pipeline_steps = pipeline.steps

            @with_signature(Signature(handler_params))
            async def handler(*args, **kwargs: UploadFile):
                """
                This function represents a pipeline function.
                It handles the files described by the pipeline, upload them to the S3 bucket
                and create the tasks for each step of the pipeline. It also creates a
                pipeline_execution.

                The function signature is described using the `with_signature` annotation that
                allows FastAPI to generate the OpenAPI spec. As the function has an undefined
                number of arguments at runtime, we have to access these arguments through the
                `kwargs` argument.
                """

                # The files for the pipeline
                pipeline_files = []

                # Iterate over the uploaded files
                for param_index, (_, file) in enumerate(kwargs.items()):
                    # Get the content type of the file
                    file_content_type = file.content_type

                    # Get the file name of the part
                    file_part_name = pipeline.data_in_fields[param_index]["name"]

                    # Get the accepted content types for the file
                    accepted_file_content_types = pipeline.data_in_fields[param_index]["type"]

                    # Check if the content type of the uploaded file is accepted
                    if file_content_type not in accepted_file_content_types:
                        return JSONResponse(
                            status_code=400,
                            content={
                                "error": "Invalid Content Type",
                                "message": f"The content type of the file '{file_part_name}' must be of type "
                                           f"{accepted_file_content_types}."
                            }
                        )

                    # Upload the file to S3
                    try:
                        file_key = await self.storage_service.upload(file)
                    except Exception:
                        return JSONResponse(
                            status_code=500,
                            content={
                                "error": "Storage upload",
                                "message": f"The upload of file '{file_part_name}' has failed."
                            }
                        )

                    pipeline_files.append(FileKeyReference(reference=f"pipeline.{file_part_name}", file_key=file_key))

                pipeline_tasks = []
                for pipeline_step in pipeline_steps:
                    task = Task()

                    task.service_id = pipeline_step.service_id
                    task.pipeline_execution_id = None
                    task.status = TaskStatus.SCHEDULED

                    task = self.tasks_service.create(task)

                    pipeline_tasks.append(task)

                # Create the pipeline execution
                pipeline_execution = PipelineExecution(
                    pipeline_id=pipeline_id,
                    current_pipeline_step_id=pipeline_steps[0].id,
                    files=pipeline_files,
                    tasks=pipeline_tasks,
                )

                # Save the pipeline execution
                pipeline_execution = self.pipeline_executions_service.create(pipeline_execution)

                # Get the first task of the pipeline
                task = None
                for task_elem in pipeline_execution.tasks:
                    if task_elem.service_id == pipeline_steps[0].service_id:
                        task = task_elem
                        break

                if not task:
                    raise NotFoundException("Task not found")

                service = self.services_service.find_one(task.service_id)

                if not service:
                    raise NotFoundException("Service not found")

                data_in = []

                for index, file in enumerate(service.data_in_fields):
                    pipeline_file = pipeline_execution.files[index]
                    data_in.append(pipeline_file["file_key"])

                async def clean_up(cause: str):
                    self.logger.debug("Removing files from storage...")

                    # Remove files from storage
                    for pipeline_file_to_remove in pipeline_files:
                        await self.storage_service.delete(pipeline_file_to_remove["file_key"])

                    self.logger.debug("Files from storage removed.")

                    self.logger.debug("Updating tasks...")

                    for pipeline_task in pipeline_tasks:
                        pipeline_task.status = TaskStatus.ERROR
                        await self.tasks_service.update(task.id, pipeline_task)

                    raise HTTPException(
                        status_code=500,
                        detail=f"Could not execute pipeline '{pipeline.slug}', cause: {cause}"
                    )

                should_post_task = True

                # Check if a condition is set for the pipeline step
                if pipeline.steps[0].condition:
                    condition = pipeline.steps[0].condition
                    files_mapping = {}
                    # Extract the files needed from the condition
                    # If files found, download the required files (text and JSON only) from S3 and update the condition
                    # to match a variable to a file
                    for file in pipeline_execution.files:
                        # Get the file key
                        file_key = file["file_key"]

                        # Get the file reference
                        file_reference = file["reference"]

                        # Get the file extension
                        file_extension = file_key.split(".")[-1]

                        # Check if file key is in task_files
                        if file_key in data_in:
                            file_reference_one_word = re.sub(r"[-.]", "_", file_reference)

                            # Check if file is a text file
                            if file_extension == "txt":
                                try:
                                    # Download the file from S3
                                    file_content = await self.storage_service.get_file_as_bytes(file_key)

                                    # Add the file to the files mapping
                                    files_mapping[file_reference_one_word] = file_content.decode("utf-8")

                                    # Update the condition
                                    condition = condition.replace(
                                        file_reference,
                                        file_reference_one_word
                                    )
                                except Exception as e:
                                    self.logger.error(f"Could not download file {file_key} from S3.: {e}")

                            # Check if file is a JSON file
                            elif file_extension == "json":
                                try:
                                    # Download the file from S3
                                    file_content = await self.storage_service.get_file_as_bytes(file_key)

                                    # Add the file to the files mapping as a JSON object
                                    files_mapping[file_reference_one_word] = json.loads(file_content.decode("utf-8"))

                                    # Update the condition
                                    condition = condition.replace(
                                        file_reference,
                                        file_reference_one_word
                                    )
                                except Exception as e:
                                    self.logger.error(f"Could not download file {file_key} from S3.: {e}")
                            else:
                                self.logger.warning(f"File {file_key} is not a text or JSON file. "
                                                    f"It will not be used in the condition.")

                    # Evaluate the condition
                    condition_clean = sanitize(condition)
                    if not eval(condition_clean, {}, files_mapping):
                        self.logger.info(f"Condition {condition_clean} evaluated to False. "
                                         f"Not launching the pipeline execution.")
                        should_post_task = False

                if should_post_task:
                    task.status = TaskStatus.PENDING
                    task.data_in = data_in
                    task.data_out = None

                    task = await self.tasks_service.update(task.id, task)

                    # Create the service task
                    service_task = ServiceTask(
                        s3_access_key_id=self.settings.s3_access_key_id,
                        s3_secret_access_key=self.settings.s3_secret_access_key,
                        s3_region=self.settings.s3_region,
                        s3_host=self.settings.s3_host,
                        s3_bucket=self.settings.s3_bucket,
                        task=task,
                        callback_url=f"{self.settings.host}/tasks/{task.id}"
                    )

                    # Submit the service task to the remote service
                    try:
                        res = await self.http_client.post(f"{service.url}/compute", json=jsonable_encoder(service_task))

                        if res.status_code != 200:
                            raise HTTPException(status_code=res.status_code, detail=res.text)
                    except HTTPException as e:
                        self.logger.warning(f"Service {service.name} returned an error: {str(e)}")
                        await clean_up(cause=str(e))
                        raise e
                    except HTTPError as e:
                        self.logger.error(f"Sending request to the service {service.name} failed: {str(e)}")
                        await clean_up(cause=str(e))
                        raise HTTPException(
                            status_code=500,
                            detail=f"Sending request to the service {service.name} failed: {str(e)}",
                        )
                    else:
                        # Return the created pipeline execution to the end-user
                        return pipeline_execution
                else:
                    await clean_up(cause="First step's condition evaluated to False")

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

    def disable_pipeline(self, app: FastAPI, pipeline: Pipeline):
        """
        Disable a pipeline from the API
        :param app: The FastAPI app reference
        :param pipeline: The pipeline to unregister
        """
        self.logger.info(f"Disabling pipeline {pipeline.name}")

        self.remove_route(app, pipeline.slug)

        self.logger.info(f"Pipeline {pipeline.name} unregistered")

    def check_pipeline_consistency(self, pipeline: Pipeline):
        """
        Check if a pipeline is consistent
        :param pipeline: Pipeline to check
        :return: True if pipeline is consistent, False otherwise
        """
        self.logger.debug("Check pipeline consistency")

        if len(pipeline.steps) == 0:
            raise InconsistentPipelineException("Pipeline has no steps.")

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
            raise InconsistentPipelineException("One or many pipeline step(s) is/are used before instantiation.")

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

                    # Compare variable_types_to_check with input_types without checking the order,
                    # variable_types_to_check needs to be a subset of input_types or equal
                    if not set(variable_types_to_check).issubset(set(input_types)):
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
