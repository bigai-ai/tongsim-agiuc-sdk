"""
tongsim.entity.ability.impl.asset
"""

from typing import Protocol

from tongsim.connection.grpc import UnaryAPI
from tongsim.connection.tags import ComponentTags
from tongsim.entity.ability.base import AbilityImplBase
from tongsim.entity.ability.registry import AbilityRegistry
from tongsim.entity.entity import Entity

__all__ = ["AssetAbility"]


class AssetAbility(Protocol):
    """
    提供对象的资产配置信息的获取接口。
    """

    def get_asset_name(self) -> str:
        """
        获取对象绑定的资产名称（同步接口）。

        Returns:
            str: 资产名称
        """

    async def async_get_asset_name(self) -> str:
        """
        获取对象绑定的资产名称（异步接口）。

        Returns:
            str: 资产名称
        """

    def get_type(self) -> str:
        """
        获取该对象的配置的类型（同步接口）。

        Returns:
            str: 类型名称
        """

    async def async_get_type(self) -> str:
        """
        获取该对象配置的类型（异步接口）。

        Returns:
            str: 类型名称
        """


@AbilityRegistry.register(AssetAbility)
class AssetAbilityImpl(AbilityImplBase):
    def __init__(self, entity: Entity):
        super().__init__(entity)
        self._object_state_component_id: str = entity.get_component_id(
            ComponentTags.OBJECT_STATE
        )

    @classmethod
    def is_applicable(cls, entity: Entity) -> bool:
        return entity.has_component_type(ComponentTags.OBJECT_STATE)

    def get_asset_name(self) -> str:
        return self._context.sync_run(self.async_get_asset_name())

    async def async_get_asset_name(self) -> str:
        return await UnaryAPI.get_asset_name(
            self._context.conn,
            subject_id=self._entity_id,
            component_id=self._object_state_component_id,
        )

    def get_type(self) -> str:
        return self._context.sync_run(self.async_get_type())

    async def async_get_type(self) -> str:
        return await UnaryAPI.get_type(
            self._context.conn, self._entity_id, self._object_state_component_id
        )
