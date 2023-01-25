from inspect import Parameter, Signature
from fastapi import FastAPI, UploadFile, Depends, HTTPException
from fastapi.responses import JSONResponse
from makefun import with_signature
from uuid import UUID
from storage.service import StorageService
from tasks.service import TasksService
from tasks.models import Task, TaskReadWithServiceAndPipeline
from sqlmodel import Session, select, desc
from database import get_session
from logger.logger import Logger, get_logger
from config import Settings, get_settings
from .enums import ServiceStatus
from .models import Service, ServiceUpdate, ServiceTask
from common.exceptions import NotFoundException, ConflictException, UnreachableException
from http_client import HttpClient
from fastapi.encoders import jsonable_encoder
from httpx import HTTPError


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

    def find_many(self, skip: int = 0, limit: int = 100):
        """
        Find many services.
        :param skip: The number of services to skip.
        :param limit: The maximum number of services to return.
        :return: The list of services.
        """
        self.logger.debug("Find many services")
        return self.session.exec(select(Service).order_by(desc(Service.created_at)).offset(skip).limit(limit)).all()

    def find_one(self, service_id: UUID):
        """
        Find a service by its id.
        :param service_id:
        :return: The service if found, None otherwise
        """
        self.logger.debug(f"Find service with id {service_id}")

        return self.session.get(Service, service_id)

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
            self.logger.debug(
                f"The service {service.name} did not respond with an OK status,"
                "it will be saved in the database as unavailable"
            )
            self.disable_service(app, service)
            raise HTTPException(
                status_code=500,
                detail=f"The service {service.name} did not respond with an OK status,"
                       "it will be saved in the database as unavailable"
            )

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
        service_data = service.dict(exclude_unset=True)
        self.logger.debug(f"Updating service {service_id} with data: {service_data}")
        for key, value in service_data.items():
            setattr(current_service, key, value)
        self.session.add(current_service)
        self.session.commit()
        self.session.refresh(current_service)
        self.logger.debug(f"Updated service with id {current_service.id}")
        return current_service

    def delete(self, service_id: UUID):
        """
        Delete a service.
        :param service_id: The id of the service to delete.
        """
        self.logger.debug("Delete service")
        current_service = self.session.get(Service, service_id)
        if not current_service:
            raise NotFoundException("Service Not Found")
        self.session.delete(current_service)
        self.session.commit()
        self.logger.debug(f"Deleted service with id {current_service.id}")

    def enable_service(self, app: FastAPI, service: Service):
        """
        Enable a service from the API and set its status to available
        :param app: The FastAPI app reference
        :param service: The service to enable
        """
        self.logger.info(f"Enabling service {service.name}")

        # Set the service as available
        updated_service = self.update(service.id, ServiceUpdate(status=ServiceStatus.AVAILABLE))

        self.logger.debug(f"Service {service.name} status set to {updated_service.status.value}")

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
                handler_params.append(
                    Parameter(
                        data_in_field["name"],
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

                    # Get the file name of the part
                    file_part_name = service.data_in_fields[param_index]["name"]

                    # Get the accepted content types for the file
                    accepted_file_content_types = service.data_in_fields[param_index]["type"]

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
                # TODO: How to manage the pipeline?
                # task.pipeline = pipeline

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
                )

                async def clean_up():
                    self.logger.debug("Removing files from storage...")

                    # Remove files from storage
                    for task_file in task_files:
                        await self.storage_service.delete(task_file)

                    self.logger.debug("Files from storage removed.")

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
                    res = await self.http_client.post(f"{service.url}/compute", json=jsonable_encoder(service_task))

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

            app.add_api_route(
                f"/{service.slug}",
                handler,
                methods=["POST"],
                summary=service.summary,
                description=service.description,
                tags=[service.name],
                responses={
                    400: {"detail": "Invalid Content Type"},
                    500: {"detail": "Internal Server Error"},
                },
                response_model=TaskReadWithServiceAndPipeline,
            )

    def disable_service(self, app: FastAPI, service: Service):
        """
        Disable a service from the API and set its status to unavailable
        :param app: The FastAPI app reference
        :param service: The service to unregister
        """
        self.logger.info(f"Disabling service {service.name}")

        # Set the service as unavailable
        updated_service = self.update(service.id, ServiceUpdate(status=ServiceStatus.UNAVAILABLE))

        self.logger.debug(f"Service {service.name} status set to {updated_service.status.value}")

        for route in app.routes:
            if route.path == f"/{service.slug}":
                app.routes.remove(route)
                break

        self.logger.info(f"Service {service.name} unregistered")

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
                # if service.status == ServiceStatus.AVAILABLE:
                    try:
                        await self.check_if_service_is_reachable_and_ok(service)
                    except HTTPException as e:
                        self.logger.warning(f"Service {service.name} ({service.slug}) did not return an OK: {str(e)}")
                        self.disable_service(app, service)
                    except UnreachableException as e:
                        self.logger.error(f"Service {service.name} ({service.slug}) unreachable: {str(e)}")
                        self.disable_service(app, service)
                    else:
                        self.logger.info(f"Service {service.name} ({service.slug}) reachable and OK")
                        self.enable_service(app, service)
                # else:
                #     self.logger.info(
                #         f"Service {service.name} ({service.slug}) is unavailable. You can change its status manually "
                #         f"or by restarting the service"
                #     )
