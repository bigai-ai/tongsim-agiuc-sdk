"""
tongsim.entity.ability.impl.interactable
"""

from typing import Protocol

from tongsim.connection.grpc import LegacyAPI, UnaryAPI
from tongsim.connection.tags import ComponentTags
from tongsim.entity.ability.base import AbilityImplBase
from tongsim.entity.ability.registry import AbilityRegistry
from tongsim.entity.entity import Entity
from tongsim.math import Vector3

__all__ = ["InteractableAbility"]


class InteractableAbility(Protocol):
    """
    InteractableAbility 定义了支持交互控制的实体能力接口。
    """

    async def async_get_active_state(self) -> bool:
        """
        异步获取当前实体的激活状态。注意如果一个电器没有通电，状态激活了也不会工作。

        Returns:
            bool: True 表示激活，False 表示未激活。
        """

    def get_active_state(self) -> bool:
        """
        同步获取当前实体的激活状态。注意如果一个电器没有通电，状态激活了也不会工作。

        Returns:
            bool: True 表示激活，False 表示未激活。
        """

    async def async_set_active_state(self, is_active: bool) -> bool:
        """
        异步设置当前实体的激活状态。注意如果一个电器没有通电，状态激活了也不会工作。

        Args:
            is_active (bool): True 表示激活，False 表示关闭。

        Returns:
            bool: 是否设置成功。
        """

    def set_active_state(self, is_active: bool) -> bool:
        """
        同步设置当前实体的激活状态。注意如果一个电器没有通电，状态激活了也不会工作。

        Args:
            is_active (bool): True 表示激活，False 表示关闭。

        Returns:
            bool: 是否设置成功。
        """

    async def async_get_interact_point(self) -> Vector3:
        """
        异步获取当前实体的交互点。依赖资产配置，若资产配置缺失，则返回 物体锚点。

        Returns:
            Vector3: 交互点的世界坐标。
        """

    def get_interact_point(self) -> Vector3:
        """
        同步获取当前实体的交互点信息。依赖资产配置，若资产配置缺失，则返回 物体锚点。

        Returns:
            Vector3: 交互点的世界坐标。
        """

    async def async_get_group_id(self) -> str:
        """
        异步获取当前实体的分组 ID。

        Returns:
            str: 分组 ID。
        """

    def get_group_id(self) -> str:
        """
        同步获取当前实体的分组 ID。

        Returns:
            str: 分组 ID。
        """

    async def async_get_entity_ids_in_same_group(self) -> list[str]:
        """
        异步获取同一分组内所有实体的 ID。

        Returns:
            list[str]: 实体 ID 列表。
        """

    def get_entity_ids_in_same_group(self) -> list[str]:
        """
        同步获取同一分组内所有实体的 ID。

        Returns:
            list[str]: 实体 ID 列表。
        """

    async def async_set_group_id(self, new_group_id: str) -> bool:
        """
        异步设置当前实体的分组 ID。

        Args:
            new_group_id (str): 新的分组 ID。

        Returns:
            bool: 是否设置成功。
        """

    def set_group_id(self, new_group_id: str) -> bool:
        """
        同步设置当前实体的分组 ID。

        Args:
            new_group_id (str): 新的分组 ID。

        Returns:
            bool: 是否设置成功。
        """

    def is_working(self) -> bool:
        """
        同步获取当前实体是否正在运作（例如电器是否正在工作）。

        Returns:
            bool: True 表示正在工作，False 表示未工作。
        """

    async def async_is_working(self) -> bool:
        """
        异步获取当前实体是否正在运作（例如电器是否正在工作）。

        Returns:
            bool: True 表示正在工作，False 表示未工作。
        """

    async def async_get_place_point(self) -> Vector3:
        """
        异步获取当前实体的配置的放置点。依赖资产配置，若资产配置缺失，则返回物体锚点。
        举例:
        - 获取 饮水机接水时 的 水杯放置位置
        - 获取 够不着的水龙头交互时 的 凳子放置位置

        Returns:
            Vector3: 交互点的世界坐标。
        """

    def get_place_point(self) -> Vector3:
        """
        同步获取当前实体的配置的放置点。依赖资产配置，若资产配置缺失，则返回物体锚点。
        举例:
        - 获取 饮水机接水时 的 水杯放置位置
        - 获取 够不着的水龙头交互时 的 凳子放置位置

        Returns:
            Vector3: 交互点的世界坐标。
        """

    async def async_set_ui_text(self, text: str) -> bool:
        """
        设置一个物体显示的文本，如支持文本显示功能
        举例:
        - 设置密码锁显示文本

        Args:
            text (str): 需要显示的文本。

        Returns:
            bool: 成功与否。
        """

    def set_ui_text(self, text: str) -> bool:
        """
        设置一个物体显示的文本，如支持文本显示功能
        举例:
        - 设置密码锁显示文本

        Args:
            text (str): 需要显示的文本。

        Returns:
            bool: 成功与否。
        """


@AbilityRegistry.register(InteractableAbility)
class InteractableAbilityImpl(AbilityImplBase):
    def __init__(self, entity: Entity):
        super().__init__(entity)
        self._object_state_component_id: str = entity.get_component_id(
            ComponentTags.OBJECT_STATE
        )

    @classmethod
    def is_applicable(cls, entity: Entity) -> bool:
        return entity.has_component_type(ComponentTags.OBJECT_STATE)

    async def async_get_active_state(self) -> bool:
        return await UnaryAPI.get_active_state(
            self._context.conn, self._entity_id, self._object_state_component_id
        )

    def get_active_state(self) -> bool:
        return self._context.sync_run(self.async_get_active_state())

    async def async_set_active_state(self, is_active: bool) -> bool:
        return await LegacyAPI.set_object_state(
            self._context.conn_legacy, self._entity_id, is_active
        )

    def set_active_state(self, is_active: bool) -> bool:
        return self._context.sync_run(self.async_set_active_state(is_active))

    async def async_get_interact_point(self) -> Vector3:
        return await UnaryAPI.get_interact_location(
            self._context.conn, self._entity_id, self._object_state_component_id
        )

    def get_interact_point(self) -> Vector3:
        return self._context.sync_run(self.async_get_interact_point())

    async def async_get_group_id(self) -> str:
        return await UnaryAPI.get_group_id(
            self._context.conn, self._entity_id, self._object_state_component_id
        )

    def get_group_id(self) -> str:
        return self._context.sync_run(self.async_get_group_id())

    async def async_get_entity_ids_in_same_group(self) -> list[str]:
        return await UnaryAPI.get_entity_ids_in_same_group(
            self._context.conn, self._entity_id, self._object_state_component_id
        )

    def get_entity_ids_in_same_group(self) -> list[str]:
        return self._context.sync_run(self.async_get_entity_ids_in_same_group())

    async def async_set_group_id(self, new_group_id: str) -> bool:
        # return await UnaryAPI.set_group_id(
        #     self._context.conn, self._object_state_component_id, new_group_id
        # )
        return await LegacyAPI.set_group_id(
            self._context.conn_legacy, self._entity_id, new_group_id
        )

    def set_group_id(self, new_group_id: str) -> bool:
        return self._context.sync_run(self.async_set_group_id(new_group_id))

    async def async_is_working(self) -> bool:
        # TODO: 当前实现依赖 is_powered 默认返回为 True, 跳过了判断一个物体是否时带有 电源组件的 物体
        is_powered = await UnaryAPI.get_is_powered(
            self._context.conn, self._entity_id, self._object_state_component_id
        )
        is_active_state = await self.async_get_active_state()
        return is_powered and is_active_state

    def is_working(self) -> bool:
        return self._context.sync_run(self.async_is_working())

    async def async_get_place_point(self) -> Vector3:
        return await UnaryAPI.get_place_location(
            self._context.conn, self._entity_id, self._object_state_component_id
        )

    def get_place_point(self) -> Vector3:
        return self._context.sync_run(self.async_get_place_point())

    async def async_set_ui_text(self, text: str) -> bool:
        return await UnaryAPI.set_ui_text(
            self._context.conn, self._object_state_component_id, text
        )

    def set_ui_text(self, text: str) -> bool:
        return self._context.sync_run(self.async_set_ui_text(text))
