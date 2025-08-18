from tongsim.connection.grpc import UnaryAPI
from tongsim.core.world_context import WorldContext
from tongsim.logger import get_logger
from tongsim.math.geometry import Vector3

_logger = get_logger("trace")


class TraceManager:
    """
        TraceManager 提供对场景空间使用各种形状检测的能力，包括: 球、立体。默认维护在 TongSim 对象实例中，可通过其trace_manager获取。

    功能:

    - 提供球形追踪（sphere trace）功能，支持单一目标和多个目标的检测
    - 提供盒形追踪（box trace）功能，支持单一目标和多个目标的检测
    - 所有操作均在线程内事件循环（AsyncLoop）中调度，确保线程安全，无需锁。
    """

    def __init__(self, world_context: WorldContext):
        self._context: WorldContext = world_context

    def sphere_trace_single(
        self,
        start: Vector3,
        end: Vector3,
        radius: float,
        ignore_subject_id: list[str],
    ) -> str:
        """
        使用同步接口进行球形追踪，Returns第一个命中的目标ID。

        Args:
            start (Vector3): 球形追踪的起点。
            end (Vector3): 球形追踪的终点。
            radius (float): 球的半径。
            ignore_subject_id (list[str]): 要忽略的目标 ID 列表。

        Returns:
            str: 第一个命中的目标ID，如果没有命中则Returns空字符串。
        """
        return self._context.sync_run(
            self.async_sphere_trace_single(start, end, radius, ignore_subject_id)
        )

    async def async_sphere_trace_single(
        self,
        start: Vector3,
        end: Vector3,
        radius: float,
        ignore_subject_id: list[str],
    ) -> str:
        """
        异步版本：进行球形追踪，Returns第一个命中的目标ID。

        Args:
            start (Vector3): 球形追踪的起点。
            end (Vector3): 球形追踪的终点。
            radius (float): 球的半径。
            ignore_subject_id (list[str]): 要忽略的目标 ID 列表。

        Returns:
            str: 第一个命中的目标ID，如果没有命中则Returns空字符串。
        """
        obj_list: list[str] = await UnaryAPI.sphere_trace(
            self._context.conn,
            start,
            end,
            radius,
            ignore_subject_id,
            False,
        )
        if len(obj_list) > 0:
            return obj_list[0]
        return ""

    def sphere_trace_multi(
        self,
        start: Vector3,
        end: Vector3,
        radius: float,
        ignore_subject_id: list[str],
    ) -> list[str]:
        """
        使用同步接口进行球形追踪，Returns所有命中的目标ID。

        Args:
            start (Vector3): 球形追踪的起点。
            end (Vector3): 球形追踪的终点。
            radius (float): 球的半径。
            ignore_subject_id (list[str]): 要忽略的目标 ID 列表。

        Returns:
            list[str]: 所有命中的目标ID列表。
        """
        return self._context.sync_run(
            self.async_sphere_trace_multi(start, end, radius, ignore_subject_id)
        )

    async def async_sphere_trace_multi(
        self,
        start: Vector3,
        end: Vector3,
        radius: float,
        ignore_subject_id: list[str],
    ) -> list[str]:
        """
        异步版本：进行球形追踪，Returns所有命中的目标ID列表。

        Args:
            start (Vector3): 球形追踪的起点。
            end (Vector3): 球形追踪的终点。
            radius (float): 球的半径。
            ignore_subject_id (list[str]): 要忽略的目标 ID 列表。

        Returns:
            list[str]: 所有命中的目标ID列表。
        """
        return await UnaryAPI.sphere_trace(
            self._context.conn,
            start,
            end,
            radius,
            ignore_subject_id,
            True,
        )

    def box_trace_single(
        self,
        start: Vector3,
        end: Vector3,
        box_half_size: Vector3,
        rotation: Vector3,
        ignore_subject_id: list[str],
    ) -> str:
        """
        使用同步接口进行盒形追踪，Returns第一个命中的目标ID。

        Args:
            start (Vector3): 盒形追踪的起点。
            end (Vector3): 盒形追踪的终点。
            box_half_size (Vector3): 盒子的半尺寸（长、宽、高）。
            rotation (Vector3): 盒子的旋转角度。
            ignore_subject_id (list[str]): 要忽略的目标 ID 列表。

        Returns:
            str: 第一个命中的目标ID，如果没有命中则Returns空字符串。
        """
        return self._context.sync_run(
            self.async_box_trace_single(
                start, end, box_half_size, rotation, ignore_subject_id
            )
        )

    async def async_box_trace_single(
        self,
        start: Vector3,
        end: Vector3,
        box_half_size: Vector3,
        rotation: Vector3,
        ignore_subject_id: list[str],
    ) -> str:
        """
        异步版本：进行盒形追踪，Returns第一个命中的目标ID。

        Args:
            start (Vector3): 盒形追踪的起点。
            end (Vector3): 盒形追踪的终点。
            box_half_size (Vector3): 盒子的半尺寸（长、宽、高）。
            rotation (Vector3): 盒子的旋转角度。
            ignore_subject_id (list[str]): 要忽略的目标 ID 列表。

        Returns:
            str: 第一个命中的目标ID，如果没有命中则Returns空字符串。
        """
        resp: list[str] = await UnaryAPI.box_trace(
            self._context.conn,
            start,
            end,
            box_half_size,
            rotation,
            ignore_subject_id,
            False,
        )
        if len(resp) > 0:
            return resp[0]
        return ""

    def box_trace_multi(
        self,
        start: Vector3,
        end: Vector3,
        box_half_size: Vector3,
        rotation: Vector3,
        ignore_subject_id: list[str],
    ) -> list[str]:
        """
        使用同步接口进行盒形追踪，Returns所有命中的目标ID。

        Args:
            start (Vector3): 盒形追踪的起点。
            end (Vector3): 盒形追踪的终点。
            box_half_size (Vector3): 盒子的半尺寸（长、宽、高）。
            rotation (Vector3): 盒子的旋转角度。
            ignore_subject_id (list[str]): 要忽略的目标 ID 列表。

        Returns:
            list[str]: 所有命中的目标ID列表。
        """
        return self._context.sync_run(
            self.async_box_trace_multi(
                start, end, box_half_size, rotation, ignore_subject_id
            )
        )

    async def async_box_trace_multi(
        self,
        start: Vector3,
        end: Vector3,
        box_half_size: Vector3,
        rotation: Vector3,
        ignore_subject_id: list[str],
    ) -> list[str]:
        """
        异步版本：进行盒形追踪，Returns所有命中的目标ID列表。

        Args:
            start (Vector3): 盒形追踪的起点。
            end (Vector3): 盒形追踪的终点。
            box_half_size (Vector3): 盒子的半尺寸（长、宽、高）。
            rotation (Vector3): 盒子的旋转角度。
            ignore_subject_id (list[str]): 要忽略的目标 ID 列表。

        Returns:
            list[str]: 所有命中的目标ID列表。
        """
        return await UnaryAPI.box_trace(
            self._context.conn,
            start,
            end,
            box_half_size,
            rotation,
            ignore_subject_id,
            True,
        )
