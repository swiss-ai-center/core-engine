# Highly inspired by: https://skonik.me/uploading-large-file-to-s3-using-aiobotocore/
from fastapi import Depends
from config import Settings, get_settings
from logger import Logger
from aiobotocore.session import get_session


class StorageService():
    def __init__(self, logger: Logger = Depends(), settings: Settings = Depends(get_settings)):
        self.logger = logger
        self.aws_access_key_id = settings.aws_access_key_id
        self.aws_secret_access_key = settings.aws_secret_access_key
        self.aws_region = settings.aws_region
        self.s3_host = settings.s3_host
        self.s3_bucket = settings.s3_bucket

    async def upload(
            self,
            file,
            key,
    ):
        session = get_session()

        async with session.create_client(
            's3',
            region_name=self.aws_region,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_access_key_id=self.aws_access_key_id,
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
            region_name=self.aws_region,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_access_key_id=self.aws_access_key_id,
            endpoint_url=self.s3_host
        ) as client:
            await client.delete_object(Bucket=self.s3_bucket, Key=key)
