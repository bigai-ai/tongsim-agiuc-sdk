"""
connection.tags.components

定义通信协议中使用的 Unreal组件 名称常量。
"""

from dataclasses import dataclass
from typing import Literal

# 定义允许的 Unreal组件 名称类型（用于类型提示）
ComponentType = Literal[
    "Pose",
    "Scale",
    "Camera",
    "SpawnerComponent",
    "Animation",
    "ObjectStateComponent",
    "EmotionComponent",
    "Container",
    "CollisionShape",
    "FoodEnergy",
    "CharacterAttachment",
    "Door",
    "Container",
    "VoxelComponent",
    "CharacterMovement",
]


@dataclass(frozen=True)
class ComponentTags:
    """
    用于存放预定义的 Unreal组件 名称常量。
    """

    ANIM: ComponentType = "Animation"
    POSE: ComponentType = "Pose"
    SCALE: ComponentType = "Scale"
    IMAGE: ComponentType = "Image"
    SPAWNER: ComponentType = "SpawnerComponent"
    OBJECT_STATE: ComponentType = "ObjectStateComponent"
    EMOTION: ComponentType = "EmotionComponent"
    CONTAINER: ComponentType = "Container"
    COLLISION: ComponentType = "CollisionShape"
    FOOD_ENERGY: ComponentType = "FoodEnergy"
    CHAR_ATTACHMENT: ComponentType = "CharacterAttachment"
    CHAR_ATTRIBUTE: ComponentType = "CharacterAttributeComponent"
    DOOR: ComponentType = "Door"
    CONTAINER: ComponentType = "Container"
