import os
from fastapi import Depends, UploadFile
from config import Settings, get_settings
from common.exceptions import NotFoundException, InternalServerErrorException
from common_code.logger.logger import Logger, get_logger
from aiobotocore.session import get_session
from botocore.exceptions import EndpointConnectionError, ClientError
from uuid import uuid4


class StorageService:
    FAKE_KEY_ID = '0000-0000-0000-0000'

    def __init__(
            self,
            logger: Logger = Depends(get_logger),
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
                # Isn't there a way to check connectivity with the S3 host other than this?
                await client.get_object(Bucket=self.s3_bucket, Key=self.FAKE_KEY_ID)
            except EndpointConnectionError:
                self.logger.info("Cannot connect to storage.")
                exit(1)
            except ClientError:
                self.logger.info("Successfully connected to storage.")

    async def upload(
            self,
            upload_file: UploadFile,
    ):
        try:
            original_filename = upload_file.filename
            original_extension = os.path.splitext(original_filename)[1]

            key = f"{uuid4()}{original_extension}"
            file = await upload_file.read()

            session = get_session()

            async with session.create_client(
                    's3',
                    region_name=self.s3_region,
                    aws_secret_access_key=self.s3_secret_access_key,
                    aws_access_key_id=self.s3_access_key_id,
                    endpoint_url=self.s3_host
            ) as client:
                await client.put_object(Bucket=self.s3_bucket, Key=key, Body=file)

            return key
        except ClientError as e:
            self.logger.error(f"Error uploading file: {e}")
            raise InternalServerErrorException("File Cannot Be Uploaded")

    async def check_if_file_exists(self, key):
        session = get_session()

        async with session.create_client(
            's3',
            region_name=self.s3_region,
            aws_secret_access_key=self.s3_secret_access_key,
            aws_access_key_id=self.s3_access_key_id,
            endpoint_url=self.s3_host
        ) as client:
            try:
                await client.get_object_acl(Bucket=self.s3_bucket, Key=key)
            except ClientError as e:
                self.logger.error(f"Error getting file: {e}")
                if e.response['Error']['Code'] == 'NoSuchKey':
                    raise NotFoundException("File Not Found")
                raise InternalServerErrorException("File Cannot Be Checked")
            finally:
                await client.close()

    async def get_file_as_bytes(
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
            response = await client.get_object(Bucket=self.s3_bucket, Key=key)

            async with response['Body'] as stream:
                file = await stream.read()
                return file

    async def get_file_as_chunks(
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
            response = await client.get_object(Bucket=self.s3_bucket, Key=key)

            async for chunk in response['Body']:
                yield chunk

    async def delete(
            self,
            key,
    ):
        try:
            session = get_session()

            async with session.create_client(
                    's3',
                    region_name=self.s3_region,
                    aws_secret_access_key=self.s3_secret_access_key,
                    aws_access_key_id=self.s3_access_key_id,
                    endpoint_url=self.s3_host
            ) as client:
                await client.delete_object(Bucket=self.s3_bucket, Key=key)
        except ClientError as e:
            self.logger.error(f"Error deleting file: {e}")
            raise e
