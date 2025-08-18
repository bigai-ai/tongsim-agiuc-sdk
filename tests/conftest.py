# tests/conftest.py

import logging
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio

from tongsim.connection.grpc.core import GrpcConnection, GrpcLegacyConnection
from tongsim.logger import initialize_logger


def pytest_addoption(parser):
    parser.addoption(
        "--grpc-ip",
        action="store",
        default="",
        help="Base IP for gRPC connections.",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "grpc: mark test as requiring gRPC connection")


def pytest_collection_modifyitems(config, items):
    grpc_ip = config.getoption("--grpc-ip")
    skip_grpc = pytest.mark.skip(reason="Skipped because --grpc-ip not set")

    for item in items:
        if "grpc" in item.keywords and not grpc_ip:
            item.add_marker(skip_grpc)


# 整个测试 session 创建一次
@pytest_asyncio.fixture(scope="session")
async def conn(request) -> AsyncGenerator[GrpcConnection, None]:
    ip = request.config.getoption("--grpc-ip")
    endpoint = f"{ip}:5056"
    conn = GrpcConnection(endpoint)
    yield conn
    await conn.aclose()


# 整个测试 session 创建一次
@pytest_asyncio.fixture(scope="session")
async def conn_legacy(request) -> AsyncGenerator[GrpcConnection, None]:
    ip = request.config.getoption("--grpc-ip")
    endpoint = f"{ip}:50052"
    conn_legacy = GrpcLegacyConnection(endpoint)
    yield conn_legacy
    await conn_legacy.aclose()


@pytest.fixture(autouse=True, scope="module")
def patch_pytest_first_line():
    # 每个测试模块开头输出一个空行,方便查看
    print("\n")  # noqa: T201


@pytest.fixture(autouse=True, scope="session")
def setup_logging():
    initialize_logger(level=logging.INFO, log_to_file=False)
