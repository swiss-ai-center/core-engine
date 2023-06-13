from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from common.exceptions import NotFoundException, InternalServerErrorException
from common_code.logger.logger import get_logger, Logger
from storage.service import StorageService
from storage.models import FileRead

router = APIRouter()


@router.post(
    "/storage",
    summary="Upload a file to storage",
    response_model=FileRead,
)
async def upload(
    file: UploadFile,
    storage_service: StorageService = Depends(),
):
    try:
        key = await storage_service.upload(file)
    except InternalServerErrorException as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FileRead(key=key)


@router.get(
    "/storage/{key}",
    summary="Download a file from storage",
)
async def download(
    key: str,
    storage_service: StorageService = Depends(),
    logger: Logger = Depends(get_logger),
):
    try:
        # TODO: Can we move this check in the service file?
        # It seems an exception thrown in a generator function is not caught.
        await storage_service.check_if_file_exists(key)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InternalServerErrorException as e:
        logger.error(f"Error while downloading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    headers = {
        'Content-Disposition': f'attachment; filename="{key}"'
    }

    chunks_generator = storage_service.get_file_as_chunks(key)

    return StreamingResponse(
        chunks_generator,
        headers=headers,
    )


@router.delete(
    "/storage/{key}",
    summary="Delete a file from storage",
    responses={
        204: {"detail": "File Removed"},
        500: {"detail": "Internal Server Error"},
    },
    status_code=204
)
async def delete(
        key: str,
        storage_service: StorageService = Depends(),
        logger: Logger = Depends(get_logger),
):
    try:
        await storage_service.check_if_file_exists(key)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InternalServerErrorException as e:
        logger.error(f"Error while downloading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    await storage_service.delete(key)
