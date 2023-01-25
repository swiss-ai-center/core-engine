from fastapi import Depends
from logger.logger import Logger, get_logger
from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from uuid import uuid4


class StorageService:
    def __init__(
            self,
            logger: Logger = Depends(get_logger),
    ):
        self.logger = logger
        self.logger.set_source(__name__)

    async def upload(
            self,
            upload_file: bytes,
            file_extension_with_dot: str,
            region_name: str,
            secret_access_key: str,
            access_key_id: str,
            endpoint_url: str,
            bucket: str,
    ):
        """
        Uploads a file to the storage service
        :param upload_file: The file to upload (bytes)
        :param file_extension: The file extension (with the dot)
        :param region_name: The region name of the S3 server
        :param secret_access_key: The secret access key of the S3 server
        :param access_key_id: The access key id of the S3 server
        :param endpoint_url: The endpoint url of the S3 server
        :param bucket: The bucket name on the S3 server
        """
        key = f"{uuid4()}{file_extension_with_dot}"
        session = get_session()

        try:
            async with session.create_client(
                    's3',
                    region_name=region_name,
                    aws_secret_access_key=secret_access_key,
                    aws_access_key_id=access_key_id,
                    endpoint_url=endpoint_url
            ) as client:
                await client.put_object(Bucket=bucket, Key=key, Body=upload_file)

            return key
        except ClientError as e:
            self.logger.error(f"Error uploading file: {e}")
            return None

    async def get_file(
            self,
            key: str,
            region_name: str,
            secret_access_key: str,
            access_key_id: str,
            endpoint_url: str,
            bucket: str,
    ):
        """
        Gets a file from the storage service
        :param key: The key of the file to retrieve
        :param region_name: The region name of the S3 server
        :param secret_access_key: The secret access key of the S3 server
        :param access_key_id: The access key id of the S3 server
        :param endpoint_url: The endpoint url of the S3 server
        :param bucket: The bucket name on the S3 server
        :return: The file as bytes
        """
        session = get_session()

        try:
            async with session.create_client(
                    's3',
                    region_name=region_name,
                    aws_secret_access_key=secret_access_key,
                    aws_access_key_id=access_key_id,
                    endpoint_url=endpoint_url
            ) as client:
                response = await client.get_object(Bucket=bucket, Key=key)

                async with response['Body'] as stream:
                    file = await stream.read()
                    return file
        except ClientError as e:
            self.logger.error(f"Error getting file: {e}")
            return None

    async def delete(
            self,
            key,
            region_name,
            secret_access_key,
            access_key_id,
            endpoint_url,
            bucket,
    ):
        """
        Deletes a file from the storage service
        :param key: The key of the file to retrieve
        :param region_name: The region name of the S3 server
        :param secret_access_key: The secret access key of the S3 server
        :param access_key_id: The access key id of the S3 server
        :param endpoint_url: The endpoint url of the S3 server
        :param bucket: The bucket name on the S3 server
        """
        session = get_session()

        try:
            async with session.create_client(
                    's3',
                    region_name=region_name,
                    aws_secret_access_key=secret_access_key,
                    aws_access_key_id=access_key_id,
                    endpoint_url=endpoint_url
            ) as client:
                await client.delete_object(Bucket=bucket, Key=key)
        except ClientError as e:
            self.logger.error(f"Error deleting file: {e}")
