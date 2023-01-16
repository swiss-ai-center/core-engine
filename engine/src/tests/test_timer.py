import pytest
import asyncio
from timer import Timer


@pytest.mark.asyncio
async def test_timer():
    testing_timer = Timer(
        timeout=0.1,
        callback=lambda: print("test"),
        app_ref=None,
    )

    testing_timer.start()
    await asyncio.sleep(0.2)
    testing_timer.stop()
