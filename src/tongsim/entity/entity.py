from collections import defaultdict
from typing import Final, TypeVar

from tongsim.connection.grpc.unary_api import UnaryAPI
from tongsim.connection.tags import ComponentType
from tongsim.core.world_context import WorldContext
from tongsim.logger import get_logger

from .ability.registry import AbilityRegistry

_logger = get_logger("entity")

T = TypeVar("T")


class Entity:
    """
    Entity 类代表一个 TongSim 世界中的对象

    类的职责包括:

    - 管理组件 ID，按组件类型分类
    - 提供能力（Ability）访问与转换机制

    注意: Entity 不直接持有组件数据，仅维护 component_id 结构。
    """

    __slots__ = ("_ability_cache", "_components", "_id", "_world_context")

    def __init__(
        self,
        entity_id: str,
        world_context: WorldContext,
        components: dict[ComponentType, list[str]],
    ):
        self._id: Final[str] = entity_id
        self._world_context: Final[WorldContext] = world_context
        self._components: dict[ComponentType, list[str]] = components
        self._ability_cache: dict[type, object] = {}  # 缓存已创建的 Impl 实例

    @property
    def id(self):
        return self._id

    @property
    def context(self):
        return self._world_context

    @classmethod
    async def from_grpc(cls, entity_id: str, world_context: WorldContext) -> "Entity":
        """
        通过 gRPC 查询构造 Entity。

        :param conn: GrpcConnection
        :param entity_id: Entity 唯一 ID
        :return: Entity 实例
        """
        resp = await UnaryAPI.query_components(world_context.conn, entity_id)
        if resp is None:
            raise RuntimeError(f"Failed to query components for entity '{entity_id}'.")

        components: dict[ComponentType, list[str]] = defaultdict(list)
        for component_id, component_type in resp.items():
            components[component_type].append(component_id)

        _logger.debug(
            f"[Consturct entity from gRPC] Entity {entity_id}  ---  component-types: {list(components.keys())}"
        )
        return cls(entity_id, world_context, components)

    # TODO: from PG

    def get_components_id_list(self, component_type: ComponentType) -> list[str]:
        """
        获取指定类型的所有组件 ID。

        :param component_type: 组件类型（如 "CamParamComponent"）
        :return: 组件 ID 列表（可能为空）
        """
        return self._components.get(component_type, [])

    def get_component_id(self, component_type: ComponentType) -> str:
        """
        获取指定类型的第一个组件 ID（如果存在）。

        :param component_type: 组件类型
        :return: 组件 ID
        :raises: KeyError 如果组件不存在
        """
        comps = self._components.get(component_type, [])
        if not comps:
            raise KeyError(
                f"Entity '{self._id}' has no component of type '{component_type}'."
            )
        return comps[0]

    def has_component_type(self, component_type: ComponentType) -> bool:
        """
        判断是否拥有指定类型的组件。

        Args:
            component_type (ComponentType): 组件类型（如 "Camera"）

        Returns:
            bool: 是否拥有该类型的组件。
        """
        return bool(self._components.get(component_type))

    def has_component_id(self, component_id: str) -> bool:
        """
        判断是否包含指定组件 ID。

        Args:
            component_id (str): 要检查的组件唯一 ID

        Returns:
            bool: 是否包含该组件 ID。
        """
        return any(component_id in ids for ids in self._components.values())

    def has_ability(self, ability_type: type[T]) -> bool:
        """
        判断该 Entity 是否支持指定的能力接口（Ability）。

        Args:
            ability_type (type[T]): 能力类型（Protocol）

        Returns:
            bool: 是否支持该能力
        """
        impl_cls = AbilityRegistry.get_impl(ability_type)
        return impl_cls is not None and impl_cls.is_applicable(self)

    def as_(self, ability_type: type[T]) -> T:
        """
        将 Entity 同步转换为具备指定能力的对象（Ability 实现类）。

        注意:
            - 本方法为同步封装，内部通过 `sync_run` 调用异步的 `async_as_`。
            - 若在事件循环线程内调用此方法，可能会导致死锁，应优先使用 `async_as_`。

        Args:
            ability_type (type[T]): 能力接口类型（Protocol）。

        Returns:
            T: 实现了该能力的能力对象实例。

        Raises:
            RuntimeError: 如果能力未注册，或当前 Entity 不支持该能力。
        """
        return self._world_context.sync_run(self.async_as_(ability_type=ability_type))

    async def async_as_(self, ability_type: type[T]) -> T:
        """
        异步地将 Entity 转换为具备指定能力的对象（Ability 实现类）。

        本方法通过能力注册表获取对应的实现类，并进行初始化绑定。
        若已缓存能力实例，将直接返回缓存。

        Args:
            ability_type (type[T]): 能力接口类型（Protocol）。

        Returns:
            T: 实现了该能力的能力对象实例。

        Raises:
            RuntimeError: 如果未注册该能力，或当前 Entity 不具备该能力要求。
        """
        if ability_type in self._ability_cache:
            return self._ability_cache[ability_type]

        impl_cls = AbilityRegistry.get_impl_cls(ability_type)
        if impl_cls is None:
            raise RuntimeError(f"Ability {ability_type.__name__} not registered.")

        if not impl_cls.is_applicable(self):
            raise RuntimeError(
                f"Entity '{self._id}' does not support ability {ability_type.__name__}."
            )

        impl = await impl_cls.create(self)
        self._ability_cache[ability_type] = impl
        return impl

    def __repr__(self) -> str:
        return (
            f"Entity(id: {self._id}   component-types: {list(self._components.keys())})"
        )
