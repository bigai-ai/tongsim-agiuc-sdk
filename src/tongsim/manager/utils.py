from tongsim.connection.grpc import UnaryAPI
from tongsim.core.world_context import WorldContext
from tongsim.logger import get_logger
from tongsim.math.geometry import Quaternion, Vector3

_logger = get_logger("utils")


class UtilFuncs:
    """
    通用工具函数集合，用于执行一些常见的模拟操作。
    """

    def __init__(self, world_context: WorldContext):
        self._context: WorldContext = world_context

    def open_all_passable_doors(self) -> bool:
        """
        同步打开场景中所有可通行的门。

        Returns:
            bool: 如果成功找到并打开了至少一扇门，则返回 True，否则返回 False。
        """
        return self._context.sync_run(self.async_open_all_passable_doors())

    async def async_open_all_passable_doors(self) -> bool:
        """
        异步打开场景中所有可通行的门。

        Returns:
            bool: 如果成功找到并打开了至少一扇门，则返回 True，否则返回 False。
        """
        door_components = await UnaryAPI.get_all_passable_doors(self._context.conn)
        if not door_components:
            _logger.warning("There is no passable door in current level.")
            return False

        for door_comp in door_components:
            await UnaryAPI.set_door_state(self._context.conn, door_comp, 1.0)

        return True

    def get_subjects_in_view_frustum_with_aabb_culling(
        self,
        camera_loc: Vector3,
        camera_rot: Quaternion,
        fov: float = 90.0,
        view_width: float = 1280.0,
        view_height: float = 720.0,
        depthbuffer_width: int | None = None,
        depthbuffer_height: int | None = None,
        near_clip: float = 0.0,
        far_clip: float = 2097152.0,
    ) -> list[str]:
        """
        同步获取视锥体内并通过 AABB 剔除的实体 ID 列表。

        Args:
            camera_loc (Vector3): 相机的世界位置。
            camera_rot (Quaternion): 相机的世界旋转。
            fov (float): 相机视场角（单位：度）。默认值为 90.0。
            view_width (float): 视口宽度（像素）。默认值为 1280。
            view_height (float): 视口高度（像素）。默认值为 720。
            depthbuffer_width (int | None): 深度图宽度，默认自动推算为 view_width 的 10%。
            depthbuffer_height (int | None): 深度图高度，默认自动推算为 view_height 的 10%。
            near_clip (float): 近裁剪面距离。默认值为 0.0。
            far_clip (float): 远裁剪面距离。默认值为 2097152.0。

        Returns:
            list[str]: 当前视锥体内的实体 ID 列表。
        """
        return self._context.sync_run(
            self.async_get_subjects_in_view_frustum_with_aabb_culling(
                camera_loc=camera_loc,
                camera_rot=camera_rot,
                fov=fov,
                view_width=view_width,
                view_height=view_height,
                depthbuffer_width=depthbuffer_width,
                depthbuffer_height=depthbuffer_height,
                near_clip=near_clip,
                far_clip=far_clip,
            )
        )

    async def async_get_subjects_in_view_frustum_with_aabb_culling(
        self,
        camera_loc: Vector3,
        camera_rot: Quaternion,
        fov: float = 90.0,
        view_width: float = 1280.0,
        view_height: float = 720.0,
        depthbuffer_width: int | None = None,
        depthbuffer_height: int | None = None,
        near_clip: float = 0.0,
        far_clip: float = 2097152.0,
    ) -> list[str]:
        """
        异步获取视锥体内并通过 AABB 剔除的实体 ID 列表。

        Args:
            camera_loc (Vector3): 相机的世界位置。
            camera_rot (Quaternion): 相机的世界旋转。
            fov (float): 相机视场角（单位：度）。默认值为 90.0。
            view_width (float): 视口宽度（像素）。默认值为 1280。
            view_height (float): 视口高度（像素）。默认值为 720。
            depthbuffer_width (int | None): 深度图宽度，默认自动推算为 view_width 的 10%。
            depthbuffer_height (int | None): 深度图高度，默认自动推算为 view_height 的 10%。
            near_clip (float): 近裁剪面距离。默认值为 0.0。
            far_clip (float): 远裁剪面距离。默认值为 2097152.0。

        Returns:
            list[str]: 当前视锥体内的实体 ID 列表。
        """
        if depthbuffer_height is None:
            depthbuffer_height = int(view_height * 0.1)
        if depthbuffer_width is None:
            depthbuffer_width = int(view_width * 0.1)
        return await UnaryAPI.get_subjects_in_view_frustum_with_aabb_culling(
            self._context.conn,
            camera_loc,
            camera_rot,
            fov=fov,
            view_width=view_width,
            view_height=view_height,
            depthbuffer_width=depthbuffer_width,
            depthbuffer_height=depthbuffer_height,
            near_clip=near_clip,
            far_clip=far_clip,
        )

    def spawn_face_dirt_on_agent(self, agent_id: str) -> bool:
        return self._context.sync_run(
            self.async_spawn_face_dirt_on_agent(agent_id=agent_id)
        )

    async def async_spawn_face_dirt_on_agent(self, agent_id: str) -> bool:
        dirt_id = await UnaryAPI.spawn_object(
            self._context.conn,
            blueprint="BP_FaceDirt",  # TODO: 当前是 UE 写死的 字符串
            location=Vector3(),
            is_simulating_physics=False,
        )

        return await UnaryAPI.attach_object_to_target(
            self._context.conn,
            object_id=dirt_id,
            target_id=agent_id,
            socket_name="FaceDirtSocket",
        )
