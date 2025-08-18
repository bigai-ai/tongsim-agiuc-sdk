from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Final

from tongsim.core.world_context import WorldContext

if TYPE_CHECKING:
    from tongsim.entity.entity import Entity


class AbilityImplBase(ABC):
    """
    所有 Ability Impl 的基类，提供通用的能力检查与上下文访问能力。
    """

    def __init__(self, entity: "Entity"):
        self._entity_id: Final[str] = entity.id
        self._context: Final[WorldContext] = entity.context

    @classmethod
    @abstractmethod
    def is_applicable(cls, entity: "Entity") -> bool:
        """
        检查该 AbilityImpl 是否满足必要的能力前提（例如组件或字段存在等）。

        Returns:
            bool: 是否满足前提条件
        """
        raise RuntimeError("Must implement in AbilityImpl")

    @classmethod
    async def create(cls, entity: "Entity") -> "AbilityImplBase":
        """
        异步工厂方法, 如果有异步初始化逻辑, 请在子类中重写此方法。
        """
        return cls(entity)
