from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from service import ServiceService

router = APIRouter()


@router.get("/status", summary="Get service availability")
async def get_availability(service_service: ServiceService = Depends()):
    if service_service.is_full():
        return JSONResponse(status_code=503, content={"detail": "Service queue is full"})
    return JSONResponse(status_code=200, content={"status": "Service is available"})
