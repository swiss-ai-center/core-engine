import json
from inspect import Parameter, Signature
from fastapi import FastAPI, UploadFile, Request, Depends
from fastapi.responses import JSONResponse
from storage.service import StorageService
from sqlmodel import Session, select, desc
from database import get_session
from logger import Logger
from uuid import UUID
from .models import Service, ServiceUpdate
from common.exception import NotFoundException


def strToArray(string):
    if string is None:
        return []
    return string.strip('][').replace(" ", "").split(",")


class ServicesService:
    def __init__(self, logger: Logger = Depends(), storage: StorageService = Depends(),
                 session: Session = Depends(get_session)):
        self.logger = logger
        self.logger.set_source(__name__)
        self.storage = storage
        self.session = session

    def add_route(self, app, id, name, slug, url, summary=None, description=None, data_in_fields=None,
                 data_out_fields=None):
        # This should be wrapped in a functor, however a bug in starlette prevents the handler to be correctly called if __call__ is declared async. This should be fixed in version 0.21.0 (https://github.com/encode/starlette/pull/1444).
        async def handler(*args, **kwargs):
            jobData = {}
            jsonParts = set()

            request = kwargs["req"]
            form = await request.form()
            i = 0
            for field_desc in data_in_fields:
                obj = form[field_desc["name"]]
                if obj.content_type not in field_desc["type"][i]:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": "Invalid content type",
                            "message": "The content type of the file must be " + field_desc.type + "."
                        })
                else:
                    i += 1
                    if obj.content_type == "application/json":
                        payload = await obj.read()
                        jobData.update(json.loads(payload))
                        jsonParts.add(name)
                    else:
                        jobData[name] = obj
            task_prototype = {
                "route": url,
                "jobData": jobData,
                "binaries": data_in_fields,
            }
            # TODO: change when storage is implemented
            self.logger.info(f"Task prototype: {task_prototype}")

            return {"id": id}

        # Change the function signature with expected types from the api description so that the api doc is correctly generated
        params = []
        for param in data_in_fields:
            params.append(Parameter(param["name"], kind=Parameter.POSITIONAL_ONLY, annotation=UploadFile))
        params.append(Parameter("req", kind=Parameter.POSITIONAL_ONLY, annotation=Request))
        handler.__signature__ = Signature(params)
        app.add_api_route("/" + slug, handler, methods=["POST"], summary=summary,
                          description=description, tags=[name])
        # Force the regeneration of the schema
        app.openapi_schema = None

    def find_many(self, skip: int = 0, limit: int = 100):
        self.logger.debug("Find many services")
        return self.session.exec(select(Service).order_by(desc(Service.created_at)).offset(skip).limit(limit)).all()

    def create(self, service: Service, app: FastAPI):
        self.logger.debug("Creating service")

        self.session.add(service)
        self.session.commit()
        self.session.refresh(service)
        self.logger.debug(f"Created service with id {service.id}")

        self.logger.debug("Adding route...")
        self.add_route(
            app,
            service.id,
            service.name,
            service.slug,
            service.url,
            service.summary,
            service.description,
            service.data_in_fields,
            service.data_out_fields,
        )
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

    def check_service_availability(self, service_slug: str):
        self.logger.info(f"Checking service availability for service {service_slug}")
        # TODO: check if service is available with a ping
        return True

    def instantiate_services(self, app: FastAPI):
        self.logger.info("Instantiating services...")
        services = self.find_many()

        if len(services) == 0:
            self.logger.info("No services in database.")
        else:
            for service in services:
                self.logger.info(f"Instantiating service {service.name}")
                # TODO: check if service is available
                if self.check_service_availability(service.slug):
                    self.add_route(
                        app,
                        service.id,
                        service.name,
                        service.slug,
                        service.url,
                        service.summary,
                        service.description,
                        service.data_in_fields,
                        service.data_out_fields,
                    )
                    self.logger.info(f"Service {service.name} instantiated")
                else:
                    self.logger.warning(f"Service {service.name} is not available")
                    # TODO: remove route
                    # TODO: check if remove or set unavailable
                    self.session.delete(service)

            self.logger.info("Services instantiated.")

    async def check_services_availability(self, app_ref: FastAPI):
        self.logger.info("Checking services availability")
        services = self.find_many()

        if len(services) == 0:
            self.logger.info("No services in database.")
        else:
            for service in services:
                try:
                    if self.check_service_availability(service.slug):
                        # TODO: check if route is already present
                        self.logger.info(f"Service {service.name} is available")
                    else:
                        self.logger.warning(f"Service {service.name} is not available")
                        # TODO: remove route
                        # TODO: check if remove or set unavailable
                        self.session.delete(service)

                except Exception as e:
                    self.logger.error(f"Unable to check {service.name}: {e}")

