import os
from inspect import Parameter, Signature
from fastapi import FastAPI, UploadFile, Depends
from fastapi.responses import JSONResponse
from makefun import with_signature
from uuid import UUID
from storage.service import StorageService
from tasks.service import TasksService
from tasks.models import Task, TaskReadWithServiceAndPipeline
from sqlmodel import Session, select, desc
from uuid import uuid4
from database import get_session
from logger import Logger, get_logger
from config import Settings, get_settings
from .models import Service, ServiceUpdate, ServiceTask
from common.exceptions import NotFoundException, ConflictException
from http_client import HttpClient
from fastapi.encoders import jsonable_encoder


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

    def add_route(
        self,
        app: FastAPI,
        service: Service
    ):
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
                            "message": f"The content type of the file '{file_part_name}' must be of type {accepted_file_content_types}."
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
            task.service = service
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

            # Submit the service task to the remote service
            try:
                await self.http_client.post(f"{service.url}/compute", json=jsonable_encoder(service_task))

                # Return the created task to the end-user
                return task
            except Exception as e:
                self.logger.warning(f"Service cannot be reached: {str(e)}")
                self.logger.debug("Removing files from storage...")

                # Remove files from storage
                for task_file in task_files:
                    await self.storage_service.delete(task_file)

                self.logger.debug("Files from storage removed.")

                self.logger.debug("Removing task...")

                # Remove the task previousely created
                self.tasks_service.delete(task.id)

                self.logger.debug("Task removed.")

                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Service task submission",
                        "message": f"The submission of the task to the service '{service.name}' has failed."
                    }
                )

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

    def find_many(self, skip: int = 0, limit: int = 100):
        self.logger.debug("Find many services")
        return self.session.exec(select(Service).order_by(desc(Service.created_at)).offset(skip).limit(limit)).all()

    def create(self, service: Service, app: FastAPI):
        self.logger.debug("Creating service")

        found_service = self.session.exec(select(Service).where(Service.slug == service.slug)).first()

        if found_service:
            raise ConflictException("Service already existing with same slug")
        else:
            self.session.add(service)
            self.session.commit()
            self.session.refresh(service)
            self.logger.debug(f"Created service with id {service.id}")

            self.logger.debug("Adding route...")
            self.add_route(app, service)
            self.logger.debug("Route added...")

            return service

    def find_one(self, service_id: UUID):
        self.logger.debug("Find service")

        return self.session.get(Service, service_id)

    def update(self, service_id: UUID, service: ServiceUpdate):
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
        self.logger.debug("Delete service")
        current_service = self.session.get(Service, service_id)
        if not current_service:
            raise NotFoundException("Service Not Found")
        self.session.delete(current_service)
        self.session.commit()
        self.logger.debug(f"Deleted service with id {current_service.id}")

    async def check_service_availability(self, service_slug: str, service_url: str):
        self.logger.info(f"Checking service availability for service {service_slug}")
        self.logger.debug(f"Checking url {service_url}")
        res = await self.http_client.get(f"{service_url}/ping")
        if res.status_code == 200:
            return True
        return False

    async def instantiate_services(self, app: FastAPI):
        self.logger.info("Instantiating services...")
        services = self.find_many()

        if len(services) == 0:
            self.logger.info("No services in database.")
        else:
            for service in services:
                try:
                    self.logger.info(f"Instantiating service {service.name}")
                    if await self.check_service_availability(service.slug, service.url):
                        self.add_route(app, service)
                        self.logger.info(f"Service {service.name} instantiated")
                    else:
                        self.logger.warning(f"Service {service.name} is not available")
                        self.unregister_service(app, service)

                except Exception as e:
                    self.logger.warning(f"Service {service.name} cannot be instantiated")
                    self.unregister_service(app, service)

            self.logger.info("Services instantiated.")

    async def check_services_availability(self, app_ref: FastAPI):
        self.logger.info("Checking services availability...")
        services = self.find_many()

        if len(services) == 0:
            self.logger.info("No services in database.")
        else:
            for service in services:
                try:
                    if await self.check_service_availability(service.slug, service.url):
                        # TODO: check if route is already present
                        self.logger.info(f"Service {service.name} is available")
                    else:
                        self.logger.warning(f"Service {service.name} is not available")
                        self.unregister_service(app_ref, service)

                except Exception as e:
                    self.logger.warning(f"Service {service.name} cannot be joined: {e}")
                    self.unregister_service(app_ref, service)

    def unregister_service(self, app: FastAPI, service: Service):
        self.logger.info(f"Unregistering service {service.name}")

        # TODO: check if remove or set unavailable
        self.session.delete(service)
        self.session.commit()

        for route in app.routes:
            if route.path == f"/{service.slug}":
                app.routes.remove(route)
                break

        self.logger.info(f"Service {service.name} unregistered")
