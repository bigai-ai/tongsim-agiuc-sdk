"""
tongsim.entity.ability.impl.consumable_energy
"""

from typing import Protocol

from tongsim.connection.grpc import LegacyAPI
from tongsim.connection.tags import ComponentTags
from tongsim.entity.ability.base import AbilityImplBase
from tongsim.entity.ability.registry import AbilityRegistry
from tongsim.entity.entity import Entity

__all__ = ["ConsumableEnergyAbility"]


class ConsumableEnergyAbility(Protocol):
    """
    ConsumableEnergyAbility 定义了食物与饮品能量管理的接口。

    支持能量读取与设置，包括食物类型和饮品类型。
    """

    async def async_get_consumable_energy(self) -> tuple[float, float]:
        """
        异步获取当前实体的抗饥饿值与抗口渴值。

        Returns:
            tuple[float, float]: (anti_hungry, anti_thirsty)
        """

    def get_consumable_energy(self) -> tuple[float, float]:
        """
        同步获取当前实体的抗饥饿值与抗口渴值。

        Returns:
            tuple[float, float]: (anti_hungry, anti_thirsty)
        """

    async def async_set_edible_energy(
        self, anti_hungry: float, anti_thirsty: float, max_parts: int
    ) -> bool:
        """
        异步设置当前实体的可食用能量值。

        Args:
            anti_hungry (float): 抗饥饿值, 代表吃下该实体后, agent 的饥饿值会上升多少。范围: 0.0 ~ 2.0, agent 的饥饿值范围为 -1.0 ~ 1.0。 -1.0 代表完全饱腹
            anti_thirsty (float): 抗口渴值, 代表吃下该实体后, agent 的口渴值会上升多少。范围: 0.0 ~ 2.0, agent 的口渴值范围为 -1.0 ~ 1.0。 -1.0 代表水分充足
            max_parts (int): 吃完需要吃几口

        Returns:
            bool: 是否成功。
        """

    def set_edible_energy(
        self, anti_hungry: float, anti_thirsty: float, max_parts: int
    ) -> bool:
        """
        同步设置当前实体的可食用能量值。

        Args:
            anti_hungry (float): 抗饥饿值, 代表吃下该实体后, agent 的饥饿值会上升多少。范围: 0.0 ~ 2.0, agent 的饥饿值范围为 -1.0 ~ 1.0。 -1.0 代表完全饱腹
            anti_thirsty (float): 抗口渴值, 代表吃下该实体后, agent 的口渴值会上升多少。范围: 0.0 ~ 2.0, agent 的口渴值范围为 -1.0 ~ 1.0。 -1.0 代表水分充足
            max_parts (int): 喝完需要喝几口

        Returns:
            bool: 是否成功。
        """

    async def async_set_beverage_energy(
        self, anti_hungry: float, anti_thirsty: float, max_parts: int
    ) -> bool:
        """
        异步设置当前实体的可饮用能量值。

        Args:
            anti_hungry (float): 抗饥饿值, 代表喝下该实体后, agent 的饥饿值会上升多少。范围: 0.0 ~ 2.0, agent 的饥饿值范围为 -1.0 ~ 1.0。 -1.0 代表完全饱腹
            anti_thirsty (float): 抗口渴值, 代表喝下该实体后, agent 的口渴值会上升多少。范围: 0.0 ~ 2.0, agent 的口渴值范围为 -1.0 ~ 1.0。 -1.0 代表水分充足
            max_parts (int): 喝完需要喝几口

        Returns:
            bool: 是否成功。
        """

    def set_beverage_energy(
        self, anti_hungry: float, anti_thirsty: float, max_parts: int
    ) -> bool:
        """
        同步设置当前实体的可饮用能量值。

        Args:
            anti_hungry (float): 抗饥饿值, 代表喝下该实体后, agent 的饥饿值会上升多少。范围: 0.0 ~ 2.0, agent 的饥饿值范围为 -1.0 ~ 1.0。 -1.0 代表完全饱腹
            anti_thirsty (float): 抗口渴值, 代表喝下该实体后, agent 的口渴值会上升多少。范围: 0.0 ~ 2.0, agent 的口渴值范围为 -1.0 ~ 1.0。 -1.0 代表水分充足
            max_parts (int): 喝完需要喝几口

        Returns:
            bool: 是否成功。
        """


@AbilityRegistry.register(ConsumableEnergyAbility)
class ConsumableEnergyAbilityImpl(AbilityImplBase):
    @classmethod
    def is_applicable(cls, entity: Entity) -> bool:
        return entity.has_component_type(ComponentTags.FOOD_ENERGY)

    async def async_get_consumable_energy(self) -> tuple[float, float]:
        return await LegacyAPI.get_food_energy(
            self._context.conn_legacy, self._entity_id
        )

    def get_consumable_energy(self) -> tuple[float, float]:
        return self._context.sync_run(self.async_get_consumable_energy())

    async def async_set_edible_energy(
        self, anti_hungry: float, anti_thirsty: float, max_parts: int
    ) -> bool:
        return await LegacyAPI.set_eatable_energy(
            self._context.legacy_stream_client,
            self._entity_id,
            anti_hungry,
            anti_thirsty,
            max_parts,
        )

    def set_edible_energy(
        self, anti_hungry: float, anti_thirsty: float, max_parts: int
    ) -> bool:
        return self._context.sync_run(
            self.async_set_edible_energy(anti_hungry, anti_thirsty, max_parts)
        )

    async def async_set_beverage_energy(
        self, anti_hungry: float, anti_thirsty: float, max_parts: int
    ) -> bool:
        return await LegacyAPI.set_drinkable_energy(
            self._context.legacy_stream_client,
            self._entity_id,
            anti_hungry,
            anti_thirsty,
            max_parts,
        )

    def set_beverage_energy(
        self, anti_hungry: float, anti_thirsty: float, max_parts: int
    ) -> bool:
        return self._context.sync_run(
            self.async_set_beverage_energy(anti_hungry, anti_thirsty, max_parts)
        )
