"""
tongsim.entity.action.impl.input

封装 Agent 实时运动控制逻辑
"""

from dataclasses import dataclass

from tongsim import Vector2
from tongsim.connection.grpc import AnimCmd
from tongsim.entity.action.base import ActionBase


# ====== SWITCH INPUT  ======
@dataclass(slots=True)
class SwitchInputAnimation(ActionBase):
    """
    动作: 启动或者关闭输入控制器。

    Attributes:
        is_enable (bool): 是否启动控制器。
    """

    is_enable: bool = False

    def validate(self) -> None:
        if not isinstance(self.is_enable, bool):
            raise TypeError("is_close_input must be a bool.")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.switch_input_animation(is_close_input=not self.is_enable)
        )


# ====== SWITCH INPUT  ======
@dataclass(slots=True)
class InputAnimation(ActionBase):
    """
    动作: 输入动作（Input Animation）。

    该动作用于控制角色的输入行为，比如移动方向、是否冲刺、角速度、跳跃与下蹲等。
    所有参数均为可选，若不设置，则不影响对应的输入状态。

    Attributes:
        move_vec (Vector2 | None): 是否有移动向量的输入，x表示左右移动， y表示前后移动，范围[-1, 1]，None 表示未设置。
        angular_speed (float | None): 角速度，表示旋转速率，单位为度/秒，None 表示不设置。
        sprint (bool | None): 是否冲刺，True 表示冲刺，False 表示正常移动，None 表示未设置。
        jump (bool | None): 是否跳跃，True 表示跳跃，False 表示不跳，None 表示未设置。
        crouch (bool | None): 是否下蹲，True 表示下蹲，False 表示站立，None 表示未设置。
    """

    move_vec: Vector2 | None = None
    angular_speed: float | None = None
    sprint: bool | None = None
    jump: bool | None = None
    crouch: bool | None = None

    def validate(self) -> None:
        if self.move_vec is not None and not isinstance(self.move_vec, Vector2):
            raise ValueError("move_vec must be a Vector2 or None.")

        if self.sprint is not None and not isinstance(self.sprint, bool):
            raise ValueError("sprint must be a boolean or None.")

        if self.jump is not None and not isinstance(self.jump, bool):
            raise ValueError("jump must be a boolean or None.")

        if self.crouch is not None and not isinstance(self.crouch, bool):
            raise ValueError("crouch must be a boolean or None.")

        if self.angular_speed is not None:
            if not isinstance(self.angular_speed, int | float):
                raise ValueError("angular_speed must be a float or None.")
            if not -360.0 <= self.angular_speed <= 360.0:
                raise ValueError("angular_speed must be in [-360.0, 360.0]")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.input_action(
                move_vec=self.move_vec,
                sprint=self.sprint,
                angular_speed=self.angular_speed,
                jump=self.jump,
                crouch=self.crouch,
            )
        )
