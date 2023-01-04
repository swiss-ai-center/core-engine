from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/ping", summary="Get service availability")
async def get_availability():
    return JSONResponse(status_code=200, content={"status": "ok"})
