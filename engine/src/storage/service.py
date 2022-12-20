# Highly inspired by: https://skonik.me/uploading-large-file-to-s3-using-aiobotocore/
from fastapi import Depends
from config import Settings, get_settings
from logger import Logger
from aiobotocore.session import get_session
from botocore.exceptions import EndpointConnectionError


class StorageService():
    FAKE_KEY_ID = '0000-0000-0000-0000'

    def __init__(
        self,
        logger: Logger = Depends(),
        settings: Settings = Depends(get_settings),
    ):
        self.logger = logger
        self.logger.set_source(__name__)
        self.s3_access_key_id = settings.s3_access_key_id
        self.s3_secret_access_key = settings.s3_secret_access_key
        self.s3_region = settings.s3_region
        self.s3_host = settings.s3_host
        self.s3_bucket = settings.s3_bucket

    async def check_storage_availability(self):
        self.logger.info("Checking storage availability...")
        session = get_session()

        async with session.create_client(
            's3',
            region_name=self.s3_region,
            aws_secret_access_key=self.s3_secret_access_key,
            aws_access_key_id=self.s3_access_key_id,
            endpoint_url=self.s3_host
        ) as client:
            try:
                # Isn't there a way to check connectivity with the S3 host other than this..?
                await client.get_object(Bucket=self.s3_bucket, Key=self.FAKE_KEY_ID)
            except EndpointConnectionError:
                self.logger.info("Cannot connect to storage.")
                exit(0)
            except Exception:
                self.logger.info("Successfully connected to storage.")

    async def upload(
            self,
            file,
            key,
    ):
        session = get_session()

        async with session.create_client(
            's3',
            region_name=self.s3_region,
            aws_secret_access_key=self.s3_secret_access_key,
            aws_access_key_id=self.s3_access_key_id,
            endpoint_url=self.s3_host
        ) as client:
            await client.put_object(Bucket=self.s3_bucket, Key=key, Body=file)

    async def delete(
            self,
            key,
    ):
        session = get_session()

        async with session.create_client(
            's3',
            region_name=self.s3_region,
            aws_secret_access_key=self.s3_secret_access_key,
            aws_access_key_id=self.s3_access_key_id,
            endpoint_url=self.s3_host
        ) as client:
            await client.delete_object(Bucket=self.s3_bucket, Key=key)
