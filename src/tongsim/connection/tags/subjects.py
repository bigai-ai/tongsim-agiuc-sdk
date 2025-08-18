"""
connection.tags.subjects

定义通信协议中使用的 Unreal Actor ID 常量。
"""

from dataclasses import dataclass
from typing import Literal

# 定义允许的 Unreal Actor ID（用于类型提示）
SubjectType = Literal[
    "SceneManager",
    "Spectator",
]


@dataclass(frozen=True)
class SubjectTags:
    SCENE_MANAGER: SubjectType = "SceneManager"
    SPECTATOR: SubjectType = "Spectator"
