import pytest
import asyncio
from timer import Timer


@pytest.mark.asyncio
async def test_timer():
    timer = Timer(
        timeout=0.1,
        callback=lambda: print("test"),  # noqa: T201
        app_ref=None,
    )

    timer.start()
    await asyncio.sleep(0.2)
    timer.stop()
