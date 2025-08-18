"""
connection.grpc._legacy.action_id

已弃用的通信协议中包含的 action_id 常量。
"""

from dataclasses import dataclass
from typing import Literal

# 定义允许的 action_id（用于类型提示）
ActionIDType = Literal[
    # unary:
    "OpenLevelCall",
    "EnableBabyAI",
    "SpawnCameraGroupCall",
    "SpawnCamera",
    "AttachCamerasToSockets",
    "GetValueCall",
    "CallSetPose",
    "SetObjectState",
    "SetGroupIDGetObjectByName",
    "StartCaptureOffline",
    "GetRandomSpawnerLocation",
    "EnableBabyAI",
    "QueryAllAnimationCompleted",
    "GetRoomNameFromLocation",
    "DestroyObjectCall",
    # stream:
    "SetValueStream",
]


@dataclass(frozen=True)
class ActionID:
    OPEN_LEVEL: ActionIDType = "OpenLevelCall"
    ENABLE_BABY_AI: ActionIDType = "EnableBabyAI"
    SPAWN_CAMERA_GROUP: ActionIDType = "SpawnCameraGroupCall"
    SPAWN_CAMERA: ActionIDType = "SpawnCamera"
    ATTACH_CAMERAS_TO_SOCKETS: ActionIDType = "AttachCamerasToSockets"
    SET_VALUE_STREAM: ActionIDType = "SetValueStream"
    GET_VALUE_CALL: ActionIDType = "GetValueCall"
    CALL_SET_POSE: ActionIDType = "CallSetPose"
    SET_OBJECT_STATE: ActionIDType = "SetObjectState"
    SET_GROUP_ID: ActionIDType = "SetGroupID"
    GET_OBJECT_BY_NAME: ActionIDType = "GetObjectByName"
    START_CAPTURE_OFFLINE: ActionIDType = "StartCaptureOffline"
    GET_RANDOM_SPAWN_LOCATION: ActionIDType = "GetRandomSpawnerLocation"
    ENABLE_BABY_AI: ActionIDType = "EnableBabyAI"
    IS_ALL_ANIM_COMPLETED: ActionIDType = "QueryAllAnimationCompleted"
    GET_ROOM_NAME_FROM_LOCATION: ActionIDType = "GetRoomNameFromLocation"
    DESTROY_OBJECT: ActionIDType = "DestroyObjectCall"
