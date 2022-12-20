import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from uuid import uuid4
from common.exceptions import NotFoundException
from .service import StorageService
from .models import FileRead

router = APIRouter()


@router.post(
    "/storage",
    summary="Upload a file to storage",
    response_model=FileRead,
)
async def create(file: UploadFile, storage_service: StorageService = Depends()):
    original_filename = file.filename
    original_extension = os.path.splitext(original_filename)[1]

    key = f'{uuid4()}{original_extension}'

    try:
        await storage_service.upload(file.file._file, key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FileRead(key=key)


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
