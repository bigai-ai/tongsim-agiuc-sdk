import asyncio
import contextlib
import time
from collections import defaultdict
from collections.abc import AsyncIterator
from concurrent.futures import Future
from typing import Any

from google.protobuf.json_format import MessageToDict

from tongsim.connection.grpc import UnaryAPI, UnaryStreamAPI
from tongsim.core.world_context import WorldContext
from tongsim.logger import get_logger

from .indexer import PGIndexer
from .registry import PG_COMPONENT_REGISTRY, ComponentSchema
from .schema import PGQueryMeta, validate_query_meta

_logger = get_logger("pg")

__all__ = ["PGManager"]


class PGManager:
    """
    PGManager 管理全量 PG(Parse-Graph) 数据状态。 默认维护在 TongSim 对象实例中，可通过其子方法 pg_manager() 获取。

    功能:

    - 从 gRPC Stream 接收增量 PG 数据
    - 将增量数据合并为结构完整的全量 PG
    - 支持基于 subject/component ID 的高性能索引访问
    - 提供基于 metainfo 的字段查询接口，支持同步与异步版本

    注意:

    - 所有操作均在线程内事件循环（AsyncLoop）中调度，确保线程安全，无需锁。
    """

    def __init__(self, world_context: WorldContext):
        self._pg: dict = {}  # 当前完整 PG 状态
        self._pg_freq: int = 10
        self._indexer = PGIndexer()
        self._context: WorldContext = world_context
        self._stream_task: Future | None = None
        self._stream = None
        self._next_segmentation_id: int = 1
        self._assign_segmentation_id: bool = True  # 记录当前是否启用了分割图 ID 分配
        self._event = asyncio.Event()

    async def notify_new_pg(self) -> AsyncIterator[dict]:
        """
        异步推送 PG 更新。每当 _run_pg_stream 合并了新帧，就 yield 一次当前的 self._pg，请使用异步函数去运行，否则会卡住

        说明：
        - 这是一个“热”流：多个消费者并行订阅时，都会在事件触发时各自被唤醒。
        - 返回的 dict 视为只读视图；若需要拷贝请在消费者侧自行 copy/deepcopy。
        """
        try:
            while self.is_pg_stream_started:
                await self._event.wait()
                self._event.clear()
                yield self._pg
        except asyncio.CancelledError:
            # 让上层正常感知取消
            raise

    @property
    def is_pg_stream_started(self) -> bool:
        """
        判断是否启动 PG 流监听

        Returns:
             bool: 是否开启 PG 流监听
        """
        return self._stream_task and not self._stream_task.done()

    def start_pg_stream(self, pg_freq: int = 10, assign_segmentation_id: bool = True):
        """
        启动 PG 流监听（同步接口）。

        Args:
            pg_freq (int): PG 刷新频率，单位为帧数（默认每 10 帧更新一次）。
            assign_segmentation_id (bool): 是否启用分割图 ID 分配, 默认为 True，即自动给场景中每个物体 分配分割图 ID.
        """
        self._context.sync_run(
            self.async_start_pg_stream(pg_freq, assign_segmentation_id)
        )

    async def async_start_pg_stream(
        self, pg_freq: int = 10, assign_segmentation_id: bool = True
    ):
        """
        启动 PG 流监听（异步接口）。

        Args:
            pg_freq (int): PG 刷新频率，单位为帧数（默认每 10 帧更新一次）。
            assign_segmentation_id (bool): 是否启用分割图 ID 分配, 默认为 True，即自动给场景中每个物体 分配分割图 ID.
        """
        if self._stream_task and not self._stream_task.done():
            return

        succ = await UnaryAPI.set_pg_frequency(self._context.conn, pg_freq)
        if succ:
            self._pg_freq = pg_freq
            self._assign_segmentation_id = assign_segmentation_id

            self._stream = UnaryStreamAPI.subscribe_pg(self._context.conn)
            pg_iter = self._stream.__aiter__()
            pg_msg = await anext(pg_iter)

            # 预处理首帧: offload 到线程池执行，避免阻塞事件循环

            loop = asyncio.get_running_loop()
            segment_id_map = await loop.run_in_executor(
                None, self.do_merge_first_pg, pg_msg
            )

            if segment_id_map:
                await UnaryAPI.set_segment_id(self._context.conn, segment_id_map)

            self._stream_task = self._context.async_task(
                self._run_pg_stream(self._stream),
                name=f"Context-{self._context.uuid} PG-Stream",
            )

        else:
            _logger.error("Context-{self._context.uuid} set pg freq failed")

    async def async_stop_pg_stream(self):
        """
        停止 PG 流监听任务（异步接口）。

        若存在活跃的 PG 流任务，将尝试取消并等待其清理完成。
        同时清空 PG 数据缓存。

        Raises:
            asyncio.CancelledError: 若取消失败或向上传播取消信号。
        """
        if self._stream:
            with contextlib.suppress(Exception):
                self._stream.cancel()
            self._stream = None

        if self._stream_task and not self._stream_task.done():
            self._stream_task.cancel()
            try:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(
                    None, self._stream_task.result
                )  # 阻塞拿结果，避免 await Future 错误
            except asyncio.CancelledError:
                _logger.debug(
                    f"PG stream task is stopped for context {self._context.uuid}"
                )
            except Exception as e:
                _logger.exception(f"Exception during PG stream stop: {e}")
            self._stream_task = None
            self._pg = {}
            self._indexer.clear()
            self._next_segmentation_id: int = 1
            self._assign_segmentation_id: bool = True
            self._event.set()

    def do_merge_first_pg(self, pg_msg: dict) -> dict[str, int] | None:
        t0 = time.perf_counter()
        new_pg = MessageToDict(
            pg_msg,
            preserving_proto_field_name=True,
            always_print_fields_with_no_presence=True,
        )
        segment_id_map = self._merge_pg(new_pg)
        t1 = time.perf_counter()
        frame = new_pg.get("current_frame", "?")
        _logger.info(f"Init full PG frame {frame} in {(t1 - t0) * 1000:.2f} ms")
        return segment_id_map

    def fetch_full_pg_from_streaming(self) -> dict:
        """
        从 PG 流中获取当前的全量 PG 数据（同步接口）。

        Returns:
            dict: 当前帧的完整 PG 数据结构。
        """
        return self._context.sync_run(self.async_fetch_full_pg_from_streaming())

    async def async_fetch_full_pg_from_streaming(self) -> dict:
        """
        从 PG 流中获取当前的全量 PG 数据（异步接口）。

        Returns:
            dict: 当前帧的完整 PG 数据结构。
        """
        return self._pg

    def fetch_subject_pg_from_streaming(self, sid: str) -> dict | None:
        """
        从 PG 流中获取指定 Subject 的 PG 信息（同步接口）。

        Args:
            sid (str): Subject ID。

        Returns:
            dict | None: 该 Subject 的 PG 数据（若不存在则为 None）。
        """
        return self._context.sync_run(self.async_fetch_subject_pg_from_streaming(sid))

    async def async_fetch_subject_pg_from_streaming(self, sid: str) -> dict | None:
        """
        从 PG 流中获取指定 Subject 的 PG 信息（异步接口）。

        Args:
            sid (str): Subject ID。

        Returns:
            dict | None: 该 Subject 的 PG 数据（若不存在则为 None）。
        """
        sidx = self._indexer.get_subject_index(sid)
        if sidx is None:
            return None
        return self._pg["subject_pg"][sidx]

    def fetch_component_pg_from_streaming(self, sid: str, cid: str) -> dict | None:
        """
        获取指定组件的 PG 信息（同步接口）。

        Args:
            sid (str): Subject ID。
            cid (str): Component ID。

        Returns:
            dict | None: 指定组件的 PG 数据（若不存在则为 None）。
        """
        return self._context.sync_run(
            self.async_fetch_component_pg_from_streaming(sid, cid)
        )

    async def async_fetch_component_pg_from_streaming(
        self, sid: str, cid: str
    ) -> dict | None:
        """
        获取指定组件的 PG 信息（异步接口）。

        Args:
            sid (str): Subject ID。
            cid (str): Component ID。

        Returns:
            dict | None: 指定组件的 PG 数据（若不存在则为 None）。
        """
        sidx = self._indexer.get_subject_index(sid)
        cidx = self._indexer.get_component_index(sid, cid)
        if sidx is None or cidx is None:
            return None
        return self._pg["subject_pg"][sidx]["component_pg"][cidx]

    def query(self, metas: list[dict]) -> dict[str, dict[str, Any]]:
        """
        执行组件字段查询（同步接口）。

        关于 metas 参数: 可使用 get_pg_metainfo_schema() 获取支持的组件与字段。

        Args:
            metas (list[dict]): 查询字段的 metainfo 列表。

        Returns:
            dict[str, dict[str, Any]]: subject_id → 字段结果映射。
                - 键为 subject_id（主体 ID）
                - 值为一个字典，包含该主体上查询到的字段结果
                - 附加键 "__meta__" 包含本次查询的全局信息
        """
        return self._context.sync_run(self.async_query_fields(metas))

    async def async_query_fields(self, metas: list[dict]) -> dict[str, dict[str, Any]]:
        """
        执行组件字段查询（异步接口）。

        关于 metas 参数: 可使用 get_pg_metainfo_schema() 获取支持的组件与字段。

        Args:
            metas (list[dict]): 查询字段的 metainfo 列表。

        Returns:
            dict[str, dict[str, Any]]: subject_id → 字段结果映射。
                - 键为 subject_id（主体 ID）
                - 值为一个字典，包含该主体上查询到的字段结果
                - 附加键 "__meta__" 包含本次查询的全局信息
        """
        validated = self._validate_metas(metas)
        metas_by_component = self._group_metas_by_component(validated)

        result: dict[str, dict[str, Any]] = {}

        for subj in self._pg.get("subject_pg", []):
            sid = subj["subject"]["id"]
            if self._subject_pass_filter(subj):
                continue
            self._extract_fields_from_subject(subj, sid, metas_by_component, result)

        # 加入全局元信息
        result["__meta__"] = {"beijing_timestamp": self._pg.get("beijing_timestamp", 0)}

        return result

    def get_pg_metainfo_schema(self) -> dict[str, ComponentSchema]:
        """
        获取当前 PG 查询支持的组件及其字段定义。

        Returns:
            组件名 → 支持字段名 列表。
        """
        return PG_COMPONENT_REGISTRY

    async def _run_pg_stream(self, stream):
        """
        从 gRPC 流中持续接收增量 PG，并合并到当前状态。
        """
        max_duration_ms = 1000.0 / max(self._pg_freq, 1)

        try:
            async for pg_msg in stream:
                t0 = time.perf_counter()
                new_pg = MessageToDict(
                    pg_msg,
                    preserving_proto_field_name=True,
                    always_print_fields_with_no_presence=True,
                )
                segment_id_map = self._merge_pg(new_pg)
                self._event.set()

                t1 = time.perf_counter()

                duration_ms = (t1 - t0) * 1000
                frame = new_pg.get("current_frame", "?")

                if duration_ms > max_duration_ms:
                    _logger.warning(
                        f"Merge PG frame {frame} took {duration_ms:.2f} ms (exceeds {max_duration_ms:.2f} ms budget)"
                    )
                else:
                    _logger.debug(f"Merge PG frame {frame} in {duration_ms:.2f} ms")

                # 设置增量的 segment_id
                if segment_id_map:
                    await UnaryAPI.set_segment_id(self._context.conn, segment_id_map)

        except asyncio.CancelledError:
            _logger.info(f"PG stream task cancelled for context {self._context.uuid}")
            raise  # 取消应向上传播以便正常关闭

        except Exception as e:
            _logger.exception(
                f"PG stream encountered error in context {self._context.uuid}: {e}"
            )

    def _merge_pg(self, new_pg: dict) -> dict[str, int] | None:
        """将增量 PG 合并到 self._pg，并更新索引器"""
        if "world_id" in new_pg:
            self._pg["world_id"] = new_pg["world_id"]
        if "current_frame" in new_pg:
            self._pg["current_frame"] = new_pg["current_frame"]
        if "beijing_timestamp" in new_pg:
            self._pg["beijing_timestamp"] = new_pg["beijing_timestamp"].get(
                "timestamp_ms", 0
            )

        new_subject_ids: list[str] = []  # 收集用于设置 分割图 ID

        for subject in new_pg.get("subject_pg", []):
            sid = subject["subject"]["id"]
            if not self._indexer.has_subject(sid):
                self._merge_subject_new(subject, sid)
                new_subject_ids.append(sid)
            else:
                self._merge_subject_existing(subject, sid)

        if self._assign_segmentation_id and new_subject_ids:
            sid_segid_map = {
                sid: self._next_segmentation_id + i
                for i, sid in enumerate(new_subject_ids)
            }
            self._next_segmentation_id += len(new_subject_ids)
            return sid_segid_map
        return None

    def _merge_subject_new(self, subject: dict, sid: str):
        self._pg.setdefault("subject_pg", []).append(subject)
        sidx = len(self._pg["subject_pg"]) - 1
        self._indexer.register_subject(sid, sidx)

        for i, comp in enumerate(subject.get("component_pg", [])):
            if "component" in comp and "id" in comp["component"]:
                self._indexer.register_component(sid, comp["component"]["id"], i)

    def _merge_subject_existing(self, subject: dict, sid: str):
        sidx = self._indexer.get_subject_index(sid)
        subject_ref = self._pg["subject_pg"][sidx]

        if subject.get("subject_destroyed"):
            subject_ref["is_subject_destroyed"] = True
            return

        for comp in subject.get("component_pg", []):
            if "component" not in comp or "id" not in comp["component"]:
                continue

            cid = comp["component"]["id"]
            cidx = self._indexer.get_component_index(sid, cid)

            if cidx is not None:
                subject_ref["component_pg"][cidx] = comp
            else:
                subject_ref["component_pg"].append(comp)
                self._indexer.register_component(
                    sid, cid, len(subject_ref["component_pg"]) - 1
                )

    def _validate_metas(self, metas: list[dict]) -> list[PGQueryMeta]:
        return [validate_query_meta(m) for m in metas]

    def _group_metas_by_component(
        self, metas: list[PGQueryMeta]
    ) -> dict[str, list[PGQueryMeta]]:
        grouped: dict[str, list[PGQueryMeta]] = defaultdict(list)
        for meta in metas:
            grouped[meta["component"]].append(meta)
        return grouped

    def _subject_pass_filter(self, subj: dict) -> bool:
        return subj.get("is_subject_destroyed", False)

    def _extract_fields_from_subject(
        self,
        subj: dict,
        sid: str,
        metas_by_component: dict[str, list[PGQueryMeta]],
        result: dict[str, dict[str, Any]],
    ):
        for comp in subj.get("component_pg", []):
            cid = comp["component"]["id"]

            for component_name, metas in metas_by_component.items():
                if component_name not in comp:
                    continue

                comp_data = comp[component_name]

                for meta in metas:
                    allow_multiple = meta.get("allow_multiple", False)
                    for field in meta["fields"]:
                        if field not in comp_data:
                            continue

                        field_name = meta.get("as_", {}).get(field, field)
                        result.setdefault(sid, {})

                        if allow_multiple:
                            result[sid].setdefault(field_name, []).append(
                                {
                                    "component_id": cid,
                                    "value": comp_data[field],
                                }
                            )
                        else:
                            result[sid][field_name] = comp_data[field]
