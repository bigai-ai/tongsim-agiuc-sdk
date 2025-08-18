"""
tongsim.entity.ability.impl.collision
"""

from typing import Protocol

from tongsim.connection.grpc import LegacyAPI
from tongsim.connection.tags import ComponentTags
from tongsim.entity.ability.base import AbilityImplBase
from tongsim.entity.ability.registry import AbilityRegistry
from tongsim.entity.entity import Entity
from tongsim.math import Box

from .scene import SceneAbility

__all__ = ["CollisionShapeAbility"]


class CollisionShapeAbility(Protocol):
    """
    提供对象的碰撞体信息的获取接口。
    """

    def get_relative_aabb(self) -> Box:
        """
        获取对象的相对 Box（同步接口）。

        注意：
            返回的 Box 是**相对于物体位置（location）**的本地包围盒。（默认 Scale 为 1）

        Returns:
            Box: 相对 Box（本地坐标系下）
        """

    async def async_get_relative_aabb(self) -> Box:
        """
        获取对象的相对 Box（异步接口）。

        注意：
            返回的 Box 是**相对于物体位置（location）**的本地包围盒。（默认 Scale 为 1）

        Returns:
            Box: 相对 Box（本地坐标系下）
        """

    def get_world_aabb(self) -> Box:
        """
        获取物体的世界空间 Box（同步接口）。

        Returns:
            Box: 绝对 Box（世界坐标系下）
        """

    async def async_get_world_aabb(self) -> Box:
        """
        获取物体的世界空间 Box（异步接口）。

        Returns:
            Box: 绝对 Box（世界坐标系下）
        """


@AbilityRegistry.register(CollisionShapeAbility)
class CollisionShapeAbilityImpl(AbilityImplBase):
    def __init__(self, entity: Entity):
        super().__init__(entity)
        self._owner_entity = entity

    @classmethod
    def is_applicable(cls, entity: Entity) -> bool:
        return entity.has_component_type(
            ComponentTags.COLLISION
        ) and entity.has_component_type(ComponentTags.POSE)

    def get_relative_aabb(self) -> Box:
        return self._context.sync_run(self.async_get_relative_aabb())

    async def async_get_relative_aabb(self) -> Box:
        min_vertex, max_vertex = await LegacyAPI.get_aabb(
            self._context.conn_legacy, self._entity_id
        )
        return Box(min_vertex, max_vertex)

    def get_world_aabb(self) -> Box:
        return self._context.sync_run(self.async_get_world_aabb())

    async def async_get_world_aabb(self) -> Box:
        relative_aabb = await self.async_get_relative_aabb()
        scene_ability = await self._owner_entity.async_as_(SceneAbility)
        transform = await scene_ability.async_get_transform()
        min = transform.transform_vector3(relative_aabb.min)
        max = transform.transform_vector3(relative_aabb.max)
        return Box(min, max)
