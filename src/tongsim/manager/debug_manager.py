from typing import NamedTuple

from tongsim.connection.grpc import UnaryAPI
from tongsim.core.world_context import WorldContext
from tongsim.logger import get_logger
from tongsim.math.geometry import Transform, Vector3

_logger = get_logger("debug")


class DebugLine(NamedTuple):
    """
    表示一条调试用的线段。

    Attributes:
        start (Vector3): 线段起点的三维坐标。
        end (Vector3): 线段终点的三维坐标。
    """

    start: Vector3
    end: Vector3


class DebugBox(NamedTuple):
    """
    表示一个用于调试绘制的盒子。

    Attributes:
        transform (Transform): 世界空间下的变换，包括位置与旋转。
        center (Vector3): 相对于 transform 的局部中心偏移。
        extent (Vector3): 盒子的半边长，表示在 x/y/z 方向的尺寸。
    """

    transform: Transform
    center: Vector3
    extent: Vector3


class DebugDraw:
    """
    DebugDraw 提供对 TongSim 场景调试绘制能力的封装接口，支持坐标系、线段、盒子等调试可视化内容。
    """

    def __init__(self, world_context: WorldContext):
        self._context: WorldContext = world_context

    def draw_coordinates(
        self,
        coordinates: list[Transform],
        time_length: float,
        line_width: float = 1.0,
        axis_length: float = 5.0,
        world_transform: Transform | None = None,
    ) -> bool:
        """
        在场景中绘制多个坐标系（同步接口）。

        Args:
            coordinates (list[Transform]): 局部坐标系的变换列表。
            time_length (float): 绘制持续时间（秒）。
            line_width (float): 坐标轴线的粗细。
            axis_length (float): 坐标轴的长度。
            world_transform (Transform | None): 坐标系的世界变换。若为 None, 则使用默认 Transform()。

        Returns:
            bool: 是否绘制成功。
        """
        return self._context.sync_run(
            self.async_draw_coordinates(
                coordinates, time_length, line_width, axis_length, world_transform
            )
        )

    async def async_draw_coordinates(
        self,
        coordinates: list[Transform],
        time_length: float,
        line_width: float = 1.0,
        axis_length: float = 5.0,
        world_transform: Transform | None = None,
    ) -> bool:
        """
        异步版本: 绘制多个坐标系。

        Args:
            coordinates (list[Transform]): 局部坐标系的变换列表。
            time_length (float): 绘制持续时间（秒）。
            line_width (float): 坐标轴线的粗细。
            axis_length (float): 坐标轴的长度。
            world_transform (Transform | None): 坐标系的世界变换。若为 None, 则使用默认 Transform()。

        Returns:
            bool: 是否绘制成功。
        """
        world_transform = world_transform or Transform()
        return await UnaryAPI.debug_draw_coordinates(
            self._context.conn,
            world_transform,
            coordinates,
            time_length,
            line_width,
            axis_length,
        )

    def draw_lines(
        self,
        lines: list[DebugLine],
        time_length: float,
        line_width: float = 1.0,
        world_transform: Transform | None = None,
    ) -> bool:
        """
        绘制一组线段（同步接口）。

        Args:
            lines (list[DebugLine]): 要绘制的线段列表。
            time_length (float): 绘制持续时间（秒）。
            line_width (float): 线段宽度。
            world_transform (Transform | None): 坐标系的世界变换。若为 None, 则使用默认 Transform()。

        Returns:
            bool: 是否绘制成功。
        """
        return self._context.sync_run(
            self.async_draw_lines(lines, time_length, line_width, world_transform)
        )

    async def async_draw_lines(
        self,
        lines: list[DebugLine],
        time_length: float,
        line_width: float = 1.0,
        world_transform: Transform | None = None,
    ) -> bool:
        """
        异步版本: 绘制一组线段。

        Args:
            lines (list[DebugLine]): 要绘制的线段列表。
            time_length (float): 绘制持续时间（秒）。
            line_width (float): 线段宽度。
            world_transform (Transform | None): 坐标系的世界变换。若为 None, 则使用默认 Transform()。

        Returns:
            bool: 是否绘制成功。
        """
        world_transform = world_transform or Transform()
        line_pairs = [(line.start, line.end) for line in lines]
        return await UnaryAPI.debug_draw_lines(
            self._context.conn,
            world_transform,
            line_pairs,
            time_length,
            line_width,
        )

    def draw_boxes(
        self,
        boxes: list[DebugBox],
        time_length: float,
        line_width: float = 1.0,
        world_transform: Transform | None = None,
    ) -> bool:
        """
        绘制一组盒子（同步接口）。

        Args:
            boxes (list[DebugBox]): 要绘制的盒子列表。
            time_length (float): 绘制持续时间（秒）。
            line_width (float): 边框宽度。
            world_transform (Transform | None): 坐标系的世界变换。若为 None, 则使用默认 Transform()。

        Returns:
            bool: 是否绘制成功。
        """
        return self._context.sync_run(
            self.async_draw_boxes(boxes, time_length, line_width, world_transform)
        )

    async def async_draw_boxes(
        self,
        boxes: list[DebugBox],
        time_length: float,
        line_width: float = 1.0,
        world_transform: Transform | None = None,
    ) -> bool:
        """
        异步版本: 绘制一组盒子。

        Args:
            boxes (list[DebugBox]): 要绘制的盒子列表。
            time_length (float): 绘制持续时间（秒）。
            line_width (float): 边框宽度。
            world_transform (Transform | None): 坐标系的世界变换。若为 None, 则使用默认 Transform()。

        Returns:
            bool: 是否绘制成功。
        """
        world_transform = world_transform or Transform()
        box_tuples = [(box.transform, box.center, box.extent) for box in boxes]
        return await UnaryAPI.debug_draw_boxes(
            self._context.conn,
            world_transform,
            box_tuples,
            time_length,
            line_width,
        )

    def draw_box_in_point(
        self,
        point: Vector3,
        time_length: float,
        box_size: float = 2.5,
        line_width: float = 1.0,
    ) -> bool:
        """
        在指定位置绘制一个盒子（同步接口）。

        Args:
            point (Vector3): 盒子中心点的位置。
            time_length (float): 绘制持续时间（秒）。
            box_size (float): 盒子的边长（将转换为 extent）。
            line_width (float): 盒子边框的线宽。

        Returns:
            bool: 是否绘制成功。
        """
        boxes = [
            DebugBox(
                transform=Transform(),  # 无偏移变换
                center=point,
                extent=Vector3(box_size, box_size, box_size),
            )
        ]
        return self._context.sync_run(
            self.async_draw_boxes(boxes, time_length, line_width)
        )

    def draw_coordinate_in_point(
        self,
        point: Vector3,
        time_length: float,
        coordinate_size: float = 5.0,
        line_width: float = 1.0,
    ) -> bool:
        """
        在指定位置绘制一个坐标系（同步接口）。

        Args:
            point (Vector3): 坐标系的原点位置。
            time_length (float): 绘制持续时间（秒）。
            coordinate_size (float): 坐标轴长度。
            line_width (float): 坐标轴的线宽。

        Returns:
            bool: 是否绘制成功。
        """
        coord = Transform(location=point)
        return self._context.sync_run(
            self.async_draw_coordinates(
                coordinates=[coord],
                time_length=time_length,
                line_width=line_width,
                axis_length=coordinate_size,
                world_transform=Transform(),
            )
        )
