from fastapi.encoders import jsonable_encoder
from http_client import HttpClient
from logger.logger import Logger
from fastapi import Depends
from config import Settings, get_settings
from service.enums import ServiceStatus
from tasks.service import TasksService
from .models import Service


class ServiceService:
    def __init__(
            self,
            logger: Logger = Depends(),
            settings: Settings = Depends(get_settings),
            http_client: HttpClient = Depends(),
            tasks_service: TasksService = Depends(),
    ):
        self.logger = logger
        self.settings = settings
        self.http_client = http_client
        self.tasks_service = tasks_service

        self.logger.set_source(__name__)

    async def announce_service(self, my_service: Service):
        """
        Announce the service to the engine
        """
        try:
            service_json = jsonable_encoder(my_service)

            self.logger.debug(f'Announcing service: {service_json}')
            res = await self.http_client.post(f"{self.settings.engine_url}/services", json=service_json)

            if res.status_code == 409:
                self.logger.warning("Service already exists in the engine")
                self.logger.info("Updating service in the engine")

                service_id = await self.get_service_id(service_json['slug'])

                res_update = await self.http_client.patch(
                    f"{self.settings.engine_url}/services/{service_id}",
                    json=service_json,
                )

                if res_update.status_code != 200:
                    self.logger.error(f"Error updating service in the engine: {res_update.text}")
                    return False
                self.logger.info("Successfully updated service in the engine")
                return True
            elif res.status_code != 200:
                self.logger.warning(f"Failed to notify the engine, request returned {str(res.status_code)} {res.text}")
                return False
            else:
                self.logger.info("Successfully announced to the engine")
                return True
        except Exception as e:
            self.logger.warning(f"Failed to notify the engine: {str(e)}")
            return False

    async def graceful_shutdown(self, my_service: Service):
        """
        Gracefully shutdown the service
        """
        try:
            self.logger.info("Gracefully shutting down service")
            self.logger.info("Stopping tasks service")
            service_id = await self.get_service_id(my_service.slug)
            service_json = jsonable_encoder({"status": ServiceStatus.UNAVAILABLE})
            # TODO: modify to handle multiple engines
            res_update = await self.http_client.patch(f"{self.settings.engine_url}/services/{service_id}",
                                                      json=service_json)
            if res_update.status_code != 200:
                self.logger.error(f"Error updating service in the engine: {res_update.text}")
            else:
                self.logger.info("Successfully updated service in the engine")

        except Exception as e:
            self.logger.error(f"Error updating service in the engine: {str(e)}")
        finally:
            await self.tasks_service.stop()
            self.logger.info("Successfully stopped tasks service")

    def is_full(self):
        """
        Check if the service is full
        """
        return self.tasks_service.is_full()

    async def get_service_id(self, slug):
        """
        Get the service id from the engine
        """
        # TODO Improve this when authentication is set on service side
        services_response = await self.http_client.get(f"{self.settings.engine_url}/services")
        services = services_response.json()

        for service in services:
            if service['slug'] == slug:
                return service['id']

        return None
