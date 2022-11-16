from fastapi import APIRouter

router = APIRouter()


@router.get("/pipelines")
async def get_all():
    return [{"pipeline1": "pipeline2"}]
