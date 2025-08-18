"""
tongsim.type.anim

定义与动画执行结果相关的数据结构和常量，包括 AnimResultInfo 数据类和 HandType 枚举类型。
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Literal

__all__ = ["AnimCmdHandType", "AnimResultInfo"]


@dataclass(slots=True)
class AnimResultInfo:
    """
    动画执行结果信息。

    Attributes:
        command_id (int): 动画命令的唯一标识符。
        unreal_frame (int): Unreal 引擎中的帧编号。
        status (Literal["begin", "end", "error"]): 动画状态，可为 "begin"、"end" 或 "error"。
        error_code (int): 错误代码，默认为 0 表示无错误。
        error_animation_code (int): 出错动画代码，默认为 0 表示无错误。
    """

    command_id: int
    unreal_frame: int
    status: Literal["begin", "end", "error"]
    error_code: int = 0
    error_animation_code: int = 0


class AnimCmdHandType(IntEnum):
    """
    手部动作类型，用于标识动画中使用的手部。
    (注意值和 proto 中 EWhichHandAction 强对应！)

    Attributes:
        RIGHT (int): 右手。
        LEFT (int): 左手。
        BOTH (int): 双手。
    """

    RIGHT = 0
    LEFT = 1
    BOTH = 2


class AnimationExecutionType(IntEnum):
    """
    动画执行类型，用于标识动画执行方式。
    (注意值和 proto 中 EAnimationExecutionType 强对应！)

    Attributes:
        ENQUEUE (int): 入队执行。
        EXECUTE_IMMEDIATELY (int): 立即执行（目前仅对部分动画有效）
        OVERRIDE_PARAMS (int): 覆盖动作参数
    """

    ENQUEUE = 0
    EXECUTE_IMMEDIATELY = 1
    OVERRIDE_PARAMS = 3
