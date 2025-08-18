import pytest

from tongsim.connection.grpc import UnaryAPI
from tongsim.logger import get_logger

_logger = get_logger("test")


@pytest.mark.grpc
@pytest.mark.asyncio
async def test_unary_api(conn):
    # get fps
    fps = await UnaryAPI.get_fps(conn)
    _logger.info(f"FPS: {fps}")
    assert isinstance(fps, float)
    assert fps > 0.0
