from typing import TypeVar

from .type import Box, Pose, Quaternion, Transform, Vector2, Vector3

__all__ = ["create_instance_from_dict"]


T = TypeVar("T")


def create_instance_from_dict(
    cls: type[Pose | Vector3 | Vector2 | Box | Transform | Quaternion], data: dict
) -> T:
    """
    根据字典数据创建类的实例，进行严格的字段检查。
    目前仅可使用于: Pose|Vector3|Vector2|Box|Transform|Quaternion

    Args:
        cls: 要创建的类
        data: 字典，包含类的属性及其值

    Returns:
        类的实例
    """
    instance = cls()

    for key, value in data.items():
        if hasattr(instance, key):
            field_type = getattr(instance, key)

            if isinstance(field_type, Vector3) and isinstance(value, dict):
                setattr(instance, key, Vector3(value["x"], value["y"], value["z"]))
            elif isinstance(field_type, Quaternion) and isinstance(value, dict):
                setattr(
                    instance,
                    key,
                    Quaternion(value["w"], value["x"], value["y"], value["z"]),
                )
            elif isinstance(value, field_type.__class__):  # 检查类型匹配
                setattr(instance, key, value)
            else:
                raise TypeError(
                    f"Invalid type for field '{key}': Expected {field_type.__class__}, got {type(value)}."
                )
        else:
            raise AttributeError(f"Class '{cls.__name__}' has no field '{key}'.")

    return instance
