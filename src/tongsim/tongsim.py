"""
tongsim.tongsim

对应单个 TongSim UE 实例, 内部依赖 WorldContext 管理连接与任务调度。
"""

import os.path
import pickle
from typing import Final, TypeVar

from tongsim.connection.grpc import LegacyAPI, UnaryAPI
from tongsim.core.world_context import WorldContext
from tongsim.entity import AgentEntity, CameraEntity
from tongsim.entity.mixin import HFCameraEntity, MixinEntityBase
from tongsim.logger import get_logger
from tongsim.manager.debug_manager import DebugDraw
from tongsim.manager.pg import PGManager
from tongsim.manager.spatial import SpatialManager
from tongsim.manager.trace import TraceManager
from tongsim.manager.utils import UtilFuncs
from tongsim.math.geometry import Quaternion, Vector3
from tongsim.type import ViewModeType

__all__ = ["TongSim"]

_logger = get_logger("tongsim")

T = TypeVar("T", bound=MixinEntityBase)  # 限定类型必须是某种 MixinEntityBase 子类


class TongSim:
    """
    TongSim 实例: 代表一个连接的 UE 实例，提供高级控制接口。
    所有方法为同步阻塞接口，便于在同步项目或脚本中使用。
    """

    def __init__(self, grpc_endpoint: str, legacy_grpc_endpoint: str):
        """
        初始化一个 TongSim 实例。

        Args:
            endpoint (str): gRPC 服务器地址，如 "localhost:5056"
            legacy_endpoint (str): 废弃的 gRPC 服务器地址，如 "localhost:50052"
        """
        self._context: Final[WorldContext] = WorldContext(
            grpc_endpoint, legacy_grpc_endpoint
        )
        self._pg_manager: Final[PGManager] = PGManager(self._context)
        self._spatical_manager: Final[SpatialManager] = SpatialManager(self._context)
        self._trace_manager: Final[TraceManager] = TraceManager(self._context)
        self._spatial_manager: Final[SpatialManager] = SpatialManager(self._context)
        self._debug_draw: Final[DebugDraw] = DebugDraw(self._context)
        self._utils: Final[UtilFuncs] = UtilFuncs(self._context)

    @property
    def utils(self) -> UtilFuncs:
        """
        获取封装的实用工具函数接口。

        Returns:
            UtilFuncs: 提供实用工具函数方法。
        """
        return self._utils

    @property
    def debug_draw(self) -> DebugDraw:
        """
        获取 DebugDraw 调试绘图接口对象。

        Returns:
            DebugDraw: 提供调试绘制方法（如坐标系、线段、盒子）的管理类。
        """
        return self._debug_draw

    @property
    def pg_manager(self) -> PGManager:
        """
        获取 PG 管理器，用于访问和操作当前场景的 Parsing-Graph（PG）。
        Returns:
            PGManager: 当前连接上下文中的 PG 管理器实例。
        """
        return self._pg_manager

    @property
    def spatial_manager(self) -> SpatialManager:
        """
        获取 spatial manager，用于对场景空间结构的访问能力，包括: 房间信息、导航、出生点等等
        """
        return self._spatial_manager

    @property
    def trace_manager(self) -> TraceManager:
        """
        获取 Trace Manager，用于对场景做碰撞检测。
        """
        return self._trace_manager

    @property
    def context(self) -> WorldContext:
        """
        获取当前 TongSim 实例的运行时上下文。

        Returns:
            WorldContext: 管理连接、事件循环、任务派发等的上下文资源对象。
        """
        return self._context

    def open_level(self, level_name: str) -> bool:
        """
        打开一个指定关卡。

        Args:
            level_name (str): 关卡资源名（支持自动补全 SDBP_Map_ 前缀）

        Returns:
            bool: 是否打开成功
        """

        async def async_open_level():
            await self.pg_manager.async_stop_pg_stream()
            return await LegacyAPI.open_level(self._context.conn_legacy, level_name)

        if not level_name.startswith("SDBP_Map_"):
            level_name = f"SDBP_Map_{level_name}"

        return self._context.sync_run(async_open_level())

    def spawn_entity(
        self,
        entity_type: type[T],
        blueprint: str,
        location: Vector3,
        desired_name: str = "",
        quat: Quaternion | None = None,
        scale: Vector3 | None = None,
        is_simulating_physics: bool = True,
        is_vr_grippable: bool = True,
    ) -> T:
        """
        创建一个实体对象，并构造指定类型的 Entity。
        资产名称可查阅资产库： https://asset-tongai.mybigai.ac.cn/

        Args:
            entity_type (Type[T]): 要返回的实体类型，如 BaseObjectEntity、AgentEntity。
            blueprint (str): 使用的资产名称。
            location (Vector3): 实体的初始位置。
            desired_name (str, optional): 期望的实体名称。
            quat (Quaternion | None, optional): 初始旋转（四元数）。
            scale (Vector3 | None, optional): 初始缩放。
            is_simulating_physics (bool): 是否启用物理模拟。
            is_vr_grippable (bool): 是否允许 VR 交互。

        Returns:
            T: 构造完成的 Entity 实例。
        """

        async def _spawn_and_wrap() -> T:
            entity_id: str = await UnaryAPI.spawn_object(
                self._context.conn,
                blueprint=blueprint,
                desired_name=desired_name,
                location=location,
                rotation=quat,
                scale=scale,
                is_simulating_physics=is_simulating_physics,
                is_vr_grippable=is_vr_grippable,
            )
            return await entity_type.from_grpc(entity_id, self._context)

        return self._context.sync_run(_spawn_and_wrap())

    def destroy_entity(self, entity_id: str) -> bool:
        """
        销毁指定 ID 的实体对象，释放场景中的资源。

        Args:
            entity_id (str): 实体的唯一 ID。

        Returns:
            bool: 是否成功销毁实体。
        """
        return self._context.sync_run(
            LegacyAPI.destroy_object(self._context.conn_legacy, entity_id)
        )

    def spawn_agent(
        self,
        blueprint: str,
        location: Vector3,
        desired_name: str = "",
        quat: Quaternion | None = None,
        scale: Vector3 | None = None,
    ) -> AgentEntity:
        """
        创建一个 agent 实例。

        Args:
            blueprint (str): 蓝图资源名
            location (Vector3): 位置向量

        Returns:
            str: 新 agent 的 UE 实例名
        """

        async def _spawn_agent_and_wrap() -> AgentEntity:
            agent_id: str = await UnaryAPI.spawn_object(
                self._context.conn,
                blueprint=blueprint,
                desired_name=desired_name,
                location=location,
                rotation=quat,
                scale=scale,
                is_simulating_physics=True,
                is_vr_grippable=False,
            )
            return await AgentEntity.from_grpc(agent_id, self._context)

        return self._context.sync_run(_spawn_agent_and_wrap())

    def spawn_camera(
        self,
        camera_name: str,
        loc: Vector3,
        quat: Quaternion,
        fov: float = 90.0,
        width: int = 1280,
        height: int = 720,
        pixel_streamer_name: str | None = None,
    ) -> CameraEntity:
        """
        创建一个摄像机实例

        Args:
            camera_name (str): 摄像机名称
            loc (Vector3): 摄像机位置
            quat (Quaternion): 摄像机旋转（四元数）
            fov (float): 摄像机视野角
            width (int): 图像宽度
            height (int): 图像高度
            pixel_streamer_name (Optional[str]): 该相机对应的 PixelStreaming 流名称

        Returns:
            Entity: 封装摄像机的 Entity 实例
        """

        async def _spawn_camera_and_wrap() -> CameraEntity:
            camera_id = await UnaryAPI.spawn_camera(
                self._context.conn,
                camera_name,
                loc,
                quat,
                fov,
                width,
                height,
                pixel_streamer_name,
            )
            return await CameraEntity.from_grpc(camera_id, self._context)

        return self._context.sync_run(_spawn_camera_and_wrap())

    def spawn_hf_camera(
        self,
        camera_name: str,
        frequency: int,
        socket: str,
        attach_owner: str = "",
        fov: float = 90.0,
        width: int = 1280,
        height: int = 720,
    ) -> HFCameraEntity:
        """
        创建一个摄像机实例

        Args:
            camera_name (str): 摄像机在系统中的唯一名称/标识。
            frequency (int): 采样频率（Hz），即期望的帧率。必须为正数。
                注意：实际推流帧率可能受引擎/带宽等限制。
            socket (str): 绑定的socket名称。
            attach_owner (str): 要挂载/跟随的宿主实体，由于目前没有移动能力，只能依附于agent。
            fov (float): 水平视场角（单位：度）。默认 90.0，建议范围 (0, 180)。
            width (int): 图像宽度（像素），必须为正数。默认 1280。
            height (int): 图像高度（像素），必须为正数。默认 720。
        Returns:
            HFCameraEntity: 封装高速摄像机的 HFCameraEntity 实例
        """

        async def _spawn_camera_and_wrap() -> HFCameraEntity:
            camera_id = camera_name + "_" + attach_owner
            await UnaryAPI.spawn_hf_camera(
                self._context.conn,
                camera_id,
                frequency,
                socket,
                True,
                True,
                True,
                attach_owner,
                fov,
                width,
                height,
            )
            return await HFCameraEntity.create(camera_id, self._context, [])

        return self._context.sync_run(_spawn_camera_and_wrap())

    def entity_from_id(self, entity_type: type[T], entity_id: str) -> T:
        """
        根据 Entity ID 构造一个完整的 Entity 实例, 要求 id 完全准确。（该接口开销比 get_entity_by_name 要低一些）

        Args:
            entity_type (Type[T]): 要构造的 Entity 类型（必须为 MixinEntityBase 子类）
            entity_id (str): 实体的唯一标识符。

        Returns:
            T: 构造完成的实体对象。
        """
        return self._context.sync_run(
            entity_type.from_grpc(entity_id=entity_id, world_context=self._context)
        )

    def get_closest_entity_id(
        self, location: Vector3, max_dist: float, object_type: str | None = None
    ) -> str:
        """
        获取距离指定位置最近的某类物体的实体 ID。

        Args:
            location (Vector3): 参考位置。
            max_dist (float): 最大搜索半径。
            object_type (str | None): 可选的目标类型（如 "cup", "bottle"），为 None 时不区分类型。

        Returns:
            str: 最近物体的 Entity ID；如果未找到，将返回空字符串。
        """
        return self._context.sync_run(
            UnaryAPI.find_closest_object_by_type(
                self._context.conn, location, max_dist, object_type
            )
        )

    def get_closest_agent_entity_id(self, location: Vector3, max_dist: float) -> str:
        """
        获取距离指定位置最近的 Agent（智能体）实体 ID。

        Args:
            location (Vector3): 搜索起点位置。
            max_dist (float): 最大搜索半径。

        Returns:
            str: 最近 Agent 的 Entity ID；若无结果返回空字符串。
        """
        return self._context.sync_run(
            UnaryAPI.find_closest_agent(self._context.conn, location, max_dist)
        )

    def get_entity_by_name(self, entity_type: type[T], name: str) -> T:
        """
        基于名称构造任意类型的 Entity。id 支持模糊匹配。

        Args:
            name (str): 支持模糊匹配的名称
            entity_type (Type[T]): 要构造的 Entity 类型（必须为 MixinEntityBase 子类）

        Returns:
            T: 构造后的实体对象

        Raises:
            RuntimeError: 未找到匹配的实体
        """

        async def _get_entity_by_name() -> T | None:
            object_ids: list[str] = await LegacyAPI.get_object_ids_by_name(
                self._context.conn_legacy, name
            )
            if not object_ids:
                return None

            return await entity_type.from_grpc(
                entity_id=object_ids[0], world_context=self._context
            )

        entity = self._context.sync_run(_get_entity_by_name())
        if entity is None:
            raise RuntimeError(f"{entity_type.__name__} with name '{name}' not found.")
        return entity

    def get_entities_by_rdf_type(self, entity_type: type[T], rdf_type: str) -> list[T]:
        """
        获取所有 RDF 类型匹配的实体。

        Args:
            rdf_type (str): RDF 类型，如 "cup"
            entity_type (Type[T]): 要构造的 Entity 类型

        Returns:
            list[T]: 匹配到的实体对象列表
        """

        async def _get_entities() -> list[T]:
            object_ids: list[str] = await UnaryAPI.get_object_by_rdf(
                self._context.conn, rdf_type
            )
            return [
                await entity_type.from_grpc(object_id, self._context)
                for object_id in object_ids
            ]

        return self._context.sync_run(_get_entities())

    def get_asset_file_content(self, asset_path: str) -> tuple[str, str]:
        """
        获取指定资产文件的内容和最后修改时间（自动转为北京时间）。

        Args:
            asset_path (str): Unreal 中的资源路径（如 "/Game/Config/xxx.json"）

        Returns:
            tuple[str, str]:
                - 北京时间格式的最后修改时间（ISO 格式字符串）
                - 文件内容的原始 JSON 字符串
        """
        from datetime import datetime, timedelta, timezone

        last_modified_time_str, file_content_json_str = self._context.sync_run(
            UnaryAPI.get_asset_file_content(self._context.conn, asset_path)
        )

        dt_utc = datetime.fromisoformat(last_modified_time_str.replace("Z", "+00:00"))
        dt_china = dt_utc.astimezone(timezone(timedelta(hours=8)))
        return dt_china.isoformat(), file_content_json_str

    def change_view_mode(self, new_view_mode: ViewModeType) -> bool:
        """
        切换 TongSim 主相机的视角模式。

        Args:
            new_view_mode (ViewModeType): 目标视角模式。

        Returns:
            bool: 切换是否成功。
        """

        return self._context.sync_run(
            UnaryAPI.switch_camera_mode(self._context.conn, new_view_mode)
        )

    def change_view_target(self, new_view_agent_id: str) -> bool:
        """
        切换 TongSim 相机跟随目标，必须传入agent_id

        Args:
            new_view_agent_id (ViewModeType): 目标角色ID。

        Returns:
            bool: 切换是否成功。
        """

        return self._context.sync_run(
            UnaryAPI.camera_switch_character(self._context.conn, new_view_agent_id)
        )

    def exec_console_command(self, console_command: str) -> bool:
        """
        执行控制台指令，用于动态调整引擎参数、调试或执行特定指令。

        Args:
            console_command (str): 需要执行的控制台指令字符串。

        Returns:
            bool: 指令是否成功发送到 TongSim
        """
        return self._context.sync_run(
            UnaryAPI.exec_console_command(self._context.conn, console_command)
        )

    def save_scene(self, path: str, file_name: str, overwrite: bool = True) -> bool:
        """
        保存场景到指定的路径和文件名，默认保存为.pkl格式。

        Args:
            path (str): 保存文件的目录路径，支持相对路径和绝对路径。
            file_name (str): 保存的文件名
            overwrite (bool): 是否覆盖已存在的文件。如果为 False 且文件已存在，返回 False。

        Returns:
            bool: 如果保存成功，返回 True；否则返回 False。
        """
        if not os.path.isdir(path):
            _logger.warning(f"The directory {path} does not exist.")
            return False

        response = self._context.sync_run(UnaryAPI.save_game(self._context.conn))
        file_dir = os.path.join(path, file_name) + ".pkl"

        # 检查文件是否已经存在
        if os.path.isfile(file_dir):
            if not overwrite:
                _logger.warning(
                    f"The file {file_dir} already exists and overwrite is set to False."
                )
                return False
            _logger.info(
                f"The file {file_dir} already exists, but will be overwritten."
            )

        try:
            with open(file_dir, "wb") as file:
                pickle.dump(response, file)
            return True
        except Exception as e:
            _logger.warning(f"Error in saving scene: {e}")
            return False

    def load_scene(self, path: str, file_name: str) -> bool:
        """
        从指定路径加载场景。

        Args:
            path (str): 场景文件的目录路径。
            file_name (str): 需要加载的文件名，支持 .pkl 格式。

        Returns:
            bool: 如果加载成功，返回 True；否则返回 False。
        """
        return self._load_scene(path, file_name)

    def _load_scene(self, path: str, file_name: str) -> bool:
        if not os.path.isdir(path):
            _logger.warning(f"The directory {path} does not exist.")
            return False

        file_dir = os.path.join(path, file_name)

        if os.path.isfile(file_dir):
            file_dir = file_dir
        elif os.path.isfile(file_dir + ".pkl"):
            file_dir = file_dir + ".pkl"
        elif os.path.isfile(file_dir + ".pb"):
            file_dir = file_dir + ".pb"
        else:
            _logger.warning(f"The file {file_dir} does not exist.")
            return False

        try:
            file_extension = os.path.splitext(file_dir)[1].lower()

            with open(file_dir, "rb") as file:
                if file_extension == ".pkl":
                    self._context.sync_run(
                        UnaryAPI.load_game(self._context.conn, pickle.load(file))
                    )
                elif file_extension == ".pb":
                    self._context.sync_run(
                        UnaryAPI.load_game(self._context.conn, file.read())
                    )
                else:
                    _logger.warning(f"Unsupported file format for {file_dir}.")
                    return False

            _logger.info(f"Scene loaded successfully from {file_dir}.")
            return True

        except Exception as e:
            _logger.warning(f"There are Error in loading scene: {e}")
            return False

    def close(self):
        """关闭当前实例并释放资源"""
        self._context.release()

    def __enter__(self):
        """支持 with 上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持 with 上下文管理器"""
        self.close()
