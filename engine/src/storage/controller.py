from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from common.exceptions import NotFoundException
from logger.logger import get_logger, Logger
from .service import StorageService
from .models import FileRead

router = APIRouter()


@router.post(
    "/storage",
    summary="Upload a file to storage",
    response_model=FileRead,
)
async def upload(file: UploadFile, storage_service: StorageService = Depends()):
    key = None

    try:
        key = await storage_service.upload(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FileRead(key=key)


@router.get(
    "/storage/{key}",
    summary="Download a file from storage",
)
async def download(key: str, storage_service: StorageService = Depends(), logger: Logger = Depends(get_logger)):
    try:
        headers = {
            'Content-Disposition': f'attachment; filename="{key}"'
        }
        return StreamingResponse(
            storage_service.get_file_as_chunks(key),
            headers=headers,
        )
    except Exception as e:
        logger.error(f"Error while downloading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
        services_service: StorageService = Depends(),
):
    try:
        await services_service.delete(key)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
