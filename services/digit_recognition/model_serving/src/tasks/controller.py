from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from tasks.models import Task

router = APIRouter()


@router.get("/status/{task_id}", summary="Get task status")
async def get_task_status(task_id: str):
    # TODO: get task status
    return JSONResponse(status_code=200, content={"status": "ok"})


@router.post("/compute", summary="Compute task")
async def compute(task: Task, callback_url: str = None):
    # TODO: compute task
    return JSONResponse(status_code=200, content={"id": "task_id"})
