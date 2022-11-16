from fastapi import APIRouter

router = APIRouter()


@router.get("/stats")
async def get_all():
    return [{"stat1": "value1"}]
