"""
connection.grpc._legacy.attribute_id

已弃用的通信协议中包含的 attribute_id 常量。
"""

from dataclasses import dataclass
from typing import Literal

# 定义允许的 attribute_id（用于类型提示）
AttributeID = Literal[
    "CameraIntrinsicMatrix",
    "Pose",
    "AABB",
    "PlayableAnimSequences",
    "FoodEnergy",
    "Scale",
]


@dataclass(frozen=True)
class AttributeIDs:
    CAMERA_INTRINSIC: AttributeID = "CameraIntrinsicMatrix"
    POSE: AttributeID = "Pose"
    AABB: AttributeID = "AABB"
    PLAYABLE_ANIMS: AttributeID = "PlayableAnimSequences"
    FOOD_ENERGY: AttributeID = "FoodEnergy"
    SCALE: AttributeID = "Scale"
