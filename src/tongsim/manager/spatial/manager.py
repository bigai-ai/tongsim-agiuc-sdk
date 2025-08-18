from tongsim.connection.grpc import UnaryAPI
from tongsim.core.world_context import WorldContext
from tongsim.logger import get_logger
from tongsim.math.geometry import Vector3

_logger = get_logger("spatial")


class SpatialManager:
    """
    SpatialManager 提供对场景空间结构的访问能力，包括: 房间信息、导航、出生点等等。默认维护在 TongSim 对象实例中，可通过其子方法 spatial_manager() 获取。
    """

    def __init__(self, world_context: WorldContext):
        self._context: WorldContext = world_context

    def get_current_room_info(self) -> list[dict]:
        """
        获取当前地图中所有房间信息。

        Returns:
            list[dict]: 每个房间信息包含如下字段:
                - room_name (str)
                - room_category (str)
                - boxes (list[dict]): AABB 边界框，包含 min/max 三维坐标。
        """
        return self._context.sync_run(self.async_get_current_room_info())

    async def async_get_current_room_info(self) -> list[dict]:
        """
        异步获取当前地图房间信息。

        Returns:
            list[dict]: 每个房间信息包含如下字段:
                - room_name (str)
                - room_category (str)
                - boxes (list[dict]): AABB 边界框，包含 min/max 三维坐标。
        """
        return await UnaryAPI.get_room_info(self._context.conn)

    def get_nearest_nav_position(self, target_location: Vector3) -> Vector3 | None:
        """
        获取目标点附近最近的可导航位置。

        Args:
            target_location (Vector3): 待查询的目标位置。

        Returns:
            Vector3: 导航网格中最近的有效点。
        """
        return self._context.sync_run(
            self.async_get_nearest_nav_position(target_location)
        )

    async def async_get_nearest_nav_position(
        self, target_location: Vector3
    ) -> Vector3 | None:
        """
        异步版本: 获取目标点附近最近的可导航位置。

        Args:
            target_location (Vector3): 待查询的目标位置。

        Returns:
            Vector3: 导航网格中最近的有效点。
        """
        return await UnaryAPI.get_nearest_nav_point(self._context.conn, target_location)

    def get_random_spawn_location(self, room_name: str = "") -> Vector3 | None:
        """
        查询指定房间内或整个地图中可用于生成智能体的随机位置。

        Args:
            room_name (str): 房间名称（可选）。若为空，则自动从所有房间中选择。

        Returns:
            Vector3: 可用于 spawn 的随机导航位置。
        """
        return self._context.sync_run(self.async_get_random_spawn_location(room_name))

    async def async_get_random_spawn_location(
        self, room_name: str = ""
    ) -> Vector3 | None:
        """
        异步版本: 查询指定房间或地图中可 spawn 的随机导航位置。

        Args:
            room_name (str): 房间名称（可选）。若为空，则自动从所有房间中选择。

        Returns:
            Vector3: 可用于 spawn 的随机导航位置。
        """
        return await UnaryAPI.get_random_spawn_location(self._context.conn, room_name)

    def get_room_name_from_location(self, location: Vector3) -> str:
        """
        获得该位置所在的房间名

        Args:
            location (Vector3): 查询位置三维坐标点

        Return:
             str: 该位置所在房间名，如果不在任何房间区域返回"None"
        """
        return self._context.sync_run(self.async_get_room_name_from_location(location))

    async def async_get_room_name_from_location(self, location: Vector3) -> str:
        """
        异步版本：获得该位置所在的房间名

        Args:
            location (Vector3): 查询位置三维坐标点

        Return:
             str: 该位置所在房间名，如果不在任何房间区域返回"None"
        """
        return await UnaryAPI.get_room_name_from_location(self._context.conn, location)

    def get_room_array(self) -> list[str]:
        """
        获得当前地图所有房间

        Returns:
            list[str]: 得到所有房间名字列表
        """
        return self._context.sync_run(self.async_get_room_array())

    async def async_get_room_array(self) -> list[str]:
        """
        异步版本：获得当前地图所有房间

        Returns:
            list[str]: 得到所有房间名字列表
        """
        return await UnaryAPI.get_room_array(self._context.conn)

    def get_nav_point_ringlike(
        self, center: Vector3, min_radius: float, max_radius: float, room: str
    ) -> Vector3:
        """
        同步版本：获取指定环形区域随机点。

        Args:
            center (Vector3): 环形区域中心位置。
            min_radius (float): 内圈半径。
            max_radius (float): 外圈半径。
            room (str): 房间内名称（限定在房间内，默认没有房间限定）。

        Returns:
            Vector3: 环形区域内随机点
        """
        return self._context.sync_run(
            self.async_get_nav_point_ringlike(center, min_radius, max_radius, room)
        )

    async def async_get_nav_point_ringlike(
        self, center: Vector3, min_radius: float, max_radius: float, room: str = ""
    ) -> Vector3:
        """
        异步版本：获取指定环形区域随机点。

        Args:
            center (Vector3): 环形区域中心位置。
            min_radius (float): 内圈半径。
            max_radius (float): 外圈半径。
            room (str): 房间内名称（限定在房间内，默认没有房间限定）。

        Returns:
            Vector3: 环形区域内随机点
        """
        return await UnaryAPI.get_nav_point_ringlike(
            self._context.conn, center, min_radius, max_radius, room
        )

    def get_navmesh_polys_in_room(self, room_name: str) -> list[list[Vector3]]:
        """
        获取房间内导航网格多边形顶点列表（同步接口）。

        Args:
            room_name (str): 房间名称。

        Returns:
            list[list[Vector3]]: 导航网格多边形集合。每个元素表示一个多边形的顶点列表，顶点类型为 Vector3。
        """
        return self._context.sync_run(self.async_get_navmesh_polys_in_room(room_name))

    async def async_get_navmesh_polys_in_room(
        self, room_name: str
    ) -> list[list[Vector3]]:
        """
        获取房间内导航网格多边形顶点列表（异步接口）。

        Args:
            room_name (str): 房间名称。

        Returns:
            list[list[Vector3]]: 导航网格多边形集合。每个元素表示一个多边形的顶点列表，顶点类型为 Vector3。
        """
        return await UnaryAPI.get_nevmesh_polys_in_room(
            self._context.conn, room_name=room_name
        )
