"""
core.async_loop

本模块定义了 AsyncLoop 类，每个 AsyncLoop 对象封装一个独立线程中的 asyncio 事件循环, 用于将异步任务封装在单个线程内运行。

核心:
1、将一个虚拟环境输入（基于Connection） 相关的所有协程派发到同一个线程（AsyncLoop 维护）上来降低并发安全的问题
    （注意: 在一个Loop内的协程 仍然可能存在并发安全问题）
2、性能出现瓶颈时，考虑把计算密集性的处理逻辑 offload 到专用的计算线程池来解决。
"""

import asyncio
import contextlib
import threading
from collections.abc import Awaitable
from concurrent.futures import Future
from concurrent.futures import TimeoutError as FutureTimeoutError
from typing import Any

from tongsim.logger import get_logger

_logger = get_logger("core")


class AsyncLoop:
    """
    AsyncLoop 管理一个独立线程中的 asyncio 事件循环和永久 TaskGroup。

    特性:
    - 独立后台线程，常驻 EventLoop
    - 基于 asyncio.TaskGroup 管理所有业务任务
    """

    def __init__(self, name: str = "AsyncLoop") -> None:
        """
        初始化 AsyncLoop。

        Args:
            name: 线程和日志标识名，便于调试多个 Loop 实例。
        """
        self._name = name
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._group_ready = threading.Event()
        self._main_task: asyncio.Task[Any] | None = None
        self._task_group: asyncio.TaskGroup | None = None
        self._business_tasks: set[asyncio.Task[Any]] = (
            set()
        )  # 记录业务 spawn 出来的 task

    @property
    def thread(self) -> threading.Thread:
        return self._thread

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    @property
    def name(self) -> str:
        return self._name

    def start(self, timeout: float = 1.0) -> None:
        """
        启动 AsyncLoop 后台线程和事件循环。

        Args:
            timeout: 等待 loop 和 task group 启动的最长秒数。
        Raises:
            RuntimeError: 如果 loop 未能在指定时间内启动。
        """
        if self.is_running():
            raise RuntimeError(f"[AsyncLoop {self._name}] already running.")

        self._thread = threading.Thread(target=self._run, name=self._name, daemon=True)
        self._thread.start()

        if not self._group_ready.wait(timeout):
            raise RuntimeError(f"[AsyncLoop {self._name}] timeout starting event loop.")

        _logger.debug(f"[AsyncLoop {self._name}] started.")

    def _run(self) -> None:
        """后台线程入口: 初始化事件循环和主任务。"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)  # 将事件循环绑定到当前线程
        self._main_task = self._loop.create_task(self._main(), name="__main_task__")
        try:
            self._loop.run_forever()
        finally:
            self._loop.close()
            _logger.debug(f"[AsyncLoop {self._name}] loop closed.")

    async def _main(self) -> None:
        """
        主协程，在 TaskGroup 上下文中挂起，直至被取消。
        """
        try:
            async with asyncio.TaskGroup() as tg:
                self._task_group = tg
                self._group_ready.set()
                await asyncio.Future()  # 永久挂起，靠 cancel 推出
        except asyncio.CancelledError:
            _logger.debug(
                f"[AsyncLoop {self._name}] main task cancelled; shutting down TaskGroup."
            )
        finally:
            assert self._loop is not None
            self._loop.call_soon_threadsafe(self._loop.stop)

    def spawn(self, coro: Awaitable[Any], name: str = "") -> Future[Any]:
        """
        在 TaskGroup 中提交一个新的异步任务。

        Args:
            coro: 待执行的 coroutine。
            name: 可选，任务名称，用于日志追踪。

        Returns:
            Future，可通过 .result(timeout) 获取 coroutine 返回值或异常。
        """
        if not (self._loop and self._task_group):
            raise RuntimeError(f"[AsyncLoop {self._name}] not started.")

        outer: Future[Any] = Future()

        def _schedule() -> None:
            task: asyncio.Task[Any] = self._task_group.create_task(coro, name=name)
            self._business_tasks.add(task)

            def _on_done(t: asyncio.Task[Any]) -> None:
                self._business_tasks.discard(t)
                if t.cancelled():
                    outer.cancel()
                else:
                    exc = t.exception()
                    if exc:
                        _logger.exception(
                            f"[AsyncLoop {self._name}] Task {name!r} raised: {exc}"
                        )
                        outer.set_exception(exc)
                        # 业务异常直接取消整个主 TaskGroup
                        assert self._main_task is not None
                        self._main_task.cancel()
                    else:
                        outer.set_result(t.result())

            task.add_done_callback(_on_done)

        self._loop.call_soon_threadsafe(_schedule)
        return outer

    def cancel_tasks(self, timeout: float) -> None:
        """
        取消所有业务协程任务（spawn 出来的 task，不包括主协程）。

        Args:
            timeout: 最长等待取消完成的秒数。
        """
        if not self.is_running():
            return

        future = asyncio.run_coroutine_threadsafe(self._cancel_tasks_seq(), self._loop)
        try:
            future.result(timeout)
        except FutureTimeoutError:
            _logger.warning(f"[AsyncLoop {self._name}] cancel_tasks timeout.")

    async def _cancel_tasks_seq(self) -> None:
        """
        在 loop 线程中取消所有已 spawn 的业务任务。
        """
        _logger.debug(
            f"[AsyncLoop {self._name}] cancelling {len(self._business_tasks)} business task(s)."
        )
        if not self._business_tasks:
            return

        tasks = list(self._business_tasks)
        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)
        self._business_tasks.clear()

    def stop(self, timeout: float = 5.0) -> None:
        """
        完全停止 AsyncLoop:
        取消所有业务任务 -> 取消主 task -> 停止 loop -> join 线程。

        Args:
            timeout: 等待整个关闭过程的最长秒数。
        """
        if not self.is_running():
            return

        # 取消主协程，TaskGroup 会自动取消所有子任务
        assert self._main_task is not None and self._loop is not None
        self._loop.call_soon_threadsafe(self._main_task.cancel)

        self._thread.join(timeout)
        if self._thread.is_alive():
            _logger.warning(f"AsyncLoop '{self._name}' did not exit cleanly.")
        self._thread = None

    def is_running(self) -> bool:
        """
        判断 AsyncLoop 是否仍在运行。

        Returns:
            True if loop thread alive, else False.
        """
        return bool(self._thread and self._thread.is_alive())

    def log_task_list(self) -> None:
        """
        打印当前 loop 内所有未完成的任务信息，便于调试。
        """
        if not (self._loop and self._task_group):
            return
        task_list = asyncio.all_tasks(self._loop)
        _logger.warning(f"[AsyncLoop {self._name}] {len(task_list)} active task(s):")
        for task in task_list:
            state = (
                "cancelled"
                if task.cancelled()
                else "done" if task.done() else "pending"
            )
            detail = ""
            if task.done() and (exc := task.exception()):
                detail = f"  exception: {type(exc).__name__}: {exc}"
            coro = task.get_coro()
            _logger.warning(
                f"  - {task.get_name()} [{state}]{detail} | coro={coro.__name__ if hasattr(coro, '__name__') else coro}"
            )

    def __del__(self) -> None:
        """析构时自动释放资源。"""
        _logger.debug(f"[AsyncLoop {self._name}] __del__ called, attempting cleanup.")
        with contextlib.suppress(Exception):
            self.stop()
