"""
tongsim
"""

import typing
from importlib import import_module
from warnings import warn

from .version import VERSION

__version__ = VERSION

__all__ = (
    "BOTH_HANDS",
    "LEFT_HAND",
    "RIGHT_HAND",
    "AgentEntity",
    "BaseObjectEntity",
    "Box",
    "CameraEntity",
    "ConsumableEntity",
    "ElectricApplianceEntity",
    "InteractableEntity",
    "LegacyAPI",
    "LightEntity",
    "NPCEntity",
    "Pose",
    "Quaternion",
    "TongSim",
    "Transform",
    "UnaryAPI",
    "UnaryStreamAPI",
    "Vector2",
    "Vector3",
    "__version__",
    "action",
    "get_version_info",
    "initialize_logger",
    "set_log_level",
)

if typing.TYPE_CHECKING:
    # 导入用于 IDE 提示和类型检查
    from .connection.grpc import LegacyAPI, UnaryAPI, UnaryStreamAPI
    from .entity import (
        AgentEntity,
        BaseObjectEntity,
        CameraEntity,
        ConsumableEntity,
        ElectricApplianceEntity,
        InteractableEntity,
        LightEntity,
        NPCEntity,
        action,
    )
    from .logger import initialize_logger, set_log_level
    from .math.geometry import Box, Pose, Quaternion, Vector2, Vector3
    from .tongsim import TongSim
    from .type import BOTH_HANDS, LEFT_HAND, RIGHT_HAND
    from .version import get_version_info

# 模块路径映射，基于 `__spec__.parent` 动态确定包路径
_dynamic_imports: dict[str, tuple[str, str]] = {
    # Math
    "Pose": (__spec__.parent, ".math.geometry"),
    "Quaternion": (__spec__.parent, ".math.geometry"),
    "Vector3": (__spec__.parent, ".math.geometry"),
    "Vector2": (__spec__.parent, ".math.geometry"),
    "Box": (__spec__.parent, ".math.geometry"),
    "Transform": (__spec__.parent, ".math.geometry"),
    # Entity
    "AgentEntity": (__spec__.parent, ".entity"),
    "BaseObjectEntity": (__spec__.parent, ".entity"),
    "CameraEntity": (__spec__.parent, ".entity"),
    "ConsumableEntity": (__spec__.parent, ".entity"),
    "ElectricApplianceEntity": (__spec__.parent, ".entity"),
    "InteractableEntity": (__spec__.parent, ".entity"),
    "NPCEntity": (__spec__.parent, ".entity"),
    "LightEntity": (__spec__.parent, ".entity"),
    # Core
    "TongSim": (__spec__.parent, ".tongsim"),
    # Action
    "action": (__spec__.parent, ".entity"),
    # Logger
    "initialize_logger": (__spec__.parent, ".logger"),
    "set_log_level": (__spec__.parent, ".logger"),
    # Type
    "BOTH_HANDS": (__spec__.parent, ".type"),
    "LEFT_HAND": (__spec__.parent, ".type"),
    "RIGHT_HAND": (__spec__.parent, ".type"),
    # gRPC
    "UnaryAPI": (__spec__.parent, ".connection.grpc"),
    "UnaryStreamAPI": (__spec__.parent, ".connection.grpc"),
    "LegacyAPI": ((__spec__.parent, ".connection.grpc")),
    # Version
    "get_version_info": (__spec__.parent, ".version"),
}

# Deprecated 动态导入，用于兼容旧版本
_deprecated_imports = {}


def __getattr__(attr_name: str) -> object:
    """
    动态导入模块成员，仅在首次访问时进行实际导入。
    """
    # 检查是否为废弃模块
    if attr_name in _deprecated_imports:
        warn(
            f"Importing `{attr_name}` from `tongsim` is deprecated and will be removed in future versions.",
            DeprecationWarning,
            stacklevel=2,
        )

    # 检查有效动态导入成员
    dynamic_attr = _dynamic_imports.get(attr_name) or _deprecated_imports.get(attr_name)
    if dynamic_attr is None:
        raise AttributeError(f"Module 'tongsim' has no attribute '{attr_name}'")

    # 动态导入
    package, module_path = dynamic_attr
    module = import_module(module_path, package=package)
    result = getattr(module, attr_name)

    # 缓存到全局命名空间，避免重复导入
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    """提供完整的模块成员列表，包括动态导入成员。"""
    return list(__all__)
