"""
tongsim.entity.ability.impl.powerable
"""

from typing import Protocol

from tongsim.connection.grpc import UnaryAPI
from tongsim.connection.tags import ComponentTags
from tongsim.entity.ability.base import AbilityImplBase
from tongsim.entity.ability.registry import AbilityRegistry
from tongsim.entity.entity import Entity

__all__ = ["PowerableAbility"]


class PowerableAbility(Protocol):
    """
    PowerableAbility 定义了具备通电状态管理的实体能力接口。

    提供是否通电状态的查询与控制接口。
    """

    async def async_get_power_status(self) -> bool:
        """
        异步获取当前实体的通电状态。

        Returns:
            bool: True 表示通电，False 表示断电。
        """

    def get_power_status(self) -> bool:
        """
        同步获取当前实体的通电状态。

        Returns:
            bool: True 表示通电，False 表示断电。
        """

    async def async_set_power_status(self, is_on: bool) -> bool:
        """
        异步设置当前实体的通电状态。注意当该接口设置后，无论物体是否接通电源，都会获得 通电/断电 的状态。

        Args:
            is_on (bool): True 表示通电，False 表示断电。

        Returns:
            bool: 是否设置成功。
        """

    def set_power_status(self, is_on: bool) -> bool:
        """
        同步设置当前实体的通电状态。注意当该接口设置后，无论物体是否接通电源，都会获得 通电/断电 的状态。

        Args:
            is_on (bool): True 表示通电，False 表示断电。

        Returns:
            bool: 是否设置成功。
        """


@AbilityRegistry.register(PowerableAbility)
class PowerableAbilityImpl(AbilityImplBase):
    def __init__(self, entity: Entity):
        super().__init__(entity)
        self._object_state_component_id: str = entity.get_component_id(
            ComponentTags.OBJECT_STATE
        )

    @classmethod
    def is_applicable(cls, entity: Entity) -> bool:
        return entity.has_component_type(ComponentTags.OBJECT_STATE)

    async def async_get_power_status(self) -> bool:
        return await UnaryAPI.get_is_powered(
            self._context.conn, self._entity_id, self._object_state_component_id
        )

    def get_power_status(self) -> bool:
        return self._context.sync_run(self.async_get_power_status())

    async def async_set_power_status(self, is_on: bool) -> bool:
        return await UnaryAPI.set_is_powered(
            self._context.conn, self._object_state_component_id, is_on
        )

    def set_power_status(self, is_on: bool) -> bool:
        return self._context.sync_run(self.async_set_power_status(is_on))
