"""
tongsim.connection.grpc.streamer.animation

本模块定义了 AnimationStreamer 类，用于管理 Animation 指令的提交与结果收集。
支持 gRPC 双向流的异步通信模式。

"""

import asyncio
import itertools
from collections import OrderedDict
from dataclasses import dataclass
from typing import cast

from google.protobuf.message import Message
from tongsim_api_protocol.basic_pb2 import Component, Subject
from tongsim_api_protocol.component.animation.animation_pb2 import (
    AnimationCommandParams,
    AnimationResult,
    EAnimationCommandStatus,
)
from tongsim_api_protocol.component.animation.animation_pb2_grpc import (
    AnimationServiceStub,
)

from tongsim.connection.grpc.anim_cmd import CommandSpec
from tongsim.connection.grpc.bidi_stream import BidiStream
from tongsim.connection.grpc.core import GrpcConnection
from tongsim.core import AsyncLoop
from tongsim.logger import get_logger
from tongsim.type.anim import AnimResultInfo

_logger = get_logger("animation")

# 模块级别共享一个 animation_id 计数器
_id_counter = itertools.count(1)


@dataclass(slots=True)
class AnimationResultTracker:
    begin_future: asyncio.Future | None = None
    end_future: asyncio.Future | None = None
    begin_result: AnimResultInfo | None = None
    end_result: AnimResultInfo | None = None


class AnimationStreamer:
    """
    AnimationStreamer 负责管理 Animation 的提交与结果收集。
    - 每个 Animation 提交后，将收到两个结果: BEGIN（开始）和 END（结束）。
    - 只有 END 类型的结果会触发 Future，BEGIN 仅用于日志输出。
    """

    def __init__(
        self,
        conn: GrpcConnection,
        async_loop: AsyncLoop,
        subject_id: str,
        component_id: str,
    ):
        self._stream: BidiStream[AnimationCommandParams, AnimationResult] = BidiStream(
            conn.get_stub(AnimationServiceStub).SubScribeAnimation,
            name=f"{subject_id}--AnimationStreamer",
        )
        self._async_loop: AsyncLoop = async_loop
        self._subject_id: str = subject_id
        self._component_id: str = component_id
        self._result_futures: OrderedDict[int, AnimationResultTracker] = OrderedDict()

    async def start(self):
        """启动 streamer 读取循环。"""
        await self._stream.start()
        self._async_loop.spawn(self._read_loop(), name="AnimationStreamer:read_loop")

    async def stop(self):
        await self._stream.aclose()

    async def submit(self, spec: CommandSpec, track: bool = True) -> int:
        """
        提交 Animation 命令，并决定是否追踪结果。

        Args:
            spec (CommandSpec): Animation 命令规范。
            track (bool): 是否追踪此 Animation 的结果，默认 True。

        Returns:
            int: command_id，唯一标识该 Animation。
        """
        command_id = next(_id_counter)

        req = AnimationCommandParams(
            subject=Subject(id=self._subject_id),
            component=Component(id=self._component_id),
            command_code=spec.tag,
            command_id=command_id,
            action_id=command_id,
        )

        # 填充 oneof 参数
        try:
            getattr(req, spec.oneof_field).CopyFrom(spec.oneof_msg)
        except AttributeError as e:
            raise RuntimeError(f"Invalid oneof field: {spec.oneof_field}") from e

        # 填充额外字段
        if spec.extra_fields:
            for key, value in spec.extra_fields.items():
                if isinstance(value, Message):
                    getattr(req, key).CopyFrom(value)
                else:
                    setattr(req, key, value)

        # 仅当 track=True 时，创建 Future
        if track:
            self._result_futures[command_id] = AnimationResultTracker()

        await self._stream.write(req)
        _logger.debug(
            f"Animation {command_id} submitted with tag {spec.tag}, is_tracked: {track}."
        )
        return command_id

    async def wait_begin(self, command_id: int) -> AnimResultInfo:
        """
        等待指定 command_id 对应的 Animation 开始（BEGIN 阶段）。

        Args:
            command_id (int): Animation 的唯一标识符。

        Returns:
            AnimResultInfo: 含有 BEGIN 阶段的执行信息。
        """
        tracker = self._result_futures.get(command_id)
        if not tracker:
            raise RuntimeError(f"No tracker found for command_id {command_id}.")

        # 此处 不执行 try_pop 依赖 TongSim 一定先返回 begin 再返回 end!
        # 如果已经从流中接受到了 result，则直接返回 cache 的result
        if tracker.begin_result:
            result = tracker.begin_result
            tracker.begin_result = None
            return result

        # 否则 创建 future 开始等待
        future = asyncio.get_event_loop().create_future()
        tracker.begin_future = future
        return await future

    async def wait_any_begin(self, command_ids: list[int]) -> AnimResultInfo:
        """
        等待任意一个指定的 Animation 进入 BEGIN 阶段。

        Args:
            command_ids (list[int]): 要监听的 animation ID 列表。

        Returns:
            AnimResultInfo: 最先开始的 animation 的 BEGIN 信息。
        """
        tasks = [asyncio.create_task(self.wait_begin(cmd_id)) for cmd_id in command_ids]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        result = next(task.result() for task in done)
        for task in pending:
            task.cancel()
        return result

    async def wait_end(self, command_id: int) -> AnimResultInfo:
        """
        等待指定 command_id 对应的 Animation 结束（END 或 ERROR 阶段）。

        Args:
            command_id (int): Animation 的唯一标识符。

        Returns:
            AnimResultInfo: 含有 END 或 ERROR 阶段的执行信息。
        """
        tracker = self._result_futures.get(command_id)
        if not tracker:
            raise RuntimeError(f"No tracker found for command_id {command_id}.")

        # 如果已经从流中接受到了 result，则直接返回 cache 的result
        if tracker.end_result:
            result = tracker.end_result
            tracker.end_result = None
            self._try_pop(command_id)
            return result

        # 否则 创建 future 开始等待
        future = asyncio.get_event_loop().create_future()
        tracker.end_future = future
        future.add_done_callback(lambda _: self._try_pop(command_id))
        return await future

    async def wait_all_end(self, command_ids: list[int]) -> list[AnimResultInfo]:
        """
        等待所有指定 Animation 的 END 阶段完成。

        Args:
            command_ids (list[int]): 所有 Animation 的 command_id 列表。

        Returns:
            list[AnimResultInfo]: 每个 Animation 的 END 或 ERROR 结果，顺序与输入一致。
        """
        tasks = [self.wait_end(cmd_id) for cmd_id in command_ids]
        return await asyncio.gather(*tasks)

    def _try_pop(self, command_id: int):
        """
        如果 END 阶段已经被用户获取（或 await 完成），则清理对应的 tracker。
        强依赖 TongSim 一定先返回 begin 再返回 end!
        """
        tracker = self._result_futures.get(command_id)
        if not tracker:
            return

        end_result_handled = tracker.end_result is None
        end_future_handled = (
            tracker.end_future is not None and tracker.end_future.done()
        )

        if end_result_handled or end_future_handled:
            self._result_futures.pop(command_id, None)

    async def _read_loop(self):
        """
        内部读取循环，用于处理 gRPC 流返回的 AnimationResult。
        """
        try:
            async for ret_result in self._stream:
                proto_result = cast(AnimationResult, ret_result)
                command_id = proto_result.command_id
                status = proto_result.animation_command_status

                # 生成结果对象
                result = AnimResultInfo(
                    command_id=command_id,
                    unreal_frame=proto_result.current_frame,
                    error_code=proto_result.error_code,
                    error_animation_code=proto_result.error_animation,
                    status=(
                        "begin" if status == EAnimationCommandStatus.BEGIN else "end"
                    ),
                )

                # 未追踪的 Animation 仅记录日志
                tracker = self._result_futures.get(command_id, None)
                if not tracker:
                    _logger.debug(
                        f"Animation {command_id} is not tracked, ignoring result."
                    )
                    continue

                if status == EAnimationCommandStatus.BEGIN:
                    if tracker.begin_future and not tracker.begin_future.done():
                        tracker.begin_future.set_result(result)
                    else:
                        tracker.begin_result = result
                    _logger.debug(f"Animation {command_id} BEGIN received.")
                else:
                    if proto_result.error_code:
                        result.status = "error"
                        _logger.warning(
                            f"Animation {command_id} error with code {proto_result.error_code}."
                        )
                    if tracker.end_future and not tracker.end_future.done():
                        tracker.end_future.set_result(result)
                    else:
                        tracker.end_result = result
                    _logger.debug(
                        f"Animation {command_id} END received with status: {result.status}"
                    )

        except Exception as e:
            # 在 gRPC 流异常或断开连接时，统一处理未完成的 Future
            _logger.error(f"Exception in read_loop: {e}")
            self._cleanup_futures(exception=e)

        finally:
            # 在 read_loop 正常退出时，确保清理未完成的 Future
            self._cleanup_futures(
                exception=RuntimeError("Streamer read loop terminated unexpectedly.")
            )

    def _cleanup_futures(self, exception: Exception):
        """
        清理未完成的 Future，防止内存泄漏。

        Args:
            exception (Exception): 将设置到未完成 Future 的异常对象。
        """
        for command_id, tracker in self._result_futures.items():
            if tracker.begin_future and not tracker.begin_future.done():
                tracker.begin_future.set_exception(exception)
            if tracker.end_future and not tracker.end_future.done():
                tracker.end_future.set_exception(exception)
            _logger.warning(f"Animation {command_id} terminated due to: {exception}")

        # 清空字典，确保内存释放
        self._result_futures.clear()
