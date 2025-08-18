"""
tongsim.connection.grpc.anim_cmd
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from google.protobuf.message import Message
from tongsim_api_protocol import basic_pb2
from tongsim_api_protocol.basic_pb2 import (
    ComponentParams,
    EHandBackOrOut,
    EHandReachFrom,
)
from tongsim_api_protocol.component.animation.aim_offset_pb2 import AimOffset
from tongsim_api_protocol.component.animation.animation_pb2 import (
    AnimationEffectAttribute,
)
from tongsim_api_protocol.component.animation.cancel_pb2 import Cancel
from tongsim_api_protocol.component.animation.climb_down_pb2 import ClimbDown
from tongsim_api_protocol.component.animation.climb_platform_pb2 import ClimbObject
from tongsim_api_protocol.component.animation.gesture_pb2 import EGestureEnum, Gesture
from tongsim_api_protocol.component.animation.hand_grab_object_pb2 import HandGrabObject
from tongsim_api_protocol.component.animation.hand_reach_pb2 import HandReach
from tongsim_api_protocol.component.animation.hand_release_pb2 import HandRelease
from tongsim_api_protocol.component.animation.input_move_pb2 import InputMove
from tongsim_api_protocol.component.animation.interact_object_pb2 import (
    InteractObject,
    InteractParams,
)
from tongsim_api_protocol.component.animation.locomotion_pb2 import (
    ELocoMotionEnum,
    LocoMotion,
)
from tongsim_api_protocol.component.animation.mop_floor_pb2 import MopFloor
from tongsim_api_protocol.component.animation.move_to_pb2 import MoveTo
from tongsim_api_protocol.component.animation.play_animation_pb2 import PlayAnimation
from tongsim_api_protocol.component.animation.pour_water_pb2 import PourWaterParam
from tongsim_api_protocol.component.animation.readbook_pb2 import ReadBook
from tongsim_api_protocol.component.animation.sitdown_pb2 import SitDown
from tongsim_api_protocol.component.animation.sleep_pb2 import Sleep, SleepType
from tongsim_api_protocol.component.animation.slice_food_pb2 import SliceFoodParam
from tongsim_api_protocol.component.animation.switch_door_pb2 import SwitchDoor
from tongsim_api_protocol.component.animation.turn_around_pb2 import TurnAroundTo
from tongsim_api_protocol.component.animation.wait_pb2 import Wait
from tongsim_api_protocol.component.animation.wash_pb2 import WashParam, WashType
from tongsim_api_protocol.component.animation.wipe_quadrilateral_pb2 import (
    WipeQuadrilateral,
)

from tongsim.connection.tags import AnimationCommandTags, AnimationCommandType
from tongsim.math.geometry import Quaternion, Vector2, Vector3
from tongsim.type.anim import AnimationExecutionType, AnimCmdHandType

from .utils import sdk_to_proto

__all__ = ["AnimCommandBuilder", "CommandSpec"]


@dataclass(slots=True)
class CommandSpec:
    tag: AnimationCommandType
    oneof_field: str = ""
    oneof_msg: Message | None = None
    extra_fields: Mapping[str, Any] | None = None


class AnimCommandBuilder:
    """
    该类型提供 所有 AnimationCommandParams 子消息的构造函数，封装成原生 Python 静态方法
    """

    # ======  bigai.ue.component.animation.moveto ======
    @staticmethod
    def move_to_location(
        loc: Vector3,
        move_speed: float = 0.0,
        can_run: bool | None = None,
        accelerate_delay_time: float | None = None,
        max_speed: float | None = None,
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.MOVE_TO,
            oneof_field="move_to",
            oneof_msg=MoveTo(
                location=sdk_to_proto(loc),
                move_speed=move_speed,
                b_can_walk=can_run,  # TODO: proto 名字 相反
                accelerate_delay_time=accelerate_delay_time,
                max_speed=max_speed,
            ),
        )

    @staticmethod
    def move_to_object(
        object_id: str,
        use_socket: bool = False,
        move_speed: float = 0.0,
        can_run: bool | None = None,
        accelerate_delay_time: float | None = None,
        max_speed: float | None = None,
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.MOVE_TO,
            oneof_field="move_to",
            oneof_msg=MoveTo(
                object_params=basic_pb2.ObjectParams(
                    target=basic_pb2.Subject(id=object_id), b_use_socket=use_socket
                ),
                move_speed=move_speed,
                b_can_walk=can_run,  # TODO: proto 名字 相反
                accelerate_delay_time=accelerate_delay_time,
                max_speed=max_speed,
            ),
        )

    @staticmethod
    def move_to_component(
        component_id: str,
        use_socket: bool = False,
        move_speed: float = 0.0,
        can_run: bool | None = None,
        accelerate_delay_time: float | None = None,
        max_speed: float | None = None,
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.MOVE_TO,
            oneof_field="move_to",
            oneof_msg=MoveTo(
                component_params=basic_pb2.ComponentParams(
                    target=basic_pb2.Component(id=component_id), b_use_socket=use_socket
                ),
                move_speed=move_speed,
                b_can_walk=can_run,  # TODO: proto 名字 相反
                accelerate_delay_time=accelerate_delay_time,
                max_speed=max_speed,
            ),
        )

    # ====== bigai.ue.component.animation.turnaround ======
    @staticmethod
    def turn_around_to_location(
        loc: Vector3,
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.TURN_AROUND_TOWARDS,
            oneof_field="turn_around_to",
            oneof_msg=TurnAroundTo(
                location=sdk_to_proto(loc),
            ),
        )

    @staticmethod
    def turn_around_to_object(
        object_id: str,
        use_socket: bool = False,
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.TURN_AROUND_TOWARDS,
            oneof_field="turn_around_to",
            oneof_msg=TurnAroundTo(
                object_params=basic_pb2.ObjectParams(
                    target=basic_pb2.Subject(id=object_id), b_use_socket=use_socket
                ),
            ),
        )

    @staticmethod
    def turn_around_to_component(
        component_id: str,
        use_socket: bool = False,
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.TURN_AROUND_TOWARDS,
            oneof_field="turn_around_to",
            oneof_msg=TurnAroundTo(
                component_params=basic_pb2.ComponentParams(
                    target=basic_pb2.Component(id=component_id), b_use_socket=use_socket
                ),
            ),
        )

    @staticmethod
    def turn_around_degree(
        degree: float,
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.TURN_AROUND_TOWARDS,
            oneof_field="turn_around_to",
            oneof_msg=TurnAroundTo(angle_in_degree=degree),
        )

    # ====== bigai.ue.component.animation.aimoffset ======
    @staticmethod
    def look_at_location(
        loc: Vector3,
        is_cancel: bool,
        execute_immediately: bool = False,
    ) -> CommandSpec:
        execute_type = (
            AnimationExecutionType.EXECUTE_IMMEDIATELY
            if execute_immediately
            else AnimationExecutionType.ENQUEUE
        )
        return CommandSpec(
            tag=AnimationCommandTags.GAZE_AT,
            oneof_field="aim_offset",
            oneof_msg=AimOffset(
                b_aiming=not is_cancel,
                location=sdk_to_proto(loc),
            ),
            extra_fields={"animation_execution_type": execute_type},
        )

    @staticmethod
    def look_at_object(
        object_id: str,
        is_cancel: bool,
        execute_immediately: bool = False,
    ) -> CommandSpec:
        execute_type = (
            AnimationExecutionType.EXECUTE_IMMEDIATELY
            if execute_immediately
            else AnimationExecutionType.ENQUEUE
        )
        return CommandSpec(
            tag=AnimationCommandTags.GAZE_AT,
            oneof_field="aim_offset",
            oneof_msg=AimOffset(
                b_aiming=not is_cancel,
                object_id=object_id,
            ),
            extra_fields={"animation_execution_type": execute_type},
        )

    @staticmethod
    def point_at_location(
        loc: Vector3,
        is_cancel: bool,
        is_left_hand: bool,
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.POINT_AT,
            oneof_field="aim_offset",
            oneof_msg=AimOffset(
                b_aiming=not is_cancel,
                location=sdk_to_proto(loc),
                is_left=is_left_hand,
            ),
        )

    @staticmethod
    def point_at_object(
        object_id: str,
        is_cancel: bool,
        is_left_hand: bool,
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.POINT_AT,
            oneof_field="aim_offset",
            oneof_msg=AimOffset(
                b_aiming=not is_cancel,
                object_id=object_id,
                is_left=is_left_hand,
            ),
        )

    # ====== bigai.ue.component.animation.locomotion ======
    @staticmethod
    def stand_up() -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.LOCOMOTION,
            oneof_field="loco_motion",
            oneof_msg=LocoMotion(locomotion_status=ELocoMotionEnum.STAND),
        )

    # ====== bigai.ue.component.animation.playanimation ======

    @staticmethod
    def play_animation(animation_to_play: str, animation_slot: str) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.PLAY_ANIM_SEQ,
            oneof_field="play_animation",
            oneof_msg=PlayAnimation(
                animation_to_play=animation_to_play,
                animation_slot=animation_slot,
            ),
        )

    # ====== bigai.ue.component.animation.wait ======
    @staticmethod
    def wait_for(
        time_duration: float,
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.WAIT,
            oneof_field="wait",
            oneof_msg=Wait(time_duration=time_duration),
        )

    # ====== bigai.ue.component.animation.gesture ======

    @staticmethod
    def wave_hand(which_hand: AnimCmdHandType) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.WAVE_HAND,
            oneof_field="gesture",
            oneof_msg=Gesture(
                gesture_status=EGestureEnum.WAVE_HAND,
                which_hand_action=which_hand,
            ),
        )

    @staticmethod
    def raise_hand(which_hand: AnimCmdHandType) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.RAISE_HAND,
            oneof_field="gesture",
            oneof_msg=Gesture(
                gesture_status=EGestureEnum.RAISE_HAND,
                which_hand_action=which_hand,
            ),
        )

    @staticmethod
    def nod_head() -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.NOD,
            oneof_field="gesture",
            oneof_msg=Gesture(
                gesture_status=EGestureEnum.NOD_HEAD,
            ),
        )

    @staticmethod
    def shake_head() -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.SHAKE_HEAD,
            oneof_field="gesture",
            oneof_msg=Gesture(
                gesture_status=EGestureEnum.SHAKE_HEAD,
            ),
        )

    @staticmethod
    def idle_gesture() -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.IDLE_GESTURE,
            oneof_field="gesture",
            oneof_msg=Gesture(
                gesture_status=EGestureEnum.IDLE,
            ),
        )

    @staticmethod
    def eat_or_drink(which_hand: AnimCmdHandType) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.EAT_OR_DRINK,
            oneof_field="gesture",
            oneof_msg=Gesture(
                gesture_status=EGestureEnum.EAT_OR_DRINK,
                which_hand_action=which_hand,
            ),
        )

    @staticmethod
    def romp_play(
        which_hand: AnimCmdHandType, decrease_boredom: float = 0.0
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.UPPER_BODY,
            oneof_field="gesture",
            oneof_msg=Gesture(
                gesture_status=EGestureEnum.ROMPPLAYOBJECT,
                which_hand_action=which_hand,
            ),
            extra_fields={
                "animation_effect_attribute": AnimationEffectAttribute(
                    decrease_boredom=decrease_boredom
                ),
            },
        )

    # ====== bigai.ue.component.animation.handreach ======

    @staticmethod
    def hand_reach_to_location(
        which_hand: AnimCmdHandType,
        location: Vector3,
        is_reach_from_front: bool = False,
        auto_offset: bool = False,  # 伸到一个物体时， 该值 True 时自动伸到其上表面
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.HAND_REACH,
            oneof_field="hand_reach",
            oneof_msg=HandReach(
                which_hand_action=which_hand,
                hand_back_or_out=EHandBackOrOut.HAND_OUT,
                hand_reach_from=(
                    EHandReachFrom.FRONT
                    if is_reach_from_front
                    else EHandReachFrom.ABOVE
                ),
                object_location=sdk_to_proto(location),
                b_auto_offset=auto_offset,
            ),
        )

    @staticmethod
    def hand_reach_to_object(
        which_hand: AnimCmdHandType,
        object_id: str,
        is_reach_from_front: bool = False,
        auto_offset: bool = False,  # 伸到一个物体时， 该值 True 时自动伸到其上表面
        use_socket: bool = False,
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.HAND_REACH,
            oneof_field="hand_reach",
            oneof_msg=HandReach(
                which_hand_action=which_hand,
                hand_back_or_out=EHandBackOrOut.HAND_OUT,
                hand_reach_from=(
                    EHandReachFrom.FRONT
                    if is_reach_from_front
                    else EHandReachFrom.ABOVE
                ),
                object_params=basic_pb2.ObjectParams(
                    target=basic_pb2.Subject(id=object_id), b_use_socket=use_socket
                ),
                b_auto_offset=auto_offset,
            ),
        )

    @staticmethod
    def hand_reach_to_component(
        which_hand: AnimCmdHandType,
        component_id: str,
        is_reach_from_front: bool = False,
        auto_offset: bool = False,  # 伸到一个物体时， 该值 True 时自动伸到其上表面
        use_socket: bool = False,
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.HAND_REACH,
            oneof_field="hand_reach",
            oneof_msg=HandReach(
                which_hand_action=which_hand,
                hand_back_or_out=EHandBackOrOut.HAND_OUT,
                hand_reach_from=(
                    EHandReachFrom.FRONT
                    if is_reach_from_front
                    else EHandReachFrom.ABOVE
                ),
                component_params=ComponentParams(
                    target=basic_pb2.Component(id=component_id), b_use_socket=use_socket
                ),
                b_auto_offset=auto_offset,
            ),
        )

    @staticmethod
    def hand_back(
        which_hand: AnimCmdHandType,
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.HAND_REACH,
            oneof_field="hand_reach",
            oneof_msg=HandReach(
                which_hand_action=which_hand,
                hand_back_or_out=EHandBackOrOut.HAND_BACK,
            ),
        )

    # ====== bigai.ue.component.animation.handrelease ======

    @staticmethod
    def hand_release_with_location(
        which_hand: AnimCmdHandType,
        target_location: Vector3,
        force_locate: bool = False,
        auto_rotate: bool = False,
        rotation: Quaternion | None = None,
        force_release: bool = False,  # 强制松手带瞬移
        disable_physics: bool = False,
        hold_if_unreachable: bool = False,  # 强制松手不瞬移
        container_unique_name: (
            str | None
        ) = None,  # 如果你需要放在一个 container 内，传这个优化动作表现
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.HAND_RELEASE,
            oneof_field="hand_release",
            oneof_msg=HandRelease(
                which_hand_action=which_hand,
                target_location=sdk_to_proto(target_location),
                b_force_locate=force_locate,
                b_auto_rotate=auto_rotate,
                rotation=sdk_to_proto(rotation) if rotation else None,
                b_force_release=force_release,
                b_disable_physics=disable_physics,
                b_hold_if_unreachable=hold_if_unreachable,
                container_unique_name=container_unique_name,
            ),
        )

    # ====== bigai.ue.component.animation.handgrabobject ======

    @staticmethod
    def hand_grab_object(
        which_hand: AnimCmdHandType,
        object_id: str,
        container_unique_name: (
            str | None
        ) = None,  # 在容器内抓东西，传这个是容器id，为了优化动画
        force_grab: bool = False,
        use_socket: bool = False,
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.HAND_GRAB,
            oneof_field="hand_grab_object",
            oneof_msg=HandGrabObject(
                which_hand_action=which_hand,
                object_params=basic_pb2.ObjectParams(
                    target=basic_pb2.Subject(id=object_id), b_use_socket=use_socket
                ),
                container_unique_name=container_unique_name,
                b_force_grab=force_grab,
            ),
        )

    @staticmethod
    def hand_grab_component(
        which_hand: AnimCmdHandType,
        component_id: str,
        container_unique_name: (
            str | None
        ) = None,  # 在容器内抓东西，传这个是容器id，为了优化动画
        force_grab: bool = False,
        use_socket: bool = False,
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.HAND_GRAB,
            oneof_field="hand_grab_object",
            oneof_msg=HandGrabObject(
                which_hand_action=which_hand,
                component_params=ComponentParams(
                    target=basic_pb2.Component(id=component_id), b_use_socket=use_socket
                ),
                container_unique_name=container_unique_name,
                b_force_grab=force_grab,
            ),
        )

    # ====== bigai.ue.component.animation.pour_water ======
    @staticmethod
    def pour_water(
        target_id: str, location: Vector3, which_hand: AnimCmdHandType
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.POUR_WATER,
            oneof_field="pour_water",
            oneof_msg=PourWaterParam(
                target_id=target_id,
                location=sdk_to_proto(location),
                which_hand_action=which_hand,
            ),
        )

    # ====== bigai.ue.component.animation.readbook ======
    @staticmethod
    def read_book(duration: int) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.READ_BOOK,
            oneof_field="read_book",
            oneof_msg=ReadBook(
                time=duration,
            ),
        )

    # ====== bigai.ue.component.animation.interact_object ======
    @staticmethod
    def touch_object_state(target_id: str, new_state: bool) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.INTERACT_OBJECT,
            oneof_field="interact_object",
            oneof_msg=InteractObject(
                interact_key="Touch",
                interact_param=InteractParams(
                    target_id=target_id,
                    bool_value=new_state,
                ),
            ),
        )

    @staticmethod
    def set_object_channel(target_id: str, new_channel: str) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.INTERACT_OBJECT,
            oneof_field="interact_object",
            oneof_msg=InteractObject(
                interact_key="SetChannel",
                interact_param=InteractParams(
                    target_id=target_id,
                    str_value=new_channel,
                ),
            ),
        )

    # ====== bigai.ue.component.animation.climbdown ======
    @staticmethod
    def climb_down() -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.CLIMB_DOWN,
            oneof_field="climb_down",
            oneof_msg=ClimbDown(
                none_msg="",
            ),
        )

    # ====== bigai.ue.component.animation.climbplatform ======

    @staticmethod
    def climb_object(object_name: str) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.CLIMB_UP,
            oneof_field="climb_object",
            oneof_msg=ClimbObject(
                object_name=object_name,
            ),
        )

    # ====== bigai.ue.component.animation.sitdown ======

    @staticmethod
    def sit_down_to_location(
        location: Vector3,
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.SIT_DOWN,
            oneof_field="sitdown",
            oneof_msg=SitDown(
                location=sdk_to_proto(location),
            ),
        )

    @staticmethod
    def sit_down_to_object(object_id: str) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.SIT_DOWN,
            oneof_field="sitdown",
            oneof_msg=SitDown(
                object_id=object_id,
            ),
        )

    # ====== bigai.ue.component.animation.sleep ======

    @staticmethod
    def sleep_down(subject: str) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.SLEEP,
            oneof_field="sleep",
            oneof_msg=Sleep(sleep_type=SleepType.SLEEP_DOWN, subject=subject),
        )

    @staticmethod
    def sleep_up() -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.SLEEP,
            oneof_field="sleep",
            oneof_msg=Sleep(sleep_type=SleepType.SLEEP_UP),
        )

    # ====== bigai.ue.component.animation.slice_food ======

    @staticmethod
    def slice_food(food_id: str, location: Vector3) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.SLICE_FOOD,
            oneof_field="slice_food",
            oneof_msg=SliceFoodParam(
                food_id=food_id,
                location=sdk_to_proto(location),
            ),
        )

    # ====== bigai.ue.component.animation.wash ======

    @staticmethod
    def wash_hands(faucet_object_name: str) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.WASH,
            oneof_field="wash_param",
            oneof_msg=WashParam(
                wash_type=WashType.WASH_HANDS,
                faucetobjectname=faucet_object_name,
            ),
        )

    @staticmethod
    def wash_face(faucet_object_name: str) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.WASH,
            oneof_field="wash_param",
            oneof_msg=WashParam(
                wash_type=WashType.WASH_FACE,
                faucetobjectname=faucet_object_name,
            ),
        )

    @staticmethod
    def wash_object_in_hand(faucet_object_name: str) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.WASH,
            oneof_field="wash_param",
            oneof_msg=WashParam(
                wash_type=WashType.WASH_OBJECT_IN_HAND,
                faucetobjectname=faucet_object_name,
            ),
        )

    # ====== bigai.ue.component.animation.switchdoor ======

    @staticmethod
    def open_door(component_id: str, which_hand: AnimCmdHandType) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.SWITCH_DOOR,
            oneof_field="switch_door",
            oneof_msg=SwitchDoor(
                component=basic_pb2.Component(id=component_id),
                b_open=True,
                which_hand_action=which_hand,
            ),
        )

    @staticmethod
    def close_door(component_id: str, which_hand: AnimCmdHandType) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.SWITCH_DOOR,
            oneof_field="switch_door",
            oneof_msg=SwitchDoor(
                component=basic_pb2.Component(id=component_id),
                b_open=False,
                which_hand_action=which_hand,
            ),
        )

    # ====== bigai.ue.component.animation.wipe_quadrilateral ======
    @staticmethod
    def wipe_quadrilateral(
        which_hand: AnimCmdHandType,
        conner1: Vector3,
        conner2: Vector3,
        conner3: Vector3,
        conner4: Vector3,
    ) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.WIPE_QUAD,
            oneof_field="wipe_quadrilateral",
            oneof_msg=WipeQuadrilateral(
                which_hand_action=which_hand,
                conner1=sdk_to_proto(conner1),
                conner2=sdk_to_proto(conner2),
                conner3=sdk_to_proto(conner3),
                conner4=sdk_to_proto(conner4),
            ),
        )

    # ====== bigai.ue.component.animation.mop_floor ======
    @staticmethod
    def mop_floor(dirt_id: str) -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.MOP_FLOOR,
            oneof_field="mop_floor",
            oneof_msg=MopFloor(dirt_id=dirt_id),
        )

    @staticmethod
    def cancel_all_action() -> CommandSpec:
        return CommandSpec(
            tag=AnimationCommandTags.CANCEL,
            oneof_field="cancel",
            oneof_msg=Cancel(action_id=0),  # 此处0为UE默认取消所有动作的id
        )

    @staticmethod
    def switch_input_animation(is_close_input: bool):
        return CommandSpec(
            tag=AnimationCommandTags.INPUT_MOVE,
            oneof_field="input_move",
            oneof_msg=InputMove(
                end_animation=is_close_input,
            ),
        )

    @staticmethod
    def input_action(
        move_vec: Vector2 | None = None,
        sprint: bool | None = None,
        angular_speed: float | None = None,
        jump: bool | None = None,
        crouch: bool | None = None,
    ):
        request = InputMove(
            move_vector=sdk_to_proto(move_vec) if move_vec is not None else None,
            sprint=sprint,
            angular_speed=angular_speed,
            jump=jump,
            crouch=crouch,
        )
        return CommandSpec(
            tag=AnimationCommandTags.INPUT_MOVE,
            oneof_field="input_move",
            oneof_msg=request,
        )
