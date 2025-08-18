"""
tongsim.entity.action.impl.locomotion
"""

from dataclasses import dataclass

from tongsim.connection.grpc import AnimCmd
from tongsim.entity.action.base import ActionBase
from tongsim.math.geometry import Vector3


@dataclass(slots=True)
class MoveToLocation(ActionBase):
    """
    动作: 移动至指定目标位置，移动速度较大时会切换为跑步动作，移动速度较小时维持走路动作。

    Attributes:
        loc (Vector3): 目标世界坐标位置。
        speed (float): 移动速度，单位为 cm/s，若为 0 表示使用默认速度。
    """

    loc: Vector3
    speed: float = 0.0

    def validate(self) -> None:
        if not isinstance(self.loc, Vector3):
            raise TypeError(f"loc must be a Vector3, got {type(self.loc)}")
        if not isinstance(self.speed, int | float) or self.speed < 0:
            raise ValueError(f"speed must be a non-negative number, got {self.speed}")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.move_to_location(loc=self.loc, move_speed=self.speed, can_run=False)
        )


@dataclass(slots=True)
class MoveToObject(ActionBase):
    """
    动作: 移动至指定目标，移动速度较大时会切换为跑步动作，移动速度较小时维持走路动作。

    Attributes:
        object_id (str): 目标的 EntityID。
        speed (float): 移动速度，单位为 cm/s，若为 0 表示使用默认速度。
    """

    object_id: str
    speed: float = 0.0

    def validate(self) -> None:
        if not self.object_id:
            raise ValueError("object_id must be specified.")
        if not isinstance(self.speed, int | float) or self.speed < 0:
            raise ValueError("speed must be a non-negative number")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.move_to_object(
                object_id=self.object_id, move_speed=self.speed, can_run=False
            )
        )


@dataclass(slots=True)
class MoveToComponent(ActionBase):
    """
    动作: 移动至指定目标组件，移动速度较大时会切换为跑步动作，移动速度较小时维持走路动作。

    Attributes:
        component_id (str): 目标的 ComponentID。
        speed (float): 移动速度，单位为 cm/s，若为 0 表示使用默认速度。
    """

    component_id: str
    speed: float = 0.0

    def validate(self) -> None:
        if not self.component_id:
            raise ValueError("component_id must be specified.")
        if not isinstance(self.speed, int | float) or self.speed < 0:
            raise ValueError("speed must be a non-negative number")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.move_to_component(
                component_id=self.component_id, move_speed=self.speed, can_run=False
            )
        )


@dataclass(slots=True)
class TurnToLocation(ActionBase):
    """
    动作: 转向目标至指定目标位置。

    Attributes:
        loc (Vector3): 目标世界坐标位置。
    """

    loc: Vector3

    def validate(self) -> None:
        if not isinstance(self.loc, Vector3):
            raise TypeError(f"loc must be a Vector3, got {type(self.loc)}")

    async def execute(self) -> None:
        await self.submit(AnimCmd.turn_around_to_location(loc=self.loc))


@dataclass(slots=True)
class TurnToObject(ActionBase):
    """
    动作: 转向目标至指定目标。

    Attributes:
        object_id (str): 目标的 EntityID。
    """

    object_id: str

    def validate(self) -> None:
        if not self.object_id:
            raise ValueError("object_id must be specified.")

    async def execute(self) -> None:
        await self.submit(AnimCmd.turn_around_to_object(object_id=self.object_id))


@dataclass(slots=True)
class TurnToComponent(ActionBase):
    """
    动作: 转向至指定目标组件。

    Attributes:
        component_id (str): 目标的 ComponentID。
    """

    component_id: str

    def validate(self) -> None:
        if not self.component_id:
            raise ValueError("component_id must be specified.")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.turn_around_to_component(
                component_id=self.component_id,
            )
        )


@dataclass(slots=True)
class TurnInDegree(ActionBase):
    """
    动作: 原地转特定角度。

    Attributes:
        degree (float): 需要原地转的角度。
    """

    degree: float

    def validate(self) -> None:
        pass

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.turn_around_degree(
                degree=self.degree,
            )
        )
