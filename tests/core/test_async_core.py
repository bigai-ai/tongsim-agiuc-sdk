# tests/test_async_core.py

import asyncio
import time
from collections.abc import Generator
from concurrent.futures import CancelledError

import pytest

from tongsim.core import AsyncLoop
from tongsim.logger import get_logger

_logger = get_logger("test")


@pytest.fixture(scope="module")
def async_loop() -> Generator[AsyncLoop, None, None]:
    loop = AsyncLoop(name="testcore-loop")
    loop.start()
    yield loop
    loop.stop()


def test_basic_task_execution(async_loop: AsyncLoop):
    results = []

    async def coro():
        results.append("done")

    fut = async_loop.spawn(coro(), name="test_basic_task_execution task")
    fut.result(timeout=1)

    assert results == ["done"]


def test_multiple_tasks_execution(async_loop: AsyncLoop):
    # 所有任务都是在同一个 AsyncLoop 的事件循环中调度执行, 不会出现并发冲突。
    counter = 0
    task_num = 100

    async def task(index):
        nonlocal counter
        await asyncio.sleep(0.1)
        counter += index

    for i in range(task_num):
        async_loop.spawn(task(i), name=f"test_multiple_tasks_execution task-{i}")

    # 100 个 task 等待 0.1 秒， 则 0.11 秒后一定能够返回
    time.sleep(0.11)
    assert counter == sum(range(task_num))


def test_exception_propagation(async_loop: AsyncLoop):
    counter = 0

    async def bad_task():
        nonlocal counter
        await asyncio.sleep(0.01)
        counter += 1
        raise RuntimeError("bad_task failure")

    async def good_task():
        nonlocal counter
        await asyncio.sleep(0.02)
        counter += 1

    async_loop.spawn(bad_task(), name="bad")
    with pytest.raises(CancelledError):
        async_loop.spawn(good_task(), name="good").result(timeout=1)
    assert (
        counter == 1
    )  # good_task 的 count+=1 因为 bad_task 提前抛出异常，不应该执行！
