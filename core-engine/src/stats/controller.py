from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder as json_encode

from stats.service import StatsService

router = APIRouter()


@router.get("/stats", summary="Get engine and pipelines statistics")
async def get_stats(stats_service: StatsService = Depends()):
    stats = stats_service.stats()

    return JSONResponse(json_encode(stats))
