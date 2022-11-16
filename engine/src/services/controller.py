from fastapi import APIRouter

router = APIRouter()


@router.get("/services")
async def get_all():
    return [{"service1": "service1"}]
