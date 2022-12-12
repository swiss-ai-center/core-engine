from fastapi import Depends
from config import Settings, get_settings
from logger import Logger
import asyncio
import math
import os
import aiobotocore
import aiofiles
from datetime import datetime, timedelta


class Storage():
    def __init__(self, logger: Logger = Depends(), settings: Settings = Depends(get_settings)):
        self.logger = logger
        self.aws_access_key_id = settings.aws_access_key_id
        self.aws_secret_access_key = settings.aws_secret_access_key
        self.aws_region = settings.aws_region
        self.s3_host = settings.s3_host
        self.s3_bucket_name = settings.s3_bucket_name
        self.s3_multipart_bytes_per_chunk = settings.s3_multipart_bytes_per_chunk
        self.s3_multiparts_deletation_days_if_transfer_fails = settings.s3_multiparts_deletation_days_if_transfer_fails

        # File object is distributed across coroutines.
        # Let's make sure it doesn't make troubles as a shared resource
        self.file_shared_lock = asyncio.Lock()

    async def __upload_chunk(
            self,
            client,
            file,
            upload_id,
            chunk_number,
            bytes_per_chunk,
            source_size,
            key,
            part_info,
    ):
        offset = chunk_number * bytes_per_chunk
        remaining_bytes = source_size - offset
        bytes_to_read = min([bytes_per_chunk, remaining_bytes])
        part_number = chunk_number + 1

        async with self.file_shared_lock:
            # At this moment the execution returns back to the event loop
            # Another coroutine might make another .seek operation
            # which leads to reading another chunk.
            # That's why we need a lock(asyncio lock) here
            await file.seek(offset)
            chunk = await file.read(bytes_to_read)

        resp = await client.upload_part(
            Bucket=self.s3_bucket_name,
            Body=chunk,
            UploadId=upload_id,
            PartNumber=part_number,
            Key=key
        )

        part_info['Parts'].append(
            {
                'PartNumber': part_number,
                'ETag': resp['ETag']
            }
        )

    async def begin_multipart_upload(
            self,
            source_path,
            s3_destination_folder_path,
    ):
        filename = os.path.basename(source_path)
        key = f'{s3_destination_folder_path}/{filename}'

        session = aiobotocore.get_session()
        async with session.create_client(
                's3',
                endpoint_url=self.s3_host,
                aws_secret_access_key=self.aws_secret_access_key,
                aws_access_key_id=self.aws_access_key_id
        ) as client:

            source_size = os.stat(source_path).st_size
            chunks_count = int(math.ceil(source_size / float(self.s3_multipart_bytes_per_chunk)))
            print('chunks_count: ', chunks_count)

            create_multipart_upload_resp = await client.create_multipart_upload(
                Bucket=self.s3_bucket_name,
                Key=key,
                Expires=datetime.now() + timedelta(days=self.s3_multiparts_deletation_days_if_transfer_failed),
            )

            upload_id = create_multipart_upload_resp['UploadId']

            # We have to keep info about uploaded parts.
            # https://github.com/boto/boto3/issues/50#issuecomment-72079954
            part_info = {
                'Parts': []
            }

            tasks = []
            async with aiofiles.open(source_path, mode='rb') as file:
                for chunk_number in range(chunks_count):
                    tasks.append(
                        self.__upload_chunk(
                            client=client,
                            file=file,
                            chunk_number=chunk_number,
                            bytes_per_chunk=self.s3_multipart_bytes_per_chunk,
                            key=key, upload_id=upload_id,
                            source_size=source_size,
                            part_info=part_info,
                        )
                    )

                await asyncio.gather(*tasks)

            list_parts_resp = await client.list_parts(
                Bucket=self.s3_bucket_name,
                Key=key,
                UploadId=upload_id
            )

            # You have to sort parts in ascending order. 
            # Otherwise api will throw an error
            part_list = sorted(part_info['Parts'], key=lambda k: k['PartNumber'])
            part_info['Parts'] = part_list

            is_finished = len(list_parts_resp['Parts']) == chunks_count

            if is_finished:
                print('Done uploading file')
                await client.complete_multipart_upload(
                    Bucket=self.s3_bucket_name,
                    Key=key,
                    UploadId=upload_id,
                    MultipartUpload=part_info
                )

            else:
                print('Aborted uploading file.')
                await client.abort_multipart_upload(
                    Bucket=self.s3_bucket_name,
                    Key=key,
                    UploadId=upload_id
                )
