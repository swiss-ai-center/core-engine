from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from .service import TasksService
from .schemas.task import TaskSchema

router = APIRouter()


@router.get("/tasks/{taskId}", summary="Get results of a task")
async def get_task_result(task_id: str):
    # result = await engine.getResult(task_id)
    result = None
    return JSONResponse(result)


@router.get("/tasks/{taskId}/status", summary="Get the status of a task")
async def get_task_status(taskId: str):
    # return await engine.pollTask(taskId)
    return None


@router.get("/tasks/{taskId}/raw", summary="Get raw pipeline data for a task")
async def get_task_raw(taskId: str):
    # raw = await engine.getJobRaw(taskId)$
    raw = None
    return JSONResponse(raw)


@router.get("/tasks/{taskId}/files/{fileName}", summary="Retrieve a binary result of a task")
async def get_task_result_file(taskId: str, fileName: str):
    # stream = await engine.getResultFile(taskId, fileName)
    stream = None
    return StreamingResponse(stream, media_type="application/octet-stream")


@router.get("/tasks", summary="Find many tasks", description="Find many tasks.", response_model=list[TaskSchema])
async def get_many_tasks(tasks_service: TasksService = Depends()):
    tasks = tasks_service.find_many()

    dtos = []

    for task in tasks:
        taskDto = TaskSchema.toTaskSchema(task)
        dtos.append(taskDto)

    return dtos


@router.post("/tasks", summary="Create a task", description="Create a task.", response_model=TaskSchema)
async def create(tasks_service: TasksService = Depends()):
    task = tasks_service.create()

    dto = TaskSchema.toTaskSchema(task)

    return dto
