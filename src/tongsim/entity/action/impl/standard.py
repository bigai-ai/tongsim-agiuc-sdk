from dataclasses import dataclass

from tongsim.connection.grpc import AnimCmd
from tongsim.entity.action.base import ActionBase
from tongsim.math.geometry import Vector3
from tongsim.type.anim import AnimCmdHandType

# ====== POUR WATER ======


@dataclass(slots=True)
class PourWater(ActionBase):
    """
    动作: 倒水。

    Attributes:
        target_id (str): 倒水目标对象ID（杯子）
        location (Vector3): 倒水的目标位置（比如杯子伸到哪）
        which_hand (AnimCmdHandType): 使用哪只手
    """

    target_id: str
    location: Vector3
    which_hand: AnimCmdHandType

    def validate(self) -> None:
        if not self.target_id:
            raise ValueError("target_id must be provided.")
        if not isinstance(self.location, Vector3):
            raise TypeError("location must be a Vector3.")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.pour_water(
                target_id=self.target_id,
                location=self.location,
                which_hand=self.which_hand,
            )
        )


# ====== READ BOOK ======


@dataclass(slots=True)
class ReadBook(ActionBase):
    """
    动作: 阅读书籍， 需要手上有书

    Attributes:
        duration (int): 阅读时间（秒）。
    """

    duration: int

    def validate(self) -> None:
        if not isinstance(self.duration, int) or self.duration <= 0:
            raise ValueError("duration must be a positive integer.")

    async def execute(self) -> None:
        await self.submit(AnimCmd.read_book(duration=self.duration))


# ====== CLIMB DOWN ======


@dataclass(slots=True)
class ClimbDown(ActionBase):
    """
    动作: 爬下
    """

    def validate(self) -> None:
        pass

    async def execute(self) -> None:
        await self.submit(AnimCmd.climb_down())


# ====== CLIMB OBJECT ======


@dataclass(slots=True)
class ClimbObject(ActionBase):
    """
    动作: 爬上指定物体。

    Attributes:
        object_name (str): 目标物体名称
    """

    object_name: str

    def validate(self) -> None:
        if not self.object_name:
            raise ValueError("object_name must be provided.")

    async def execute(self) -> None:
        await self.submit(AnimCmd.climb_object(object_name=self.object_name))


# ====== SIT======


@dataclass(slots=True)
class SitDownToLocation(ActionBase):
    """
    动作: 坐下到指定位置。

    Attributes:
        location (Vector3): 坐下的位置
    """

    location: Vector3

    def validate(self) -> None:
        if not isinstance(self.location, Vector3):
            raise TypeError("location must be a Vector3.")

    async def execute(self) -> None:
        await self.submit(AnimCmd.sit_down_to_location(location=self.location))


@dataclass(slots=True)
class SitDownToObject(ActionBase):
    """
    动作: 坐下到指定物体。

    Attributes:
        object_id (str): 目标物体 ID
    """

    object_id: str

    def validate(self) -> None:
        if not self.object_id:
            raise ValueError("object_id must be provided.")

    async def execute(self) -> None:
        await self.submit(AnimCmd.sit_down_to_object(object_id=self.object_id))


# ====== SLEEP ======


@dataclass(slots=True)
class SleepDown(ActionBase):
    """
    动作: 躺下睡觉

    Attributes:
        object_id (str): 睡觉目标（床 或者 沙发）
    """

    object_id: str

    def validate(self) -> None:
        if not self.object_id:
            raise ValueError("object_id must be provided.")

    async def execute(self) -> None:
        await self.submit(AnimCmd.sleep_down(subject=self.object_id))


@dataclass(slots=True)
class SleepUp(ActionBase):
    """
    动作: 起身（从睡眠状态）。
    """

    def validate(self) -> None:
        pass

    async def execute(self) -> None:
        await self.submit(AnimCmd.sleep_up())


# ====== SLICE FOOD ======


@dataclass(slots=True)
class SliceFood(ActionBase):
    """
    动作: 切割食物。

    Attributes:
        food_id (str): 被切割的食物 ID
        location (Vector3): 切割位置
    """

    food_id: str
    location: Vector3

    def validate(self) -> None:
        if not self.food_id:
            raise ValueError("food_id must be provided.")
        if not isinstance(self.location, Vector3):
            raise TypeError("location must be a Vector3.")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.slice_food(food_id=self.food_id, location=self.location)
        )


# ====== WASH ======


@dataclass(slots=True)
class WashHands(ActionBase):
    """
    动作: 洗手。

    Attributes:
        faucet_object_id (str): 水龙头对象名称
    """

    faucet_object_id: str

    def validate(self) -> None:
        if not self.faucet_object_id:
            raise ValueError("faucet_object_id must be provided.")

    async def execute(self) -> None:
        await self.submit(AnimCmd.wash_hands(faucet_object_name=self.faucet_object_id))


@dataclass(slots=True)
class WashFace(ActionBase):
    """
    动作: 洗脸。

    Attributes:
        faucet_object_id (str): 水龙头对象名称
    """

    faucet_object_id: str

    def validate(self) -> None:
        if not self.faucet_object_id:
            raise ValueError("faucet_object_id must be provided.")

    async def execute(self) -> None:
        await self.submit(AnimCmd.wash_face(faucet_object_name=self.faucet_object_id))


@dataclass(slots=True)
class WashObjectInHand(ActionBase):
    """
    动作: 洗手中的物体。

    Attributes:
        faucet_object_id (str): 水龙头对象名称
    """

    faucet_object_id: str

    def validate(self) -> None:
        if not self.faucet_object_id:
            raise ValueError("faucet_object_id must be provided.")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.wash_object_in_hand(faucet_object_name=self.faucet_object_id)
        )


# ====== SWITCH DOOR ======


@dataclass(slots=True)
class OpenDoor(ActionBase):
    """
    动作: 开门或抽屉。TongSim中, 门组件 泛指 基于物理约束绑定的组件，比如旋转门，推拉门，抽屉等等。

    Attributes:
        component_id (str): 门组件 ID。
        which_hand (AnimCmdHandType): 使用哪只手
    """

    component_id: str
    which_hand: AnimCmdHandType

    def validate(self) -> None:
        if not self.component_id:
            raise ValueError("component_id must be provided.")
        if not isinstance(self.which_hand, AnimCmdHandType):
            raise ValueError(f"Invalid hand type: {self.which_hand}")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.move_to_component(component_id=self.component_id, use_socket=True)
        )
        await self.submit(
            AnimCmd.turn_around_to_component(
                component_id=self.component_id, use_socket=True
            )
        )
        await self.submit(
            AnimCmd.hand_reach_to_component(
                which_hand=self.which_hand,
                component_id=self.component_id,
                use_socket=True,
            )
        )
        await self.submit(
            AnimCmd.open_door(
                component_id=self.component_id, which_hand=self.which_hand
            )
        )
        await self.submit(AnimCmd.hand_back(which_hand=self.which_hand))


@dataclass(slots=True)
class CloseDoor(ActionBase):
    """
    动作: 关门或抽屉。TongSim中, 门组件 泛指 基于物理约束绑定的组件，比如旋转门，推拉门，抽屉等等。

    Attributes:
        component_id (str): 门组件 ID。
        which_hand (AnimCmdHandType): 使用哪只手
    """

    component_id: str
    which_hand: AnimCmdHandType

    def validate(self) -> None:
        if not self.component_id:
            raise ValueError("component_id must be provided.")
        if not isinstance(self.which_hand, AnimCmdHandType):
            raise ValueError(f"Invalid hand type: {self.which_hand}")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.move_to_component(component_id=self.component_id, use_socket=True)
        )
        await self.submit(
            AnimCmd.turn_around_to_component(
                component_id=self.component_id, use_socket=True
            )
        )
        await self.submit(
            AnimCmd.hand_reach_to_component(
                which_hand=self.which_hand,
                component_id=self.component_id,
                use_socket=True,
            )
        )
        await self.submit(
            AnimCmd.close_door(
                component_id=self.component_id, which_hand=self.which_hand
            )
        )
        await self.submit(AnimCmd.hand_back(which_hand=self.which_hand))


@dataclass(slots=True)
class StandUp(ActionBase):
    """
    动作: 起立。

    用于从坐下或躺下状态回到站立状态。
    """

    def validate(self) -> None:
        pass

    async def execute(self) -> None:
        await self.submit(AnimCmd.stand_up())


@dataclass(slots=True)
class PlayAnimation(ActionBase):
    """
    动作: 播放指定的动画序列。

    Attributes:
        animation_name (str): 动画序列的名称。
        animation_slot (str): 动画槽位。当前支持： [PlayAnimSequence(default), UpperBody, LowerBody,Facial]
    """

    animation_name: str
    animation_slot: str = "PlayAnimSequence"

    def validate(self) -> None:
        if not self.animation_name:
            raise ValueError("animation_name must be provided.")
        if not self.animation_slot:
            raise ValueError("animation_slot must be provided.")

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.play_animation(
                animation_to_play=self.animation_name,
                animation_slot=self.animation_slot,
            )
        )


@dataclass(slots=True)
class Wait(ActionBase):
    """
    动作: 等待指定时间。用于动作之间的间隔或延迟处理。

    Attributes:
        time_duration (float): 等待时间（单位: 秒），必须为非负数。
    """

    time_duration: float = 0.0

    def validate(self) -> None:
        if not isinstance(self.time_duration, int | float) or self.time_duration < 0:
            raise ValueError("time_duration must be a non-negative number.")

    async def execute(self) -> None:
        await self.submit(AnimCmd.wait_for(time_duration=self.time_duration))


@dataclass(slots=True)
class WipeQuad(ActionBase):
    """
    动作：擦拭一个矩形区域。

    注意：该动作想要成功擦除，要求 agent 手上有抹布等物体。

    Attributes:
        which_hand (AnimCmdHandType): 使用的手（左手或右手）。
        dirt_location (Vector3): 矩形区域的中心位置。
        quad_extent (float): 半边长(单位: cm), 决定矩形的大小。
    """

    which_hand: AnimCmdHandType
    dirt_location: Vector3
    quad_extent: float = 5.0

    def validate(self) -> None:
        if not isinstance(self.dirt_location, Vector3):
            raise ValueError("dirt_location must be a Vector3.")
        if not isinstance(self.quad_extent, int | float) or self.quad_extent <= 0:
            raise ValueError("quad_extent must be a positive number.")
        if not isinstance(self.which_hand, AnimCmdHandType):
            raise ValueError("which_hand must be a valid AnimCmdHandType.")

    async def execute(self) -> None:
        x, y, z = self.dirt_location.x, self.dirt_location.y, self.dirt_location.z
        e = self.quad_extent

        wipe_point1 = Vector3(x - e, y + e, z)
        wipe_point2 = Vector3(x + e, y + e, z)
        wipe_point3 = Vector3(x - e, y - e, z)
        wipe_point4 = Vector3(x + e, y - e, z)

        await self.submit(
            AnimCmd.wipe_quadrilateral(
                which_hand=self.which_hand,
                conner1=wipe_point1,
                conner2=wipe_point2,
                conner3=wipe_point3,
                conner4=wipe_point4,
            )
        )


@dataclass(slots=True)
class MopFloor(ActionBase):
    """
    动作：使用拖把清洁地面。

    注意：该动作要求 agent 右手持有拖把。

    Attributes:
        dirt_id (str): 需要清洁的污渍 ID。
    """

    dirt_id: str

    def validate(self) -> None:
        if not self.dirt_id:
            raise ValueError("dirt_id must be provided.")

    async def execute(self) -> None:
        await self.submit(AnimCmd.mop_floor(dirt_id=self.dirt_id))


@dataclass(slots=True)
class CancelAllActions(ActionBase):
    """
    动作：强制取消所有动作，包括当前正在执行的动作。
    """

    def validate(self) -> None:
        pass

    async def execute(self) -> None:
        await self.submit(AnimCmd.cancel_all_action())
