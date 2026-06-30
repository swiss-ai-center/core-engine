"""Regression tests for task<->step routing in pipeline execution.

A pipeline execution's tasks and its pipeline's steps are stored in separate
relationships with no guaranteed shared row order. The execution engine must
therefore pair a task to its step through the stable ``pipeline_step_id`` link,
never by list position. When it relied on position, a finished task's produced
files were labelled with the wrong step identifier, routing the wrong data to
the next step (e.g. a face-detection bounding-box JSON delivered where the
blurred image was expected).
"""
from types import SimpleNamespace

import pytest

# Import the model modules in dependency order before pulling individual names, to
# avoid the circular import between services.models and pipeline_steps.models.
import services.models  # noqa: F401,E402 isort:skip
import pipeline_steps.models  # noqa: F401,E402 isort:skip
import pipelines.models  # noqa: F401,E402 isort:skip
import pipeline_executions.models  # noqa: F401,E402 isort:skip
import tasks.models  # noqa: F401,E402 isort:skip

from common_code.logger.logger import get_logger  # noqa: E402
from config import get_settings  # noqa: E402
from pipeline_executions.models import PipelineExecution  # noqa: E402
from pipeline_steps.models import PipelineStep  # noqa: E402
from pipelines.models import Pipeline  # noqa: E402
from services.models import Service  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402
from sqlmodel.pool import StaticPool  # noqa: E402
from tasks.enums import TaskStatus  # noqa: E402
from tasks.models import Task  # noqa: E402
from tasks.service import TasksService  # noqa: E402


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def _ref_map(pipeline_execution: PipelineExecution) -> dict:
    refs = {}
    for f in pipeline_execution.files or []:
        reference = f["reference"] if isinstance(f, dict) else f.reference
        file_key = f["file_key"] if isinstance(f, dict) else f.file_key
        refs[reference] = file_key
    return refs


@pytest.mark.asyncio
async def test_next_step_routing_with_scrambled_task_order(session: Session):
    """Even when tasks are stored in a different order than steps, a finished
    task's output is labelled with its own step and routed to the right next step."""
    face_detection = Service(
        name="face-detection", slug="face-detection", summary="s", description="d", url="http://fd",
        data_in_fields=[{"name": "image", "type": ["image/jpeg"]}],
        data_out_fields=[{"name": "areas", "type": ["application/json"]}],
    )
    image_blur = Service(
        name="image-blur", slug="image-blur", summary="s", description="d", url="http://ib",
        data_in_fields=[{"name": "image", "type": ["image/jpeg"]}, {"name": "areas", "type": ["application/json"]}],
        data_out_fields=[{"name": "image", "type": ["image/jpeg"]}],
    )
    session.add(face_detection)
    session.add(image_blur)
    session.commit()
    session.refresh(face_detection)
    session.refresh(image_blur)

    pipeline = Pipeline(
        name="p", slug="p", summary="s", description="d",
        data_in_fields=[{"name": "image", "type": ["image/jpeg"]}],
        data_out_fields=[
            {"name": "out", "type": ["image/jpeg"], "format_hint": {"pipeline_source": "image-blur.image"}},
        ],
    )
    session.add(pipeline)
    session.commit()
    session.refresh(pipeline)

    # Steps inserted in order [face-detection, image-blur].
    step_fd = PipelineStep(identifier="face-detection", needs=[], inputs=["pipeline.image"],
                           pipeline_id=pipeline.id, service_id=face_detection.id)
    step_ib = PipelineStep(identifier="image-blur", needs=["face-detection"],
                           inputs=["pipeline.image", "face-detection.areas"],
                           pipeline_id=pipeline.id, service_id=image_blur.id)
    session.add(step_fd)
    session.add(step_ib)
    session.commit()
    session.refresh(step_fd)
    session.refresh(step_ib)

    pipeline_execution = PipelineExecution(
        pipeline_id=pipeline.id, files=[{"reference": "pipeline.image", "file_key": "input.jpg"}]
    )
    session.add(pipeline_execution)
    session.commit()
    session.refresh(pipeline_execution)

    # Tasks inserted SCRAMBLED relative to steps: image-blur's task first, face-detection's second.
    task_ib = Task(service_id=image_blur.id, pipeline_step_id=step_ib.id,
                   pipeline_execution_id=pipeline_execution.id, status=TaskStatus.SCHEDULED)
    task_fd = Task(service_id=face_detection.id, pipeline_step_id=step_fd.id,
                   pipeline_execution_id=pipeline_execution.id, status=TaskStatus.FINISHED, data_out=["bbox.json"])
    session.add(task_ib)
    session.add(task_fd)
    session.commit()
    session.refresh(pipeline_execution)
    session.refresh(task_fd)
    session.refresh(task_ib)

    # Sanity check: the order really is scrambled, so a positional join would be wrong.
    assert [t.pipeline_step_id for t in pipeline_execution.tasks] != [s.id for s in pipeline.steps]

    settings = get_settings()

    async def fake_post(url, json=None):
        return SimpleNamespace(status_code=200, text="ok")

    async def noop(*args, **kwargs):
        return None

    tasks_service = TasksService(
        logger=get_logger(settings), session=session,
        http_client=SimpleNamespace(post=fake_post),
        pipeline_executions_service=SimpleNamespace(),
        settings=settings, storage_service=SimpleNamespace(), connection_manager=SimpleNamespace(),
    )
    tasks_service.send_message = noop

    await tasks_service.launch_next_step_in_pipeline(task_fd)

    session.refresh(pipeline_execution)
    refs = _ref_map(pipeline_execution)

    # The finished face-detection output must be labelled with ITS step, not image-blur's.
    assert refs.get("face-detection.areas") == "bbox.json"
    assert "image-blur.image" not in refs

    # image-blur must then receive the image + the bbox via its declared inputs.
    session.refresh(task_ib)
    assert task_ib.status == TaskStatus.PENDING
    assert task_ib.data_in == ["input.jpg", "bbox.json"]
