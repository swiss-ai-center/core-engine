from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/status", summary="Get service availability")
async def get_availability():
    return JSONResponse(status_code=200, content={"status": "Service is available"})
