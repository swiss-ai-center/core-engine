from unittest.mock import MagicMock

# Load model modules in dependency order to avoid their existing circular import.
import services.models  # noqa: F401,E402 isort:skip
import pipeline_steps.models  # noqa: F401,E402 isort:skip
import pipelines.models  # noqa: F401,E402 isort:skip

from pipelines.models import Pipeline, PipelineUpdate  # noqa: E402
from pipelines.service import PipelinesService  # noqa: E402


def test_metadata_update_preserves_slug_steps_and_executions():
    pipeline = Pipeline(
        name="Original title",
        slug="stable-pipeline-slug",
        summary="Original summary",
        description="Original description",
        steps=[],
    )
    session = MagicMock()
    session.get.return_value = pipeline

    service = PipelinesService.__new__(PipelinesService)
    service.session = session
    service.logger = MagicMock()
    service.tasks_service = MagicMock()
    service.pipeline_executions_service = MagicMock()
    service.remove_route = MagicMock()
    service.enable_pipeline = MagicMock()
    app = MagicMock()

    result = service.update(
        app,
        pipeline.id,
        PipelineUpdate(
            name="Updated title",
            summary="Updated summary",
            description="Updated description",
        ),
    )

    assert result is pipeline
    assert pipeline.name == "Updated title"
    assert pipeline.summary == "Updated summary"
    assert pipeline.description == "Updated description"
    assert pipeline.slug == "stable-pipeline-slug"
    assert pipeline.steps == []
    session.exec.assert_not_called()
    service.tasks_service.update.assert_not_called()
    service.pipeline_executions_service.delete.assert_not_called()
    service.remove_route.assert_called_once_with(app, "stable-pipeline-slug")
    service.enable_pipeline.assert_called_once_with(app, pipeline)
