"""
tongsim.entity.ability.registry

注册与管理所有 Ability 接口与其对应实现类的映射关系。

通过懒加载机制为开发者提供高效的能力扩展和组合功能。

Example:
    @AbilityRegistry.register(CameraAbility)
    class CameraAbilityImpl(AbilityImplBase):
        ...
"""

from collections.abc import Callable
from typing import ClassVar, TypeVar, get_origin

from tongsim.entity.ability.base import AbilityImplBase
from tongsim.logger import get_logger

_logger = get_logger("ability")

T = TypeVar("T")

__all__ = ["AbilityRegistry"]


class AbilityRegistry:
    """
    Ability 注册表，维护 Protocol -> Impl 的映射关系。
    """

    _impls: ClassVar[dict[type[T], type[AbilityImplBase]]] = {}
    __new__ = staticmethod(lambda cls: cls)

    @classmethod
    def register(
        cls, ability: type[T]
    ) -> Callable[[type[AbilityImplBase]], type[AbilityImplBase]]:
        """
        注册一个 Ability 接口及其对应的实现类。

        Args:
            ability (type[T]): 继承自 Protocol 的能力类型。

        Returns:
            Callable: 装饰器，用于修饰 AbilityImpl 类。
        """

        def decorator(impl_cls: type[AbilityImplBase]) -> type[AbilityImplBase]:
            key = cls._normalize(ability)
            if key in cls._impls:
                raise ValueError(
                    f"[AbilityRegistry] Ability '{key.__name__}' already registered."
                )
            cls._impls[key] = impl_cls
            return impl_cls

        return decorator

    @classmethod
    def get_impl_cls(cls, ability: type[T]) -> type[AbilityImplBase] | None:
        """
        获取指定 Ability 的实现类（若已注册）。

        Args:
            ability (type[T]): Protocol 类型能力接口

        Returns:
            AbilityImplBase 的子类，或 None（未注册时）
        """
        return cls._impls.get(cls._normalize(ability))

    @classmethod
    def debug_dump(cls) -> None:
        """
        打印所有已注册的 Ability 映射（调试用）。
        """
        _logger.debug("=== Registered Ability Implementations ===")
        for ability, impl in cls._impls.items():
            _logger.debug(f"{ability.__name__} -> {impl.__name__}")

    @staticmethod
    def _normalize(ability: type[T]) -> type[T]:
        """
        统一泛型 Protocol 和原始类型的映射 key。
        """
        return get_origin(ability) or ability
