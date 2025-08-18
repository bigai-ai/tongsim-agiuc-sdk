"""
tongsim.entity.action.impl.gesture

封装 Gesture 动作，包括 WaveHand, RaiseHand, NodHead, ShakeHead, EatOrDrink 及其 WithDuration 版本。
"""

from dataclasses import dataclass

from tongsim.connection.grpc import AnimCmd
from tongsim.entity.action.base import ActionBase
from tongsim.type.anim import AnimCmdHandType


@dataclass(slots=True)
class IdleGesture(ActionBase):
    """
    恢复为默认动作（Idle）。

    该动作用于重置当前动画状态，将角色恢复到默认姿态。
    """

    def validate(self) -> None:
        pass

    async def execute(self) -> None:
        await self.submit(AnimCmd.idle_gesture())


@dataclass(slots=True)
class WaveHand(ActionBase):
    """
    动作: 挥手。

    Attributes:
        which_hand (AnimCmdHandType): 指定挥手的手部，可选值为 `AnimCmdHandType.LEFT`、`AnimCmdHandType.RIGHT`、`AnimCmdHandType.BOTH`。
    """

    which_hand: AnimCmdHandType

    def validate(self) -> None:
        if not isinstance(self.which_hand, AnimCmdHandType):
            raise ValueError(f"Invalid hand type: {self.which_hand}")

    async def execute(self) -> None:
        await self.submit(AnimCmd.wave_hand(which_hand=self.which_hand))


@dataclass(slots=True)
class WaveHandWithDuration(ActionBase):
    """
    动作: 挥手并保持指定时长后恢复为 Idle。

    Attributes:
        which_hand (AnimCmdHandType): 指定挥手的手部。
        duration (float): 持续时间（秒）。0 表示立即恢复。
    """

    which_hand: AnimCmdHandType
    duration: float = 0.0

    def validate(self) -> None:
        if not isinstance(self.which_hand, AnimCmdHandType):
            raise ValueError(f"Invalid hand type: {self.which_hand}")
        if not isinstance(self.duration, int | float) or self.duration < 0:
            raise ValueError("Duration must be a non-negative number.")

    async def execute(self) -> None:
        await self.submit(AnimCmd.wave_hand(which_hand=self.which_hand))

        if self.duration > 0:
            await self.submit(AnimCmd.wait_for(time_duration=self.duration))

        await self.submit(AnimCmd.idle_gesture())


@dataclass(slots=True)
class RaiseHand(ActionBase):
    """
    动作: 举手。

    Attributes:
        which_hand (AnimCmdHandType): 指定举手的手部。
    """

    which_hand: AnimCmdHandType

    def validate(self) -> None:
        if not isinstance(self.which_hand, AnimCmdHandType):
            raise ValueError(f"Invalid hand type: {self.which_hand}")

    async def execute(self) -> None:
        await self.submit(AnimCmd.raise_hand(which_hand=self.which_hand))


@dataclass(slots=True)
class RaiseHandWithDuration(ActionBase):
    """
    动作: 举手并保持指定时长后恢复为 Idle。

    Attributes:
        which_hand (AnimCmdHandType): 指定举手的手部。
        duration (float): 持续时间（秒）。0 表示立即恢复。
    """

    which_hand: AnimCmdHandType
    duration: float = 0.0

    def validate(self) -> None:
        if not isinstance(self.which_hand, AnimCmdHandType):
            raise ValueError(f"Invalid hand type: {self.which_hand}")
        if not isinstance(self.duration, int | float) or self.duration < 0:
            raise ValueError("Duration must be a non-negative number.")

    async def execute(self) -> None:
        await self.submit(AnimCmd.raise_hand(which_hand=self.which_hand))

        if self.duration > 0:
            await self.submit(AnimCmd.wait_for(time_duration=self.duration))

        await self.submit(AnimCmd.idle_gesture())


@dataclass(slots=True)
class NodHead(ActionBase):
    """
    动作: 点头。
    """

    def validate(self) -> None:
        pass

    async def execute(self) -> None:
        await self.submit(AnimCmd.nod_head())


@dataclass(slots=True)
class NodHeadWithDuration(ActionBase):
    """
    动作: 点头并保持指定时长后恢复为 Idle。

    Attributes:
        duration (float): 持续时间（秒）。0 表示立即恢复。
    """

    duration: float = 0.0

    def validate(self) -> None:
        if not isinstance(self.duration, int | float) or self.duration < 0:
            raise ValueError("Duration must be a non-negative number.")

    async def execute(self) -> None:
        await self.submit(AnimCmd.nod_head())

        if self.duration > 0:
            await self.submit(AnimCmd.wait_for(time_duration=self.duration))

        await self.submit(AnimCmd.idle_gesture())


@dataclass(slots=True)
class ShakeHead(ActionBase):
    """
    动作: 摇头。
    """

    def validate(self) -> None:
        pass

    async def execute(self) -> None:
        await self.submit(AnimCmd.shake_head())


@dataclass(slots=True)
class ShakeHeadWithDuration(ActionBase):
    """
    动作: 摇头并保持指定时长后恢复为 Idle。

    Attributes:
        duration (float): 持续时间（秒）。0 表示立即恢复。
    """

    duration: float = 0.0

    def validate(self) -> None:
        if not isinstance(self.duration, int | float) or self.duration < 0:
            raise ValueError("Duration must be a non-negative number.")

    async def execute(self) -> None:
        await self.submit(AnimCmd.shake_head())

        if self.duration > 0:
            await self.submit(AnimCmd.wait_for(time_duration=self.duration))

        await self.submit(AnimCmd.idle_gesture())


@dataclass(slots=True)
class EatOrDrink(ActionBase):
    """
    动作: 吃喝动作。

    Attributes:
        which_hand (AnimCmdHandType): 指定举手的手部。
    """

    which_hand: AnimCmdHandType

    def validate(self) -> None:
        if not isinstance(self.which_hand, AnimCmdHandType):
            raise ValueError(f"Invalid hand type: {self.which_hand}")
        pass

    async def execute(self) -> None:
        await self.submit(AnimCmd.eat_or_drink(self.which_hand))


@dataclass(slots=True)
class RompPlay(ActionBase):
    """
    动作: 把玩当前手上的物体（需要手上有物体），若不通过 IdleGesture 取消，会一直持续把玩的动作。

    Attributes:
        which_hand (AnimCmdHandType): 指定用哪知手。 不可使用 BOTH 同时双手。
        decrease_boredom (float): 做完这个动作可以减少 agent 多少的无聊值
    """

    which_hand: AnimCmdHandType
    decrease_boredom: float = 0.0

    def validate(self) -> None:
        # hand type
        if not isinstance(self.which_hand, AnimCmdHandType):
            raise TypeError(
                f"which_hand must be AnimCmdHandType, got {type(self.which_hand)}"
            )
        if self.which_hand == AnimCmdHandType.BOTH:
            raise ValueError("RompPlay does not support BOTH hands.")

        # decrease_boredom
        if not isinstance(self.decrease_boredom, int | float):
            raise TypeError(
                f"decrease_boredom must be int or float, got {type(self.decrease_boredom)}"
            )

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.romp_play(
                which_hand=self.which_hand, decrease_boredom=self.decrease_boredom
            )
        )


@dataclass(slots=True)
class RompPlayWithDuration(ActionBase):
    """
    动作: 把玩当前手上的物体并保持指定时长后恢复为 Idle。

    Attributes:
        which_hand (AnimCmdHandType): 指定用哪只手。不可使用 BOTH 同时双手。
        decrease_boredom (float): 做完这个动作可以减少 agent 多少的无聊值。
        duration (float): 持续时间（秒）。0 表示立即恢复 Idle。
    """

    which_hand: AnimCmdHandType
    decrease_boredom: float = 0.0
    duration: float = 0.0

    def validate(self) -> None:
        # hand type
        if not isinstance(self.which_hand, AnimCmdHandType):
            raise TypeError(
                f"which_hand must be AnimCmdHandType, got {type(self.which_hand)}"
            )
        if self.which_hand == AnimCmdHandType.BOTH:
            raise ValueError("RompPlay does not support BOTH hands.")

        # decrease_boredom
        if not isinstance(self.decrease_boredom, int | float):
            raise TypeError(
                f"decrease_boredom must be int or float, got {type(self.decrease_boredom)}"
            )

        # duration
        if not isinstance(self.duration, int | float):
            raise TypeError(f"duration must be int or float, got {type(self.duration)}")
        if self.duration < 0:
            raise ValueError("duration must be non-negative.")

    async def execute(self) -> None:
        # 开始把玩
        await self.submit(
            AnimCmd.romp_play(
                which_hand=self.which_hand, decrease_boredom=self.decrease_boredom
            )
        )

        # 等待指定时长
        if self.duration > 0:
            await self.submit(AnimCmd.wait_for(time_duration=self.duration))

        # 恢复 Idle
        await self.submit(AnimCmd.idle_gesture())
