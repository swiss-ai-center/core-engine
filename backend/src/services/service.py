from inspect import Parameter, Signature
from sqlalchemy.exc import IntegrityError
from common_code.common.models import ExecutionUnitTag
from common_code.common.enums import ExecutionUnitTagName, ExecutionUnitTagAcronym
from fastapi import FastAPI, UploadFile, Depends, HTTPException
from fastapi.responses import JSONResponse
from makefun import with_signature
from uuid import UUID
from common.functions import get_example_filename
from execution_units.enums import ExecutionUnitStatus
from storage.service import StorageService
from tasks.service import TasksService
from tasks.models import Task, TaskReadWithServiceAndPipeline
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Session, select, desc, col, or_, and_, cast
from database import get_session
from common_code.logger.logger import Logger, get_logger
from config import Settings, get_settings
from services.models import Service, ServiceUpdate, ServiceTask
from common.exceptions import NotFoundException, ConflictException, UnreachableException, ConstraintException
from http_client import HttpClient
from fastapi.encoders import jsonable_encoder
from httpx import HTTPError

REGISTERED_SERVICES_TAG = "Registered Services"


class ServicesService:
    def __init__(
            self,
            logger: Logger = Depends(get_logger),
            storage_service: StorageService = Depends(),
            tasks_service: TasksService = Depends(),
            settings: Settings = Depends(get_settings),
            session: Session = Depends(get_session),
            http_client: HttpClient = Depends(),
    ):
        self.logger = logger
        self.storage_service = storage_service
        self.tasks_service = tasks_service
        self.settings = settings
        self.session = session
        self.http_client = http_client

        self.logger.set_source(__name__)

    def get_count(self, statement: select):
        """
        Get the number of services from a statement.
        :return: The number of services.
        """
        self.logger.debug("Get the number of services.")
        count = self.session.exec(statement)
        return len([service for service in count])

    def create_statement(
            self,
            search: str | None,
            order_by: str | None,
            order: str | None,
            tags: str | None,
            ai: bool | None,
            status: str = None,
    ) -> select:
        """
        Create a statement to find many services.
        :param search: The search string.
        :param order_by: The field to order by.
        :param order: The order direction.
        :param tags: The tags to filter by.
        :param ai: Only return services with AI.
        :param status: The status to filter by.
        :return: The statement.
        """
        filter_statement = or_(
            Service.status == ExecutionUnitStatus.AVAILABLE,
            Service.status == ExecutionUnitStatus.UNAVAILABLE,
            Service.status == ExecutionUnitStatus.DISABLED,
            Service.status == ExecutionUnitStatus.SLEEPING
        )
        print(status)

        if status:
            # status can be a comma separated list of statuses
            status_list = status.split(",")
            status_enums = [ExecutionUnitStatus[status_str.upper()] for status_str in status_list]
            filter_statement = and_(filter_statement, Service.status.in_(status_enums))

        if ai:
            filter_statement = and_(filter_statement, Service.has_ai == ai)

        if search:
            filter_statement = and_(
                filter_statement,
                or_(
                    col(Service.name).ilike(f"%{search}%"),
                    col(Service.description).ilike(f"%{search}%"),
                    col(Service.slug).ilike(f"%{search}%"),
                    col(Service.summary).ilike(f"%{search}%")
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
                tags_filter = cast(Service.tags, JSONB).contains(cast(jsonable_encoder(tags_list), JSONB))
            else:
                tags_filter = and_(*[Service.tags.contains(tag) for tag in tags_list])

            filter_statement = and_(
                Service.tags.is_not(None),
                filter_statement,
                tags_filter
            )

        statement = select(Service).where(
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
            ai: bool = False,
            status: str = None,
    ):
        """
        Find many services with total count.
        :param search: The search string.
        :param skip: The number of services to skip.
        :param limit: The maximum number of services to return.
        :param order_by: The field to order by.
        :param order: The order (asc or desc).
        :param tags: The tags to filter by.
        :param ai: Only return services with AI.
        :param status: The status to filter by.
        :return: The list of filtered services and the total count.
        """
        self.logger.debug("Find many services with total count.")

        statement = self.create_statement(search, order_by, order, tags, ai, status)

        statement_to_count = statement

        statement = statement.offset(skip).limit(limit)

        services = self.session.exec(statement).all()

        total_count = self.get_count(statement_to_count)

        return total_count, services

    def find_many(
            self,
            search: str = "",
            skip: int = 0,
            limit: int = 100,
            order_by: str = "name",
            order: str = "asc",
            tags: str = None,
            ai: bool = False,
            status: str = None,
    ):
        """
        Find many services.
        :param search: The search string.
        :param skip: The number of services to skip.
        :param limit: The maximum number of services to return.
        :param order_by: The field to order by.
        :param order: The order (asc or desc).
        :param tags: The tags to filter by.
        :param ai: Only return services with AI.
        :param status: The status to filter by.
        :return: The list of services.
        """
        self.logger.debug("Find many services")

        statement = self.create_statement(search, order_by, order, tags, ai, status)

        statement = statement.offset(skip).limit(limit)

        services = self.session.exec(statement).all()

        return services

    def find_one(self, service_id: UUID):
        """
        Find a service by its id.
        :param service_id:
        :return: The service if found, None otherwise
        """
        self.logger.debug(f"Find service with id {service_id}")

        return self.session.get(Service, service_id)

    def find_one_by_slug(self, service_slug: str):
        """
        Find a service by its slug.
        :param service_slug:
        :return: The service if found, None otherwise
        """
        self.logger.debug(f"Find service with slug {service_slug}")

        return self.session.exec(select(Service).where(Service.slug == service_slug)).first()

    async def create(self, service: Service, app: FastAPI):
        """
        Create a new service.
        :param service: The service to create
        :param app: The FastAPI app reference
        :return: The created service
        """
        self.logger.debug("Creating service")

        found_service = self.session.exec(select(Service).where(Service.slug == service.slug)).first()

        if found_service:
            raise ConflictException(f"Service with slug '{service.slug}' already exists.")

        self.logger.debug(f"Checking service {service.name} before adding it to the engine...")

        is_service_response_ok = True

        # stringify the url and docs_url and remove the trailing slash
        service.url = str(service.url).rstrip("/")
        service.docs_url = str(service.docs_url).rstrip("/")

        try:
            await self.check_if_service_is_reachable_and_ok(service)
        except UnreachableException as e:
            self.logger.debug(
                f"The service {service.name} is unreachable, it will not be added to the engine: {str(e)}")
            raise HTTPException(status_code=503, detail=str(e))
        except HTTPException:
            is_service_response_ok = False

        self.session.add(service)
        self.session.commit()
        self.session.refresh(service)

        if is_service_response_ok:
            self.logger.debug(f"The service {service.name} will be saved in the database as available")
            self.enable_service(app, service)
            return service
        else:
            error_message = f"The service {service.name} with ID {service.id} did not respond with an OK status, " \
                            "it will be saved in the database as unavailable"
            self.logger.debug(error_message)
            self.disable_service(app, service)
            raise HTTPException(status_code=500, detail=error_message)

    def update(self, service_id: UUID, service: ServiceUpdate):
        """
        Update a service.
        :param service_id: The id of the service to update.
        :param service: The service modifications.
        :return: The updated service.
        """
        self.logger.debug("Update service")
        current_service = self.session.get(Service, service_id)
        if not current_service:
            raise NotFoundException("Service Not Found")
        service_data = service.model_dump(exclude_unset=True)
        self.logger.debug(f"Updating service {service_id} with data: {service_data}")
        for key, value in service_data.items():
            if key == "url":
                # stringify the url and remove the trailing slash
                value = str(value).rstrip("/")
            if key == "docs_url":
                # stringify docs_url and remove the trailing slash
                value = str(value).rstrip("/")
            setattr(current_service, key, value)
        self.session.add(current_service)
        self.session.commit()
        self.session.refresh(current_service)
        self.logger.debug(f"Updated service with id {current_service.id}")
        return current_service

    def delete(self, service_id: UUID, app: FastAPI):
        """
        Delete a service.
        :param service_id: The id of the service to delete
        :param app: The FastAPI app reference
        """
        self.logger.debug("Delete service")
        current_service = self.session.get(Service, service_id)
        if not current_service:
            raise NotFoundException("Service Not Found")
        try:
            self.session.delete(current_service)
            self.remove_route(app, current_service.slug)
            self.session.commit()
        except IntegrityError:
            raise ConstraintException(
                "Service is linked to a pipeline, please update the related step in the pipeline first.")
        self.logger.debug(f"Deleted service with id {current_service.id}")

    def remove_route(self, app: FastAPI, slug: str):
        # Delete the service route from the app
        for route in app.routes:
            if route.path == f"/{slug}":
                app.routes.remove(route)
                self.logger.debug(f"Route {route.path} removed from FastAPI app")
                app.openapi_schema = None
                break

    def enable_service(self, app: FastAPI, service: Service):
        """
        Enable a service from the API and set its status to available
        :param app: The FastAPI app reference
        :param service: The service to enable
        """
        self.logger.info(f"Enabling service {service.name}")

        is_service_route_present = False

        for route in app.routes:
            if route.path == f"/{service.slug}":
                is_service_route_present = True
                break

        # Add the route to the app if not present
        if not is_service_route_present:
            # Create the `handler` signature from service's `data_in_fields`
            handler_params = []
            for data_in_field in service.data_in_fields:
                field_name = data_in_field.get("name") if isinstance(data_in_field, dict) else data_in_field.name
                handler_params.append(
                    Parameter(
                        field_name,
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=UploadFile,
                    )
                )

            service_id = service.id

            @with_signature(Signature(handler_params))
            async def handler(*args, **kwargs: UploadFile):
                """
                This function represents a service function.
                It handles the files described by the service, upload them to the S3 bucket
                and create the task with the uploaded files. It will then forward the task to
                the service in order to the service to execute them.

                The function signature is described using the `with_signature` annotation that
                allows FastAPI to generate the OpenAPI spec. As the function has an undefined
                number of arguments at runtime, we have to access these arguments through the
                `kwargs` argument.
                """

                # The files for the tasks
                task_files = []

                # Iterate over the uploaded files
                for param_index, (_, file) in enumerate(kwargs.items()):
                    # Get the content type of the file
                    file_content_type = file.content_type

                    data_in_field = service.data_in_fields[param_index]
                    file_part_name = data_in_field.get("name") if isinstance(data_in_field,
                                                                             dict) else data_in_field.name
                    accepted_file_content_types = data_in_field.get("type") if isinstance(data_in_field,
                                                                                          dict) else data_in_field.type

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
                    file_key = None
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

                    task_files.append(file_key)

                # Create the task
                task = Task()
                task.data_in = task_files
                task.service_id = service_id

                # Save the task in database
                task = self.tasks_service.create(task)

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

                async def clean_up():
                    self.logger.debug("Removing files from storage...")

                    # Remove files from storage
                    for task_file in task_files:
                        await self.storage_service.delete(task_file)

                    self.logger.debug("Files removed from storage.")

                    self.logger.debug("Removing task...")

                    # Remove the task previously created
                    self.tasks_service.delete(task.id)

                    self.logger.debug("Task removed.")

                    raise HTTPException(
                        status_code=500,
                        detail=f"The submission of the task to the service '{service.name}' has failed."
                    )

                # Submit the service task to the remote service
                try:
                    res = await self.http_client.post(
                        f"{service.url}/compute",
                        json=jsonable_encoder(service_task)
                    )

                    if res.status_code != 200:
                        raise HTTPException(status_code=res.status_code, detail=res.text)
                except HTTPException as e:
                    self.logger.warning(f"Service {service.name} returned an error: {str(e)}")
                    await clean_up()
                    raise e
                except HTTPError as e:
                    self.logger.error(f"Sending request to the service {service.name} failed: {str(e)}")
                    await clean_up()
                    raise HTTPException(
                        status_code=500,
                        detail=f"Sending request to the service {service.name} failed: {str(e)}",
                    )
                else:
                    # Return the created task to the end-user
                    return task

            # Enable pipelines linked to the service via pipeline steps
            self.enable_pipelines_linked_to_service(service)

            app.add_api_route(
                f"/{service.slug}",
                handler,
                methods=["POST"],
                summary=service.summary,
                description=service.description,
                tags=[REGISTERED_SERVICES_TAG],
                responses={
                    400: {"detail": "Invalid Content Type"},
                    500: {"detail": "Internal Server Error"},
                },
                response_model=TaskReadWithServiceAndPipeline,
            )
            app.openapi_schema = None

    def disable_service(self, app: FastAPI, service: Service):
        """
        Disable a service from the API and set its status to unavailable
        :param app: The FastAPI app reference
        :param service: The service to unregister
        """
        self.logger.info(f"Disabling service {service.name}")

        # Set the service as unavailable
        if service.status == ExecutionUnitStatus.DISABLED:
            self.logger.debug(f"Service {service.name} is already disabled")
            updated_service = service
        else:
            updated_service = self.update(service.id, ServiceUpdate(status=ExecutionUnitStatus.UNAVAILABLE))

        self.logger.debug(f"Service {service.name} status set to {updated_service.status.value}")

        # Disable pipeline linked to the service via pipeline steps
        self.disable_pipelines_linked_to_service(updated_service)

        self.remove_route(app, service.slug)

        self.logger.info(f"Service {service.name} unregistered")

    def enable_pipelines_linked_to_service(self, service: Service):
        """
        Enable pipelines linked to a service via pipeline steps
        :param service: The service to enable the pipelines for
        """
        self.logger.debug(f"Enabling pipelines linked to service {service.id}")

        # Get the pipelines linked to the service
        for pipeline_step in service.pipeline_steps:
            pipeline = pipeline_step.pipeline
            # check if the services linked to the pipeline are all available
            for step in pipeline.steps:
                if step.service.status != ExecutionUnitStatus.AVAILABLE:
                    return
            pipeline.status = ExecutionUnitStatus.AVAILABLE
            self.session.add(pipeline)
            self.session.commit()
            self.logger.debug(f"Pipeline {pipeline.name} status set to {pipeline.status.value}")

    def disable_pipelines_linked_to_service(self, service: Service):
        """
        Disable pipelines linked to a service via pipeline steps
        :param service: The service to disable the pipelines for
        """
        self.logger.debug(f"Disabling pipelines linked to service {service.id}")

        # Get the pipelines linked to the service
        for pipeline_step in service.pipeline_steps:
            pipeline = pipeline_step.pipeline
            pipeline.status = ExecutionUnitStatus.DISABLED
            self.session.add(pipeline)
            self.session.commit()
            self.logger.debug(f"Pipeline {pipeline.name} status set to {pipeline.status.value}")

    async def check_if_service_is_reachable_and_ok(self, service: Service):
        """
        Check if a service is reachable and that its response's is OK (status code 200).
        :param service: The service to check.
        :return: Throw UnreachableException if not reachable or throw HTTPException
                 if status code is different from 200
        """
        self.logger.debug(f"Checking service {service.url}/status")

        try:
            res = await self.http_client.get(f"{service.url}/status")

            if res.status_code != 200:
                raise HTTPException(status_code=res.status_code, detail=res.text)
        except HTTPError as e:
            raise UnreachableException(f"Service {service.name} ({service.slug}) unreachable: {str(e)}")

    async def check_services_availability(self, app: FastAPI):
        """
        Check all services availability and update the routes accordingly
        :param app: the FastAPI app reference
        """
        self.logger.info("Checking services availability...")
        services = self.find_many()

        if len(services) == 0:
            self.logger.info("No services in database.")
        else:
            for service in services:
                if service.status == ExecutionUnitStatus.DISABLED:
                    self.logger.info(f"Service {service.name} ({service.slug}) is disabled, skipping...")
                    continue
                try:
                    await self.check_if_service_is_reachable_and_ok(service)
                except HTTPException as e:
                    self.logger.warning(f"Service {service.name} ({service.slug}) did not return an OK: {str(e)}")
                    self.disable_service(app, service)
                except UnreachableException as e:
                    self.logger.warning(f"Service {service.name} ({service.slug}) unreachable: {str(e)}")
                    self.disable_service(app, service)
                else:
                    self.logger.info(f"Service {service.name} ({service.slug}) reachable and OK")
                    updated_service = self.update(service.id, ServiceUpdate(status=ExecutionUnitStatus.AVAILABLE))
                    self.enable_service(app, updated_service)

    async def wake_up_service(self, service: Service):
        """
        Wake up a service by sending a request to its /status endpoint.
        :param app: The FastAPI app reference
        :param service: The service to wake up
        """
        self.logger.info(f"Waking up service {service.name}")

        try:
            result = await self.http_client.get(f"{service.url}/status")
            if result.status_code != 200:
                raise HTTPException(status_code=result.status_code, detail=result.text)
        except HTTPError as e:
            self.logger.error(f"Waking up service {service.name} failed: {str(e)}")
        else:
            self.logger.info(f"Service {service.name} woke up successfully")

    def generate_code_snippet(self, service: Service):
        """
        Generate a code snippet for a service using input and output data fields.
        :param service: The service to generate the code snippet for.
        :return: The code snippet as python string to paste.
        """
        self.logger.debug(f"Generating code snippet for service {service.name}")

        # Prepare base url (use configured host, fall back to localhost)
        base_url = str(getattr(self.settings, "host", "http://localhost:8000")).rstrip("/")

        # Prepare function name derived from slug
        func_name = f"execute_{service.slug.replace('-', '_')}_workflow"

        # Prepare input fields (name and content-type)
        inputs = service.data_in_fields or []
        if not inputs:
            # fallback generic single file input
            inputs = [{"name": "file", "type": ["application/octet-stream"]}]

        # Determine if we need multiple file parameters
        has_multiple_inputs = len(inputs) > 1

        # Build function parameters based on inputs
        if has_multiple_inputs:
            param_list = ", ".join([
                f"{field.get('name') if isinstance(field, dict) else getattr(field, 'name', f'input{idx}')}_path"
                for idx, field in enumerate(inputs)
            ])
            first_param = f"{inputs[0].get('name') if isinstance(inputs[0], dict) else getattr(inputs[0], 'name', 'input0')}_path"
        else:
            param_list = "file_path"
            first_param = "file_path"

        # Build files dict
        file_entries = []
        file_open_statements = []

        for idx, field in enumerate(inputs):
            field_name = field.get("name") if isinstance(field, dict) else getattr(field, "name", f"input{idx}")
            accepted = field.get("type") if isinstance(field, dict) else getattr(field, "type", None)

            # Get the first accepted content type
            if isinstance(accepted, (list, tuple)) and len(accepted) > 0:
                content_type = accepted[0]
            elif isinstance(accepted, str):
                content_type = accepted
            else:
                content_type = "application/octet-stream"

            param_name = f"{field_name}_path" if has_multiple_inputs else "file_path"
            file_var = f"f{idx}" if has_multiple_inputs else "f"

            file_open_statements.append(f"open({param_name}, 'rb') as {file_var}")

            # Determine filename from path
            file_entries.append(
                f"                '{field_name}': (os.path.basename({param_name}), {file_var}, '{content_type}')"
            )

        # Build with statement and files dict
        if has_multiple_inputs:
            with_statement = f"with {', '.join(file_open_statements)}:"
            files_block = "        files = {\n" + ",\n".join(file_entries) + "\n            }"
        else:
            with_statement = f"with {file_open_statements[0]}:"
            files_block = "        files = {\n" + "\n".join(file_entries) + "\n            }"

        # Build docstring args section
        if has_multiple_inputs:
            args_doc_lines = [
                f"        {field.get('name') if isinstance(field, dict) else getattr(field, 'name', f'input{idx}')}_path: Path to the {field.get('name') if isinstance(field, dict) else getattr(field, 'name', f'input{idx}')} file"
                for idx, field in enumerate(inputs)
            ]
            args_doc = "\n".join(args_doc_lines)
        else:
            args_doc = "        file_path: Path to the input file"

        # Determine output handling based on output types
        outputs = service.data_out_fields or []

        # Check if outputs might be binary (non-JSON)
        has_binary_output = False
        if outputs:
            for output in outputs:
                output_types = output.get("type") if isinstance(output, dict) else getattr(output, "type", [])
                if isinstance(output_types, (list, tuple)):
                    output_types = list(output_types)
                elif isinstance(output_types, str):
                    output_types = [output_types]
                else:
                    output_types = []

                # Check if any output type is binary
                binary_types = [
                    "image/jpeg", "image/png", "application/pdf", "application/zip",
                    "audio/mpeg", "audio/ogg", "application/octet-stream"
                ]
                if any(ot in binary_types for ot in output_types):
                    has_binary_output = True
                    break

        # Build download logic based on output types
        if has_binary_output:
            download_logic = """            # Step 3: Download all output files
                    results = []
                    download_urls = []
                    for output_id in data_out:
                        download_url = f"{base_url}/storage/{output_id}"
                        download_urls.append(download_url)
                        print(f"Downloading result: {output_id}")
                        response = requests.get(download_url)
            
                        if response.status_code == 200:
                            # Try to parse as JSON first, otherwise keep raw content
                            try:
                                results.append(response.json())
                            except:
                                results.append(response.content)
                        else:
                            print(f"Error downloading {output_id}: {response.status_code}")
                    
                    # Print download URLs
                    print("\\n=== Download URLs ===")
                    for idx, url in enumerate(download_urls, 1):
                        print(f"Output {idx}: {url}")"""
        else:
            download_logic = """            # Step 3: Download all output files
                    results = []
                    download_urls = []
                    for output_id in data_out:
                        download_url = f"{base_url}/storage/{output_id}"
                        download_urls.append(download_url)
                        print(f"Downloading result: {output_id}")
                        response = requests.get(
                            download_url,
                            headers={'accept': 'application/json'}
                        )
            
                        if response.status_code == 200:
                            results.append(response.json())
                        else:
                            print(f"Error downloading {output_id}: {response.status_code}")
                    
                    # Print download URLs
                    print("\\n=== Download URLs ===")
                    for idx, url in enumerate(download_urls, 1):
                        print(f"Output {idx}: {url}")"""

        # Get example filename for the main usage example
        example_files = []
        for idx, field in enumerate(inputs):
            example_files.append(f'"{get_example_filename(field)}"')

        example_call = f"{func_name}({', '.join(example_files)})"

        # Build the final snippet string
        snippet = f"""
        import requests
        import time
        import json
        import os
        
        
        def {func_name}({param_list}):
            \"\"\"
            Execute {service.name} workflow: upload inputs, poll for completion, download results.
        
            Args:
        {args_doc}
        
            Returns:
                dict or bytes: The downloaded result data, or None if error
            \"\"\"
            base_url = "{base_url}"
        
            # Step 1: Launch execution
            print(f"Uploading file(s): {{{first_param}}}")
            {with_statement}
        {files_block}
        
                response = requests.post(
                    f"{{base_url}}/{service.slug}",
                    files=files,
                    headers={{'accept': 'application/json'}}
                )
        
            if response.status_code not in [200, 201]:
                print(f"Error uploading file: {{response.status_code}}")
                return None
        
            task_data = response.json()
            task_id = task_data.get('id')
            print(f"Task created: {{task_id}}")
        
            # Step 2: Poll for task completion
            max_attempts = 60  # Maximum polling attempts
            poll_interval = 2  # Seconds between polls
        
            for attempt in range(max_attempts):
                print(f"Polling task status (attempt {{attempt + 1}}/{{max_attempts}})...")
                response = requests.get(
                    f"{{base_url}}/tasks/{{task_id}}",
                    headers={{'accept': 'application/json'}}
                )
        
                if response.status_code != 200:
                    print(f"Error fetching task status: {{response.status_code}}")
                    return None
        
                task_status = response.json()
                status = task_status.get('status', '').lower()
        
                print(f"Current status: {{status}}")
        
                if status == 'finished':
                    print("Task completed successfully!")
                    data_out = task_status.get('data_out', [])
        
                    if not data_out:
                        print("No output data found")
                        return None
        
        {download_logic}
        
                    # Return single result if only one output, otherwise return list
                    return results[0] if len(results) == 1 else results
        
                elif status == 'error':
                    error_msg = task_status.get('error_message', 'Unknown error')
                    print(f"Task failed with error: {{error_msg}}")
                    return None
        
                # Wait before next poll
                time.sleep(poll_interval)
        
            print("Timeout: Task did not complete within expected time")
            return None
        
        
        # Example usage
        if __name__ == "__main__":
            result = {example_call}
        
            if result:
                print("\\n=== Result ===")
                if isinstance(result, bytes):
                    print(f"Binary result: {{len(result)}} bytes")
                else:
                    print(json.dumps(result, indent=2))
            else:
                print("Failed to get result")
        """
        return snippet
