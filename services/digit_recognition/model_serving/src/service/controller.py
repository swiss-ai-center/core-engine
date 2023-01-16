from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter()


@router.get("/status", summary="Get service availability")
async def get_availability():
    return Response(status_code=204)
