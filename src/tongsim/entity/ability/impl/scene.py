# tongsim/entity/ability/impl/scene.py

from typing import Protocol

from tongsim.connection.grpc import LegacyAPI, UnaryAPI
from tongsim.connection.tags import ComponentTags
from tongsim.entity.ability.base import AbilityImplBase
from tongsim.entity.ability.registry import AbilityRegistry
from tongsim.entity.entity import Entity
from tongsim.math.geometry import Pose, Quaternion, Transform, Vector3


class SceneAbility(Protocol):
    """
    空间能力接口，提供 Entity 的位置、旋转、朝向向量等能力。
    """

    def get_pose(self) -> Pose:
        """
        获取 Entity 的当前位置和旋转姿态（同步接口）。

        Returns:
            Pose: 实体的位姿（位置 + 旋转）。
        """

    async def async_get_pose(self) -> Pose:
        """
        获取 Entity 的当前位置和旋转姿态（异步接口）。

        Returns:
            Pose: 实体的位姿（位置 + 旋转）。
        """

    def set_pose(self, pose: Pose) -> bool:
        """
        设置 Entity 的位置与旋转。

        Args:
            pose (Pose): 目标位姿。

        Returns:
            bool: 设置是否成功。
        """

    async def async_set_pose(self, pose: Pose) -> bool:
        """
        设置 Entity 的位置与旋转（异步接口）。

        Args:
            pose (Pose): 目标位姿。

        Returns:
            bool: 设置是否成功。
        """

    def get_location(self) -> Vector3:
        """
        获取 Entity 的当前位置（同步接口）。

        Returns:
            Vector3: 当前位置。
        """

    async def async_get_location(self) -> Vector3:
        """
        获取 Entity 的当前位置（异步接口）。

        Returns:
            Vector3: 当前位置。
        """

    def set_location(self, location: Vector3) -> bool:
        """
        设置 Entity 的位置，保持原有旋转不变。

        Args:
            location (Vector3): 新位置。

        Returns:
            bool: 设置是否成功。
        """

    def get_rotation(self) -> Quaternion:
        """
        获取 Entity 当前的旋转（同步接口）。

        Returns:
            Quaternion: 当前旋转（四元数）。
        """

    def set_rotation(self, rotation: Quaternion) -> bool:
        """
        设置 Entity 的旋转，保持原有位置不变。

        Args:
            rotation (Quaternion): 新的旋转（四元数）。

        Returns:
            bool: 设置是否成功。
        """

    def get_forward_vector(self) -> Vector3:
        """
        获取 Entity 的朝前方向向量（同步接口）。

        Returns:
            Vector3: 单位向量，表示前方方向。
        """

    async def async_get_forward_vector(self) -> Vector3:
        """
        获取 Entity 的朝前方向向量（异步接口）。

        Returns:
            Vector3: 单位向量，表示前方方向。
        """

    def get_right_vector(self) -> Vector3:
        """
        获取 Entity 的右方方向向量（同步接口）。

        Returns:
            Vector3: 单位向量，表示右方方向。
        """

    async def async_get_right_vector(self) -> Vector3:
        """
        获取 Entity 的右方方向向量（异步接口）。

        Returns:
            Vector3: 单位向量，表示右方方向。
        """

    def get_object_direction(self) -> Vector3:
        """
        用来获取 镜子、柜子 等物体的面朝方向。资产配置 右方方向 为面朝正方向，此接口底层返回 RightVector

        Returns:
            Vector3: 单位向量
        """

    async def async_get_object_direction(self) -> Vector3:
        """
        用来获取 镜子、柜子 等物体的面朝方向。资产配置 右方方向 为面朝正方向，此接口底层返回 RightVector

        Returns:
            Vector3: 单位向量
        """

    def get_scale(self) -> Vector3:
        """
        获取 Entity 的当前缩放（同步接口）。

        Returns:
            Vector3: 当前缩放。
        """

    async def async_get_scale(self) -> Vector3:
        """
        获取 Entity 的当前缩放（异步接口）。

        Returns:
            Vector3: 当前缩放。
        """

    def set_scale(self, new_scale: Vector3) -> bool:
        """
        设置 Entity 的缩放。

        Args:
            new_scale (Vector3): 新的缩放值。

        Returns:
            bool: 设置是否成功。
        """

    async def async_set_scale(self, new_scale: Vector3) -> bool:
        """
        设置 Entity 的缩放（异步接口）。

        Args:
            new_scale (Vector3): 新的缩放值。

        Returns:
            bool: 设置是否成功。
        """

    def get_transform(self) -> Transform:
        """
        获取 Entity 的完整变换信息（位置、旋转、缩放）（同步接口）。

        Returns:
            Transform: 完整的变换信息。
        """

    async def async_get_transform(self) -> Transform:
        """
        获取 Entity 的完整变换信息（位置、旋转、缩放）（异步接口）。

        Returns:
            Transform: 完整的变换信息。
        """


@AbilityRegistry.register(SceneAbility)
class SceneAbilityImpl(AbilityImplBase):
    def __init__(self, entity: Entity):
        super().__init__(entity)
        self._pose_component_id: str = entity.get_component_id(ComponentTags.POSE)
        self._is_scalable = entity.has_component_type(ComponentTags.SCALE)

    @classmethod
    def is_applicable(cls, entity: Entity) -> bool:
        return entity.has_component_type(ComponentTags.POSE)

    def get_pose(self) -> Pose:
        return self._context.sync_run(self.async_get_pose())

    async def async_get_pose(self) -> Pose:
        return await LegacyAPI.get_pose(self._context.conn_legacy, self._entity_id)

    def set_pose(self, pose: Pose) -> bool:
        return self._context.sync_run(self.async_set_pose(pose))

    async def async_set_pose(self, pose: Pose) -> bool:
        return await LegacyAPI.set_pose(
            self._context.conn_legacy, self._entity_id, pose
        )

    def get_location(self) -> Vector3:
        return self.get_pose().location

    async def async_get_location(self) -> Vector3:
        pose = await self.async_get_pose()
        return pose.location

    def set_location(self, location: Vector3) -> bool:
        current = self.get_pose()
        return self.set_pose(Pose(location, current.rotation))

    def get_rotation(self) -> Quaternion:
        return self.get_pose().rotation

    def set_rotation(self, rotation: Quaternion) -> bool:
        current = self.get_pose()
        return self.set_pose(Pose(current.location, rotation))

    def get_forward_vector(self) -> Vector3:
        return self._context.sync_run(self.async_get_forward_vector())

    async def async_get_forward_vector(self) -> Vector3:
        return await UnaryAPI.get_forward_vector(
            self._context.conn,
            subject_id=self._entity_id,
            component_id=self._pose_component_id,
        )

    def get_right_vector(self) -> Vector3:
        return self._context.sync_run(self.async_get_right_vector())

    async def async_get_right_vector(self) -> Vector3:
        return await UnaryAPI.get_right_vector(
            self._context.conn,
            subject_id=self._entity_id,
            component_id=self._pose_component_id,
        )

    def get_object_direction(self) -> Vector3:
        return self._context.sync_run(self.async_get_right_vector())

    async def async_get_object_direction(self) -> Vector3:
        return await UnaryAPI.get_right_vector(
            self._context.conn,
            subject_id=self._entity_id,
            component_id=self._pose_component_id,
        )

    def get_scale(self) -> Vector3:
        return self._context.sync_run(self.async_get_scale())

    async def async_get_scale(self) -> Vector3:
        if self._is_scalable:
            return await LegacyAPI.get_scale(self._context.conn_legacy, self._entity_id)
        return Vector3(1.0, 1.0, 1.0)

    def set_scale(self, new_scale: Vector3) -> bool:
        return self._context.sync_run(self.async_set_scale(new_scale))

    async def async_set_scale(self, new_scale: Vector3) -> bool:
        return await LegacyAPI.set_scale(
            self._context.legacy_stream_client, self._entity_id, new_scale
        )

    def get_transform(self) -> Transform:
        return self._context.sync_run(self.async_get_transform())

    async def async_get_transform(self) -> Transform:
        pose = await self.async_get_pose()
        scale = await self.async_get_scale()
        # 组合成 Transform
        return Transform(pose.location, pose.rotation, scale)
