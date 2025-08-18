"""
connection.tags.anim_cmd

定义通信协议中使用的 Unreal Animataion Command Name 常量。
"""

from dataclasses import dataclass
from typing import Literal

# 定义允许的 Unreal Animataion Command Name（用于类型提示）
AnimationCommandType = Literal[
    "AC_MoveTo",
    "AC_TurnAroundTowards",
    "GazeAt",
    "PointAt",
    "AC_Wait",
    "ACCH_HandReach",
    "ACCH_HandRelease",
    "ACCH_HandGrabObject",
    "AC_PourWater",
    "AC_ReadBook",
    "AC_Sleep",
    "AC_SliceFood",
    "AC_SitDown",
    "AC_ClimbDown",
    "AC_ClimbPlatform",
    "AC_Wash",
    "AC_SwitchDoor",
    "AC_SM_LocoMotion",
    "AC_PlayAnimSequenceAC_SM_UpperBody",
    "AC_InteractObject",
    "AC_MopFloor",
    "ACCH_WipeQuadrilateral",
]


@dataclass(frozen=True)
class AnimationCommandTags:
    MOVE_TO: AnimationCommandType = "AC_MoveTo"
    TURN_AROUND_TOWARDS: AnimationCommandType = "AC_TurnAroundTowards"
    GAZE_AT: AnimationCommandType = "GazeAt"
    POINT_AT: AnimationCommandType = "PointAt"
    WAIT: AnimationCommandType = "AC_Wait"
    WAVE_HAND: AnimationCommandType = "AC_SM_UpperBody"
    NOD: AnimationCommandType = "AC_SM_UpperBody"
    SHAKE_HEAD: AnimationCommandType = "AC_SM_UpperBody"
    RAISE_HAND: AnimationCommandType = "AC_SM_UpperBody"
    IDLE_GESTURE: AnimationCommandType = "AC_SM_UpperBody"
    EAT_OR_DRINK: AnimationCommandType = "AC_SM_UpperBody"
    UPPER_BODY: AnimationCommandType = "AC_SM_UpperBody"
    HAND_REACH: AnimationCommandType = "ACCH_HandReach"
    HAND_RELEASE: AnimationCommandType = "ACCH_HandRelease"
    HAND_GRAB: AnimationCommandType = "ACCH_HandGrabObject"
    POUR_WATER: AnimationCommandType = "AC_PourWater"
    READ_BOOK: AnimationCommandType = "AC_ReadBook"
    SLEEP: AnimationCommandType = "AC_Sleep"
    SLICE_FOOD: AnimationCommandType = "AC_SliceFood"
    SIT_DOWN: AnimationCommandType = "AC_SitDown"
    CLIMB_DOWN: AnimationCommandType = "AC_ClimbDown"
    CLIMB_UP: AnimationCommandType = "AC_ClimbPlatform"
    WASH: AnimationCommandType = "AC_Wash"
    SWITCH_DOOR: AnimationCommandType = "AC_SwitchDoor"
    LOCOMOTION: AnimationCommandType = "AC_SM_LocoMotion"
    PLAY_ANIM_SEQ: AnimationCommandType = "AC_PlayAnimSequence"
    INTERACT_OBJECT: AnimationCommandType = "AC_InteractObject"
    MOP_FLOOR: AnimationCommandType = "AC_MopFloor"
    WIPE_QUAD: AnimationCommandType = "ACCH_WipeQuadrilateral"
    CANCEL: AnimationCommandType = "AC_Cancel"
    INPUT_MOVE: AnimationCommandType = "ALS_InputMove"
