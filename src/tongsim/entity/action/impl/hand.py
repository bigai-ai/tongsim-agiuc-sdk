"""
tongsim.entity.action.impl.hand

封装 Agent 的手部动作
"""

from dataclasses import dataclass

from tongsim.connection.grpc import AnimCmd
from tongsim.entity.action.base import ActionBase
from tongsim.math.geometry import Quaternion, Vector3
from tongsim.type.anim import AnimCmdHandType

# ====== TAKE OBJECT ======


@dataclass(slots=True)
class TakeObject(ActionBase):
    """
    动作: 拿起物体。

    Attributes:
        which_hand (AnimCmdHandType): 使用的手部。
        object_id (str): 目标物体 ID。
        use_socket (bool): 是否使用 socket，默认 False。
        force_grab (bool): 是否强制抓取，默认 False。
        is_reach_from_front (bool): 是否从前方伸手，默认 False。
        auto_offset (bool): 是否自动调整到物体表面，默认 False。
        container_id (str | None): 容器 ID（用于优化动作表现），可选。
    """

    which_hand: AnimCmdHandType
    object_id: str
    use_socket: bool = False
    force_grab: bool = False
    is_reach_from_front: bool = False
    auto_offset: bool = False
    container_id: str | None = None

    def validate(self) -> None:
        if not self.object_id:
            raise ValueError("object_id must be specified.")
        if not isinstance(self.which_hand, AnimCmdHandType):
            raise ValueError(f"Invalid hand type: {self.which_hand}")

    async def execute(self) -> None:
        # 1. 伸手
        await self.submit(
            AnimCmd.hand_reach_to_object(
                which_hand=self.which_hand,
                object_id=self.object_id,
                is_reach_from_front=self.is_reach_from_front,
                auto_offset=self.auto_offset,
                use_socket=self.use_socket,
            )
        )

        # 2. 抓取
        await self.submit(
            AnimCmd.hand_grab_object(
                which_hand=self.which_hand,
                object_id=self.object_id,
                container_unique_name=self.container_id,
                force_grab=self.force_grab,
                use_socket=self.use_socket,
            )
        )

        # 3. 收手
        await self.submit(AnimCmd.hand_back(which_hand=self.which_hand))


# ====== PUT DOWN TO LOCATION ======


@dataclass(slots=True)
class PutDownToLocation(ActionBase):
    """
    动作: 放下物体到指定位置。

    Attributes:
        which_hand (AnimCmdHandType): 使用的手部。
        target_location (Vector3): 目标位置。
        disable_physics (bool): 松手后是否禁用物理效果，默认 False。
        hold_if_unreachable (bool): 若物体无法到达目标位置，是否保持抓握，默认 False。
        force_release (bool): 是否强制释放，默认 True。
        auto_rotate (bool): 是否自动调整旋转，默认 False。
        rotation (Quaternion | None): 调整后的旋转角度，可选。
        force_locate (bool): 是否强制放到特定位置，默认 True。
        container_id (str | None): 容器 ID（用于优化动作表现），可选。
    """

    which_hand: AnimCmdHandType
    target_location: Vector3
    force_release: bool = True
    disable_physics: bool = False
    hold_if_unreachable: bool = False
    auto_rotate: bool = False
    rotation: Quaternion | None = None
    force_locate: bool = True
    container_id: str | None = None

    def validate(self) -> None:
        if not isinstance(self.target_location, Vector3):
            raise TypeError("target_location must be a Vector3.")
        if not isinstance(self.which_hand, AnimCmdHandType):
            raise ValueError(f"Invalid hand type: {self.which_hand}")

    async def execute(self) -> None:
        # 1. 伸手
        await self.submit(
            AnimCmd.hand_reach_to_location(
                which_hand=self.which_hand,
                location=self.target_location,
                is_reach_from_front=False,
                auto_offset=True,
            )
        )

        # 2. 放置
        await self.submit(
            AnimCmd.hand_release_with_location(
                which_hand=self.which_hand,
                target_location=self.target_location,
                force_locate=self.force_locate,
                auto_rotate=self.auto_rotate,
                rotation=self.rotation,
                force_release=self.force_release,
                disable_physics=self.disable_physics,
                hold_if_unreachable=self.hold_if_unreachable,
                container_unique_name=self.container_id,
            )
        )

        # 3. 收手
        await self.submit(AnimCmd.hand_back(which_hand=self.which_hand))


# ====== HAND REACH ======


@dataclass(slots=True)
class HandReach(ActionBase):
    """
    动作: 手部伸向目标位置。

    Attributes:
        which_hand (AnimCmdHandType): 使用的手部。
        target_location (Vector3): 目标位置。
        is_reach_from_front (bool): 是否从前方伸手，默认 False。
        auto_offset (bool): 是否自动调整到表面，默认 True。
    """

    which_hand: AnimCmdHandType
    target_location: Vector3
    is_reach_from_front: bool = False
    auto_offset: bool = True

    def validate(self) -> None:
        if not isinstance(self.target_location, Vector3):
            raise TypeError("target_location must be a Vector3.")
        if not isinstance(self.which_hand, AnimCmdHandType):
            raise ValueError(f"Invalid hand type: {self.which_hand}")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.hand_reach_to_location(
                which_hand=self.which_hand,
                location=self.target_location,
                is_reach_from_front=self.is_reach_from_front,
                auto_offset=self.auto_offset,
            )
        )


# ====== HAND BACK ======


@dataclass(slots=True)
class HandBack(ActionBase):
    """
    动作: 手部收回。

    Attributes:
        which_hand (AnimCmdHandType): 使用的手部。
    """

    which_hand: AnimCmdHandType

    def validate(self) -> None:
        if not isinstance(self.which_hand, AnimCmdHandType):
            raise ValueError(f"Invalid hand type: {self.which_hand}")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.hand_back(
                which_hand=self.which_hand,
            )
        )


# ====== HAND RELEASE ======


@dataclass(slots=True)
class HandRelease(ActionBase):
    """
    动作: 释放手中的物体。

    Attributes:
        which_hand (AnimCmdHandType): 使用的手部。
        target_location (Vector3): 目标位置。
        force_locate (bool): 是否强制放到特定位置，默认 True。
        force_release (bool): 是否强制释放，默认 True
        auto_rotate (bool): 是否自动调整旋转，默认 False。
        disable_physics (bool): 是否禁用物理效果，默认 False。
        hold_if_unreachable (bool): 若释放失败是否继续抓握，默认 False。
        container_id (str | None): 容器 ID（用于优化表现），可选。
    """

    which_hand: AnimCmdHandType
    target_location: Vector3
    force_locate: bool = True
    force_release: bool = True
    auto_rotate: bool = False
    rotation: Quaternion | None = None
    disable_physics: bool = False
    hold_if_unreachable: bool = False
    container_id: str | None = None

    def validate(self) -> None:
        if not isinstance(self.target_location, Vector3):
            raise TypeError("target_location must be a Vector3.")
        if not isinstance(self.which_hand, AnimCmdHandType):
            raise ValueError(f"Invalid hand type: {self.which_hand}")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.hand_release_with_location(
                which_hand=self.which_hand,
                target_location=self.target_location,
                force_locate=self.force_locate,
                auto_rotate=self.auto_rotate,
                rotation=self.rotation,
                force_release=self.force_release,
                disable_physics=self.disable_physics,
                hold_if_unreachable=self.hold_if_unreachable,
                container_unique_name=self.container_id,
            )
        )
