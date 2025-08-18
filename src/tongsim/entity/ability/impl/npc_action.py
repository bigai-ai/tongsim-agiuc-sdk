"""
tongsim.entity.ability.impl.npc_action
"""

from typing import Protocol

from tongsim.connection.grpc import UnaryAPI
from tongsim.entity.ability.base import AbilityImplBase
from tongsim.entity.ability.registry import AbilityRegistry
from tongsim.entity.entity import Entity
from tongsim.math import Quaternion, Vector3

__all__ = ["NPCActionAbility"]


class NPCActionAbility(Protocol):
    """
    提供 NPC 行为能力接口，支持移动、播放动画、转向、拾取与放下物体等操作。

    本能力接口定义了同步与异步版本，便于在不同调度上下文中调用。
    """

    def move_to_location(self, location: Vector3) -> bool:
        """
        让 NPC 移动到指定的世界坐标位置。

        Args:
            location (Vector3): 目标世界坐标。

        Returns:
            bool: 操作是否成功。
        """

    async def async_move_to_location(self, location: Vector3) -> bool:
        """
        异步版本：让 NPC 移动到指定的世界坐标位置。

        Args:
            location (Vector3): 目标世界坐标。

        Returns:
            bool: 操作是否成功。
        """

    def play_animation(self, anim_name: str) -> bool:
        """
        让 NPC 播放指定名称的动画。

        Args:
            anim_name (str): 动画名称。

        Returns:
            bool: 操作是否成功。
        """

    async def async_play_animation(self, anim_name: str) -> bool:
        """
        异步版本：让 NPC 播放指定名称的动画。

        Args:
            anim_name (str): 动画名称。

        Returns:
            bool: 操作是否成功。
        """

    def turn_around_to_object(self, object_id: str) -> bool:
        """
        让 NPC 面向指定对象进行转向。

        Args:
            object_id (str): 目标对象 ID。

        Returns:
            bool: 操作是否成功。
        """

    async def async_turn_around_to_object(self, object_id: str) -> bool:
        """
        异步版本：让 NPC 面向指定对象进行转向。

        Args:
            object_id (str): 目标对象 ID。

        Returns:
            bool: 操作是否成功。
        """

    def turn_around_to_location(self, location: Vector3) -> bool:
        """
        让 NPC 面向指定坐标点进行转向。

        Args:
            location (Vector3): 目标坐标。

        Returns:
            bool: 操作是否成功。
        """

    async def async_turn_around_to_location(self, location: Vector3) -> bool:
        """
        异步版本：让 NPC 面向指定坐标点进行转向。

        Args:
            location (Vector3): 目标坐标。

        Returns:
            bool: 操作是否成功。
        """

    def turn_around_degree(self, degree: float) -> bool:
        """
        让 NPC 进行指定角度的旋转（朝向不变，仅旋转）。

        Args:
            degree (float): 相对旋转角度（单位：度）。

        Returns:
            bool: 操作是否成功。
        """

    async def async_turn_around_degree(self, degree: float) -> bool:
        """
        异步版本：让 NPC 进行指定角度的旋转（朝向不变，仅旋转）。

        Args:
            degree (float): 相对旋转角度（单位：度）。

        Returns:
            bool: 操作是否成功。
        """

    def pick_up(self, object_id: str) -> bool:
        """
        让 NPC 拾取指定对象。

        Args:
            object_id (str): 要拾取的对象 ID。

        Returns:
            bool: 操作是否成功。
        """

    async def async_pick_up(self, object_id: str) -> bool:
        """
        异步版本：让 NPC 拾取指定对象。

        Args:
            object_id (str): 要拾取的对象 ID。

        Returns:
            bool: 操作是否成功。
        """

    def put_down(
        self, object_id: str, location: Vector3, rotation: Quaternion | None = None
    ) -> bool:
        """
        让 NPC 在指定位置和旋转角度放下对象。

        Args:
            object_id (str): 要放下的对象 ID。
            location (Vector3): 对象需要放在的位置。
            rotation (Quaternion): 对象放下后，对象的旋转。

        Returns:
            bool: 操作是否成功。
        """

    async def async_put_down(
        self,
        object_id: str,
        location: Vector3,
        rotation: Quaternion | None = None,
    ) -> bool:
        """
        异步版本：让 NPC 在指定位置和旋转角度放下对象。

        Args:
            object_id (str): 要放下的对象 ID。
            location (Vector3): 对象需要放在的位置。
            rotation (Quaternion): 对象放下后，对象的旋转。

        Returns:
            bool: 操作是否成功。
        """


@AbilityRegistry.register(NPCActionAbility)
class NPCActionAbilityImpl(AbilityImplBase):
    def __init__(self, entity: Entity):
        super().__init__(entity)

    @classmethod
    def is_applicable(cls, entity: Entity) -> bool:
        return True

    def move_to_location(self, location: Vector3) -> bool:
        return self._context.sync_run(self.async_move_to_location(location))

    async def async_move_to_location(self, location: Vector3) -> bool:
        return await UnaryAPI.npc_moveto_location(
            self._context.conn, npc_id=self._entity_id, location=location
        )

    def play_animation(self, anim_name: str) -> bool:
        return self._context.sync_run(self.async_play_animation(anim_name))

    async def async_play_animation(self, anim_name: str) -> bool:
        return await UnaryAPI.npc_play_animation(
            self._context.conn, npc_id=self._entity_id, anim_name=anim_name
        )

    def turn_around_to_object(self, object_id: str) -> bool:
        return self._context.sync_run(self.async_turn_around_to_object(object_id))

    async def async_turn_around_to_object(self, object_id: str) -> bool:
        return await UnaryAPI.npc_turnaround(
            self._context.conn,
            npc_id=self._entity_id,
            object_id=object_id,
        )

    def turn_around_to_location(self, location: Vector3) -> bool:
        return self._context.sync_run(self.async_turn_around_to_location(location))

    async def async_turn_around_to_location(self, location: Vector3) -> bool:
        return await UnaryAPI.npc_turnaround(
            self._context.conn,
            npc_id=self._entity_id,
            location=location,
        )

    def turn_around_degree(self, degree: float) -> bool:
        return self._context.sync_run(self.async_turn_around_degree(degree))

    async def async_turn_around_degree(self, degree: float) -> bool:
        return await UnaryAPI.npc_turnaround(
            self._context.conn,
            npc_id=self._entity_id,
            degree=degree,
        )

    def pick_up(self, object_id: str) -> bool:
        return self._context.sync_run(self.async_pick_up(object_id))

    async def async_pick_up(self, object_id: str) -> bool:
        return await UnaryAPI.npc_pickup(
            self._context.conn,
            npc_id=self._entity_id,
            object_id=object_id,
        )

    def put_down(
        self, object_id: str, location: Vector3, rotation: Quaternion | None = None
    ) -> bool:
        return self._context.sync_run(
            self.async_put_down(object_id, location, rotation)
        )

    async def async_put_down(
        self,
        object_id: str,
        location: Vector3,
        rotation: Quaternion | None = None,
    ) -> bool:
        if rotation is None:
            rotation = Quaternion()
        return await UnaryAPI.npc_putdown(
            self._context.conn,
            npc_id=self._entity_id,
            object_id=object_id,
            location=location,
            rotation=rotation,
        )
