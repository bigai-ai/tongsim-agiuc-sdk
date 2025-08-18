"""
connection.grpc.unary_stream_api

封装所有 unary-stream 类型接口为标准 Python 方法。
使用 async for 逻辑，由调用层负责控制并发。
"""

from collections.abc import AsyncIterator, Sequence

from grpc.aio import UnaryStreamCall
from tongsim_api_protocol import basic_pb2
from tongsim_api_protocol.component.voxel_pb2 import SubscribeVoxelRequest
from tongsim_api_protocol.component.voxel_pb2_grpc import VoxelServiceStub
from tongsim_api_protocol.subsystem.acoustics_manager_pb2 import AudioStreamRequest
from tongsim_api_protocol.subsystem.acoustics_manager_pb2_grpc import (
    AcousticsManagerServiceStub,
)
from tongsim_api_protocol.subsystem.camera_pb2 import CameraConfig, ImageRequest
from tongsim_api_protocol.subsystem.camera_pb2_grpc import CameraServiceStub
from tongsim_api_protocol.subsystem.event_stream_pb2_grpc import EventStreamServiceStub
from tongsim_api_protocol.subsystem.pg_pb2_grpc import PGServiceStub

from tongsim.math import Vector3

from .core import GrpcConnection
from .type import AudioDataWrapper, CameraImageRequest, CameraImageWrapper
from .utils import safe_unary_stream, sdk_to_proto


class UnaryStreamAPI:
    """
    Proto unary-stream 接口封装，返回 async iterator。
    调用方式:

        async for resp in UnaryStreamAPI.unary_stream_call(...):
    """

    @staticmethod
    @safe_unary_stream()
    async def subscribe_image(
        conn: GrpcConnection,
        image_requests: Sequence[CameraImageRequest],
        stream_name="",
    ) -> AsyncIterator[list[CameraImageWrapper]]:
        stub = conn.get_stub(CameraServiceStub)

        req = ImageRequest(
            camera_config_list=[image_req.to_proto() for image_req in image_requests],
            stream_name=stream_name,
        )

        # 发起请求，获取流式响应, 以迭代器返回
        stream_call = stub.SubscribeImage(req)
        async for response in stream_call:
            yield [
                CameraImageWrapper(camera_image)
                for camera_image in response.camera_image_list
            ]

    @staticmethod
    @safe_unary_stream()
    async def subscribe_audio(
        conn: GrpcConnection,
    ) -> AsyncIterator[AudioDataWrapper]:
        stub = conn.get_stub(AcousticsManagerServiceStub)

        req = AudioStreamRequest()

        # 发起请求，获取流式响应, 以迭代器返回
        stream_call = stub.StartAudioStream(req)
        async for response in stream_call:
            yield AudioDataWrapper(response.audio_data)

    @staticmethod
    @safe_unary_stream()
    async def subscribe_hf_image(
        conn: GrpcConnection,
        camera_id: str = "",
        rgb: bool = True,
        depth: bool = False,
        segmentation: bool = False,
    ) -> AsyncIterator[list[CameraImageWrapper]]:
        stub = conn.get_stub(CameraServiceStub)

        req = ImageRequest(
            camera_config_list=[
                CameraConfig(
                    camera_id=camera_id,
                    b_rgb=rgb,
                    b_depth=depth,
                    b_segmentation=segmentation,
                )
            ],
        )

        # 发起请求，获取流式响应, 以迭代器返回
        stream_call = stub.SubscribeCustomRenderImage(req)
        async for response in stream_call:
            yield [
                CameraImageWrapper(camera_image)
                for camera_image in response.camera_image_list
            ]

    @staticmethod
    @safe_unary_stream()
    async def subscribe_voxel(
        conn: GrpcConnection,
        component_id: str,
        rate: float,
        voxel_half_resolution: tuple[int, int, int],
        voxel_extent: Vector3,
        center_offset: Vector3,
        is_ignore_self: bool = True,
        ignore_subjects: Sequence[str] | None = None,
    ) -> AsyncIterator[bytes]:
        stub = conn.get_stub(VoxelServiceStub)
        request = SubscribeVoxelRequest(
            component=basic_pb2.Component(id=component_id),
            rate=rate,
            voxel_half_num_x=voxel_half_resolution[0],
            voxel_half_num_y=voxel_half_resolution[1],
            voxel_half_num_z=voxel_half_resolution[2],
            extent=sdk_to_proto(voxel_extent),
            box_center_offset=sdk_to_proto(center_offset),
            is_ignore_self=is_ignore_self,
            subjects=(
                [
                    basic_pb2.Subject(id=ignore_subject_id)
                    for ignore_subject_id in ignore_subjects
                ]
                if ignore_subjects
                else []
            ),
        )
        stream_call = stub.SubscribeVoxel(request)
        async for response in stream_call:
            yield response.voxel

    # pg 流需要被主动 cancel，直接返回 UnaryStreamCall
    @staticmethod
    def subscribe_pg(conn: GrpcConnection) -> UnaryStreamCall:
        stub = conn.get_stub(PGServiceStub)
        req = basic_pb2.EmptyRequest()
        return stub.SubScribePG(req)

    @staticmethod
    @safe_unary_stream()
    async def subscribe_collision(
        conn: GrpcConnection, subject_id: str
    ) -> AsyncIterator[str]:
        stub = conn.get_stub(EventStreamServiceStub)
        req = basic_pb2.Subject(id=subject_id)
        stream_call = stub.SubScribeOverlapEvent(req)
        async for response in stream_call:
            yield response.subject.id
