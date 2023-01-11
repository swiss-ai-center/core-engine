from fastapi.encoders import jsonable_encoder
from http_client import HttpClient
from logger import Logger
from fastapi import Depends
from config import Settings, get_settings
from .models import DigitRecognitionService


class ServiceService:
    def __init__(
            self,
            logger: Logger = Depends(),
            settings: Settings = Depends(get_settings),
            http_client: HttpClient = Depends(),
    ):
        self.logger = logger
        self.settings = settings
        self.http_client = http_client
        self.logger.set_source(__name__)

    async def announce_service(self):
        """
        Announce the service to the engine
        """
        try:
            entity = jsonable_encoder(DigitRecognitionService())
            self.logger.info(f'Announcing service: {entity}')
            res = await self.http_client.post(self.settings.engine + "/services", json=entity)
            if res.status_code == 409:
                self.logger.warning(f"Service already exists in the engine")
                return True
            elif res.status_code != 200:
                self.logger.warning(f"Failed to notify the engine, request returned {str(res.status_code)} {res.text}")
                return False
            self.logger.info("Successfully announced to the engine")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to notify the engine: {str(e)}")
            return False
