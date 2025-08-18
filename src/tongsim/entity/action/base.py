from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from tongsim.connection.grpc.streamer.animation import AnimationStreamer, CommandSpec
from tongsim.core.world_context import WorldContext
from tongsim.logger import get_logger
from tongsim.type.anim import AnimResultInfo

if TYPE_CHECKING:
    from tongsim.entity.ability.impl import AgentActionAbility

_logger = get_logger("animation")


@dataclass
class ActionBase(ABC):
    """
    动作抽象基类。

    每个 Action 将由若干个 Animation 组成，`submit()` 只负责提交，不阻塞等待结果。
    结果收集与异常处理将在 `collect_results()` 中统一完成。

    子类必须实现 `__call__()` 方法，用于描述 Action 的 Animation 组成。
    """

    _anim_ids: list[int] = field(default_factory=list, init=False)
    _streamer: AnimationStreamer | None = field(default=None, init=False)
    _context: WorldContext | None = field(default=None, init=False)
    _action_ability: AgentActionAbility | None = field(default=None, init=False)
    _track_result = False

    @property
    def anim_ids(self):
        return self._anim_ids

    @property
    def streamer(self):
        return self._streamer

    @abstractmethod
    async def execute(self) -> None:
        """
        异步执行动作，将 Animation 提交到 streamer 中，不阻塞等待结果。
        """
        raise NotImplementedError("Subclasses must implement the `execute` method.")

    @abstractmethod
    def validate(self) -> None:
        """
        验证 Action 的输入参数。

        子类可覆盖此方法以实现具体的参数校验逻辑。
        """
        raise NotImplementedError("Subclasses must implement the `validate` method.")

    def initialize(
        self,
        action_ability: AgentActionAbility,
        streamer: AnimationStreamer,
        context: WorldContext,
        track_result: bool,
    ) -> None:
        """
        设置 AnimationStreamer，用于提交动画命令。
        """
        self._streamer = streamer
        self._context = context
        self._track_result = track_result
        self._action_ability = action_ability

    async def submit(self, cmd_spec: CommandSpec) -> None:
        """
        提交单个 Animation 命令，并记录其 command_id。
        """
        if not self._streamer:
            raise RuntimeError("Streamer not set for action.")

        try:
            command_id = await self._streamer.submit(cmd_spec, self._track_result)
            self._anim_ids.append(command_id)
            _logger.debug(
                f"Action {self.__class__.__name__}: Submitted animation command {command_id}"
            )

        except Exception as e:
            tag = getattr(cmd_spec, "tag", "<unknown>")
            _logger.error(f"Error in submitting command {tag}, error_msg: {e}")

    async def wait_any_started(self) -> AnimResultInfo:
        """
        等待本 Action 中任意一个 Animation 的 BEGIN 阶段到达。

        Returns:
            AnimResultInfo: 最先开始的动画信息。
        """
        if not self._streamer:
            raise RuntimeError("Streamer not set for action.")

        return await self._streamer.wait_any_begin(self._anim_ids)

    async def collect_results(
        self, cancel_on_error: bool = False
    ) -> list[AnimResultInfo]:
        """
        收集当前 Action 中所有 Animation 的结果。

        Args:
            cancel_on_error (bool): 若为 True，当任一 Animation 发生错误时立即取消剩余动画。

        Returns:
            List[AnimResultInfo]: 每个 Animation 的执行结果。
        """
        if not self._streamer:
            raise RuntimeError("Streamer not set for action.")

        # TODO:  cancel_on_error

        results: list[AnimResultInfo] = await self._streamer.wait_all_end(
            self._anim_ids
        )
        self._anim_ids.clear()
        return results

    async def _cancel_pending(self) -> None:
        """
        取消当前 Action 内所有未完成的 Animation。
        """
        if not self._streamer:
            raise RuntimeError("Streamer not set for action.")
        # TODO:
        raise NotImplementedError("Cancellation logic is not implemented.")

    async def run(self) -> None:
        """
        统一执行入口。

        - 首先进行参数验证。
        - 然后执行 Animation 提交。
        """
        try:
            self.validate()
            await self.execute()
        except Exception as e:
            _logger.error(f"Action {self.__class__.__name__} execution failed: {e}")
            raise
