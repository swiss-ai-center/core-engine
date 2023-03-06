from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from ..common.exceptions import NotFoundException
from ..common.exceptions import QueueFullException
from .models import ServiceTask
from .service import TasksService
from uuid import UUID

router = APIRouter()


@router.get("/tasks/{task_id}/status", summary="Get task status")
async def get_task_status(task_id: UUID, tasks_service: TasksService = Depends()):
    try:
        status = await tasks_service.get_task_status(task_id)
        return JSONResponse(status_code=200, content={"status": status})
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/compute", summary="Compute task")
async def compute(request: Request, task: ServiceTask, tasks_service: TasksService = Depends()):
    try:
        await tasks_service.add_task(task)
        return JSONResponse(status_code=200, content={"status": "Task added to the queue"})
    except QueueFullException as e:
        raise HTTPException(status_code=503, detail=str(e))
