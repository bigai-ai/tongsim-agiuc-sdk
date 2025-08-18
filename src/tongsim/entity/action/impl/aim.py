"""
tongsim.entity.action.impl.aim
"""

from dataclasses import dataclass

from tongsim.connection.grpc import AnimCmd
from tongsim.entity.action.base import ActionBase
from tongsim.math.geometry import Vector3
from tongsim.type.anim import AnimCmdHandType


@dataclass(slots=True)
class PointAtLocationWithDuration(ActionBase):
    """
    动作: 指向指定位置，并保持指定时长后取消。

    Attributes:
        loc (Vector3): 指向的目标位置。
        time_duration (float): 指向保持的时长（秒）。若为 0 则立即取消指向。
        which_hand (AnimCmdHandType): 使用的手部，`AnimCmdHandType.LEFT`、`AnimCmdHandType.RIGHT`、`AnimCmdHandType.BOTH`。
    """

    loc: Vector3
    time_duration: float
    which_hand: AnimCmdHandType = AnimCmdHandType.RIGHT

    def validate(self) -> None:
        if not isinstance(self.loc, Vector3):
            raise TypeError(f"loc must be a Vector3, got {type(self.loc)}")

        if not isinstance(self.time_duration, int | float) or self.time_duration < 0:
            raise ValueError("time_duration must be a non-negative number.")

        if not isinstance(self.which_hand, AnimCmdHandType):
            raise ValueError(f"Invalid hand type: {self.which_hand}")

    async def execute(self) -> None:
        # 开始指向
        await self.submit(
            AnimCmd.point_at_location(
                loc=self.loc,
                is_cancel=False,
                is_left_hand=self.which_hand == AnimCmdHandType.LEFT,
            )
        )

        # 保持指定时长
        if self.time_duration > 0:
            await self.submit(AnimCmd.wait_for(time_duration=self.time_duration))

        # 取消指向
        await self.submit(
            AnimCmd.point_at_location(
                loc=self.loc,
                is_cancel=True,
                is_left_hand=self.which_hand == AnimCmdHandType.LEFT,
            )
        )


@dataclass(slots=True)
class PointAtLocation(ActionBase):
    """
    动作: 指向指定位置或取消指向指定位置。

    Attributes:
        loc (Vector3): 指向的目标位置。
        is_cancel (float): 指向指定位置或取消指向指定位置，True表示取消，False表示执行。默认为False。
        which_hand (AnimCmdHandType): 使用的手部，`AnimCmdHandType.LEFT`、`AnimCmdHandType.RIGHT`、`AnimCmdHandType.BOTH`。
    """

    loc: Vector3
    is_cancel: bool = False
    which_hand: AnimCmdHandType = AnimCmdHandType.RIGHT

    def validate(self) -> None:
        if not isinstance(self.loc, Vector3):
            raise TypeError(f"loc must be a Vector3, got {type(self.loc)}")

        if not isinstance(self.is_cancel, bool):
            raise ValueError(f"is_cancel must be a bool, got {type(self.is_cancel)}")

        if not isinstance(self.which_hand, AnimCmdHandType):
            raise ValueError(f"Invalid hand type: {self.which_hand}")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.point_at_location(
                loc=self.loc,
                is_cancel=self.is_cancel,
                is_left_hand=self.which_hand == AnimCmdHandType.LEFT,
            )
        )


@dataclass(slots=True)
class LookAtLocationWithDuration(ActionBase):
    """
    动作: 注视指定位置，并保持指定时长后取消注视。

    Attributes:
        loc (Vector3): 注视的目标位置。
        time_duration (float): 注视保持的时长（秒）。若为 0 则立即取消注视。
    """

    loc: Vector3
    time_duration: float

    def validate(self) -> None:
        if not isinstance(self.loc, Vector3):
            raise TypeError(f"loc must be a Vector3, got {type(self.loc)}")

        if not isinstance(self.time_duration, int | float) or self.time_duration < 0:
            raise ValueError("time_duration must be a non-negative number.")

    async def execute(self) -> None:
        # 开始注视
        await self.submit(
            AnimCmd.look_at_location(
                loc=self.loc,
                is_cancel=False,
            )
        )

        # 保持指定时长
        if self.time_duration > 0:
            await self.submit(AnimCmd.wait_for(time_duration=self.time_duration))

        # 取消注视
        await self.submit(
            AnimCmd.look_at_location(
                loc=self.loc,
                is_cancel=True,
            )
        )


@dataclass(slots=True)
class LookAtLocation(ActionBase):
    """
    动作: 注视指定位置或取消注释指定位置

    Attributes:
        loc (Vector3): 注视的目标位置。
        is_cancel (float): 注视或取消注视，默认为False。
        execute_immediately (bool): 是否立即执行，默认为False
    """

    loc: Vector3
    is_cancel: bool = False
    execute_immediately: bool = False

    def validate(self) -> None:
        if not isinstance(self.loc, Vector3):
            raise TypeError(f"loc must be a Vector3, got {type(self.loc)}")

        if not isinstance(self.is_cancel, bool):
            raise ValueError(f"is_cancel must be a bool, got {type(self.is_cancel)}")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.look_at_location(
                loc=self.loc,
                is_cancel=self.is_cancel,
                execute_immediately=self.execute_immediately,
            )
        )


@dataclass(slots=True)
class LookAtObject(ActionBase):
    """
    动作: 注视指定实体或取消注视。

    Attributes:
        object_id (str): 目标实体的 ID。
        is_cancel (bool): 是否取消注视。默认为 False 表示执行注视。
    """

    object_id: str
    is_cancel: bool = False
    execute_immediately: bool = False

    def validate(self) -> None:
        if not isinstance(self.object_id, str) or not self.object_id:
            raise ValueError("object_id must be a non-empty string.")
        if not isinstance(self.is_cancel, bool):
            raise ValueError("is_cancel must be a bool.")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.look_at_object(
                object_id=self.object_id,
                is_cancel=self.is_cancel,
                execute_immediately=self.execute_immediately,
            )
        )


@dataclass(slots=True)
class LookAtObjectWithDuration(ActionBase):
    """
    动作: 注视指定实体并保持指定时长后取消。

    Attributes:
        object_id (str): 目标实体的 ID。
        time_duration (float): 注视保持的时长（秒）。若为 0 则立即取消。
    """

    object_id: str
    time_duration: float

    def validate(self) -> None:
        if not isinstance(self.object_id, str) or not self.object_id:
            raise ValueError("object_id must be a non-empty string.")
        if not isinstance(self.time_duration, int | float) or self.time_duration < 0:
            raise ValueError("time_duration must be a non-negative number.")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.look_at_object(
                object_id=self.object_id,
                is_cancel=False,
            )
        )
        if self.time_duration > 0:
            await self.submit(AnimCmd.wait_for(time_duration=self.time_duration))
        await self.submit(
            AnimCmd.look_at_object(
                object_id=self.object_id,
                is_cancel=True,
            )
        )


@dataclass(slots=True)
class PointAtObject(ActionBase):
    """
    动作: 指向指定实体或取消指向。

    Attributes:
        object_id (str): 目标实体的 ID。
        is_cancel (bool): 是否取消指向。默认为 False 表示执行指向。
        which_hand (AnimCmdHandType): 使用的手部。
    """

    object_id: str
    is_cancel: bool = False
    which_hand: AnimCmdHandType = AnimCmdHandType.RIGHT

    def validate(self) -> None:
        if not isinstance(self.object_id, str) or not self.object_id:
            raise ValueError("object_id must be a non-empty string.")
        if not isinstance(self.is_cancel, bool):
            raise ValueError("is_cancel must be a bool.")
        if not isinstance(self.which_hand, AnimCmdHandType):
            raise ValueError(f"Invalid hand type: {self.which_hand}")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.point_at_object(
                object_id=self.object_id,
                is_cancel=self.is_cancel,
                is_left_hand=self.which_hand == AnimCmdHandType.LEFT,
            )
        )


@dataclass(slots=True)
class PointAtObjectWithDuration(ActionBase):
    """
    动作: 指向指定实体并保持指定时长后取消。

    Attributes:
        object_id (str): 目标实体的 ID。
        time_duration (float): 指向保持的时长（秒）。若为 0 则立即取消。
        which_hand (AnimCmdHandType): 使用的手部。
    """

    object_id: str
    time_duration: float
    which_hand: AnimCmdHandType = AnimCmdHandType.RIGHT

    def validate(self) -> None:
        if not isinstance(self.object_id, str) or not self.object_id:
            raise ValueError("object_id must be a non-empty string.")
        if not isinstance(self.time_duration, int | float) or self.time_duration < 0:
            raise ValueError("time_duration must be a non-negative number.")
        if not isinstance(self.which_hand, AnimCmdHandType):
            raise ValueError(f"Invalid hand type: {self.which_hand}")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.point_at_object(
                object_id=self.object_id,
                is_cancel=False,
                is_left_hand=self.which_hand == AnimCmdHandType.LEFT,
            )
        )
        if self.time_duration > 0:
            await self.submit(AnimCmd.wait_for(time_duration=self.time_duration))
        await self.submit(
            AnimCmd.point_at_object(
                object_id=self.object_id,
                is_cancel=True,
                is_left_hand=self.which_hand == AnimCmdHandType.LEFT,
            )
        )
