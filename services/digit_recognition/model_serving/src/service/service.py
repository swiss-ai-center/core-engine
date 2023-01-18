from fastapi.encoders import jsonable_encoder
from http_client import HttpClient
from logger.logger import Logger
from fastapi import Depends
from config import Settings, get_settings
from tasks.service import TasksService
from .models import DigitRecognitionService


class ServiceService:
    def __init__(
            self,
            logger: Logger = Depends(),
            settings: Settings = Depends(get_settings),
            http_client: HttpClient = Depends(),
            tasks_service: TasksService = Depends()
    ):
        self.logger = logger
        self.settings = settings
        self.http_client = http_client
        self.logger.set_source(__name__)
        self.tasks_service = tasks_service

    async def announce_service(self):
        """
        Announce the service to the engine
        """
        try:
            entity = jsonable_encoder(DigitRecognitionService())
            self.logger.debug(f'Announcing service: {entity}')
            res = await self.http_client.post(self.settings.engine + "/services", json=entity)
            if res.status_code == 409:
                self.logger.warning(f"Service already exists in the engine")
                self.logger.info(f"Updating service in the engine")
                services = await self.http_client.get(self.settings.engine + "/services")
                service_id = next((service['id'] for service in services.json() if service['slug'] == entity['slug']),
                                  None)
                res_update = await self.http_client.patch(self.settings.engine + f"/services/{service_id}", json=entity)
                if res_update.status_code != 200:
                    self.logger.error(f"Error updating service in the engine: {res_update.text}")
                    return False
                return True
            elif res.status_code != 200:
                self.logger.warning(f"Failed to notify the engine, request returned {str(res.status_code)} {res.text}")
                return False
            self.logger.info("Successfully announced to the engine")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to notify the engine: {str(e)}")
            return False

    def is_full(self):
        """
        Check if the service is full
        """
        return self.tasks_service.is_full()
