# tongsim/entity/ability/impl/camera.py

from typing import Protocol

from tongsim import UnaryAPI
from tongsim.connection.tags import ComponentTags
from tongsim.entity.ability.base import AbilityImplBase
from tongsim.entity.ability.registry import AbilityRegistry
from tongsim.entity.entity import Entity
from tongsim.logger import get_logger
from tongsim.math import Vector3

_logger = get_logger("light")

__all__ = [
    "LightAbility",
]


class LightAbility(Protocol):
    """
    灯光能力接口定义，包括:
    - 设置灯光颜色
    """

    def set_light_color(self, color: Vector3) -> bool:
        """
        设置当前实体的灯光颜色

        Args:
            color (Vector3): 灯光的颜色 (0-255)。

        Return:
            bool: 是否设置成功。
        """

    async def async_set_light_color(self, color: Vector3) -> bool:
        """
        异步设置当前实体的灯光颜色

        Args:
            color (Vector3): 灯光的颜色 (0-255)。

        Return:
            bool: 是否设置成功。
        """


@AbilityRegistry.register(LightAbility)
class LightAbilityImpl(AbilityImplBase):
    def __init__(self, entity: Entity):
        super().__init__(entity)
        self._object_state_component_id: str = entity.get_component_id(
            ComponentTags.OBJECT_STATE
        )

    @classmethod
    def is_applicable(cls, entity: Entity) -> bool:
        return entity.has_component_type(ComponentTags.OBJECT_STATE)

    async def async_set_light_color(self, color: Vector3) -> bool:
        return await UnaryAPI.set_light_color(
            self._context.conn, self._object_state_component_id, color
        )

    def set_light_color(self, color: Vector3) -> bool:
        return self._context.sync_run(self.async_set_light_color(color))
