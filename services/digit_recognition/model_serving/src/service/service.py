from fastapi.encoders import jsonable_encoder
from http_client import HttpClient
from logger import Logger
from fastapi import Depends

import httpx
from .models import DigitRecognitionService
from config import Settings, get_settings


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
        try:
            entity = jsonable_encoder(DigitRecognitionService())
            self.logger.info(f'Announcing service: {entity}')
            res = await self.http_client.post(self.settings.engine + "/services",
                                              json=entity)
            if res.status_code != 200:
                self.logger.warning(f"Failed to notify the engine, request returned {str(res.status_code)} {res.text}")
                return False
            self.logger.info("Successfully notified the engine")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to notify the engine: {str(e)}")
            return False
