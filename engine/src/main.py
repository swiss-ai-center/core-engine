from fastapi import FastAPI, Depends
import config
from pipelines.controller import router as pipelines_router
from services.controller import router as services_router
from stats.controller import router as stats_router
from tasks.controller import router as tasks_router

api_description = """
CSIA-PME API - The **best** API in the world.
"""

app = FastAPI(
    title="CSIA-PME API",
    description=api_description,
    version="0.0.1",
    contact={
        "name": "CSIA-PME",
        "url": "https://github.com/csia-pme/csia-pme",
        "email": None,
    },
    # license_info={
    #     "name": "",
    #     "url": "",
    # },
)

app.include_router(pipelines_router, tags=['Pipelines'])
app.include_router(services_router, tags=['Services'])
app.include_router(stats_router, tags=['Stats'])
app.include_router(tasks_router, tags=['Tasks'])

@app.get("/", tags=['Demo'])
async def root():
    return {"message": "Hello World"}

@app.get("/info", tags=['Demo'])
async def info(settings: config.Settings = Depends(config.get_settings)):
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email,
        "items_per_user": settings.items_per_user,
    }
