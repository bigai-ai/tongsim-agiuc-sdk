from tongsim.connection import tags as tag
from tongsim.math.geometry import Pose, Quaternion, Vector3

from ._legacy.action_id import ActionID
from ._legacy.attribute_id import AttributeIDs
from ._legacy.generated.TongosAgentGRPCForUE_pb2 import (
    FunctionRequest,
    FunctionResponse,
)
from ._legacy.generated.TongosAgentGRPCForUE_pb2_grpc import ServiceInterfaceStub
from ._legacy.streamer import LegacyStreamClient
from ._legacy.utils import pack_to_request, parse_from_response
from .core import GrpcConnection
from .utils import safe_async_rpc

_SERVE_INIT = 0
_SERVE_SUCCESS = 1

__all__ = ["LegacyAPI"]


class LegacyAPIError(Exception):
    def __init__(self, message: str, code: int):
        super().__init__(
            f"LegacyAPI call failed with code {code}\n message: {message}\n"
        )
        self.code = code
        self.message = message


class LegacyAPI:
    """
    已丢弃的一套通信接口，该类将其通信 封装成原生 Python 静态方法。
    TODO: 全部迁移到到基于 tongsim_api_protocol 的通信中。
    """

    # === tongos.service.ServiceInterface ===
    @staticmethod
    @safe_async_rpc(raise_on_error=True)
    async def call_function(
        conn: GrpcConnection, request: FunctionRequest
    ) -> FunctionResponse:
        return await conn.get_stub(ServiceInterfaceStub).CallFunction(
            request, timeout=20.0
        )

    # ====== SceneManager.SpawnerComponent ======
    @staticmethod
    @safe_async_rpc(default=False)
    async def open_level(conn: GrpcConnection, level_name: str) -> bool:
        req: FunctionRequest = FunctionRequest(
            subject_name=tag.SubjectTags.SCENE_MANAGER,
            component_name=tag.ComponentTags.SPAWNER,
            action_name=ActionID.OPEN_LEVEL,
        )
        pack_to_request(value=level_name, request=req)
        resp: FunctionResponse = await LegacyAPI.call_function(conn, req)

        if resp.code not in (_SERVE_SUCCESS, _SERVE_INIT):
            raise LegacyAPIError(resp.msg, resp.code)

        return True

    @staticmethod
    @safe_async_rpc(default=[])
    async def get_object_ids_by_name(
        conn: GrpcConnection, object_name: str
    ) -> list[str]:
        req: FunctionRequest = FunctionRequest(
            subject_name=tag.SubjectTags.SCENE_MANAGER,
            component_name=tag.ComponentTags.SPAWNER,
            action_name=ActionID.GET_OBJECT_BY_NAME,
        )
        pack_to_request(value=object_name, request=req)
        resp: FunctionResponse = await LegacyAPI.call_function(conn, req)
        if resp.code is not _SERVE_SUCCESS:
            raise LegacyAPIError(resp.msg, resp.code)
        object_ids: list[str] = parse_from_response(list[str], response=resp, index=0)
        return object_ids

    @staticmethod
    @safe_async_rpc(default="")
    async def spawn_camera_group(
        conn: GrpcConnection,
        desired_name: str,
        location: Vector3 | None = None,
        rotation: Quaternion | None = None,
    ) -> str:
        if location is None:
            location = Vector3()
        if rotation is None:
            rotation = Quaternion()

        req: FunctionRequest = FunctionRequest(
            subject_name=tag.SubjectTags.SCENE_MANAGER,
            component_name=tag.ComponentTags.SPAWNER,
            action_name=ActionID.SPAWN_CAMERA_GROUP,
        )
        pack_to_request(value=desired_name, request=req)
        pack_to_request(value=location, request=req)
        pack_to_request(value=rotation, request=req)
        resp: FunctionResponse = await LegacyAPI.call_function(conn, req)

        if resp.code is not _SERVE_SUCCESS:
            raise LegacyAPIError(resp.msg, resp.code)
        camera_group_id: str = parse_from_response(str, response=resp, index=0)
        return camera_group_id

    @staticmethod
    @safe_async_rpc(default=False)
    async def start_capture_image_offline(
        conn: GrpcConnection,
        camera_name_list: list[str],
        duration: int,
        output_path_name: str,
        is_capture_depth: bool,
        is_capture_segment: bool,
    ) -> bool:
        req: FunctionRequest = FunctionRequest(
            subject_name=tag.SubjectTags.SCENE_MANAGER,
            component_name=tag.ComponentTags.SPAWNER,
            action_name=ActionID.START_CAPTURE_OFFLINE,
        )
        pack_to_request(value=camera_name_list, request=req)
        pack_to_request(value=duration, request=req)
        pack_to_request(value=output_path_name, request=req)
        pack_to_request(value=is_capture_depth, request=req)
        pack_to_request(value=is_capture_segment, request=req)
        resp: FunctionResponse = await LegacyAPI.call_function(conn, req)
        if resp.code is not _SERVE_SUCCESS:
            raise LegacyAPIError(resp.msg, resp.code)
        return True

    @staticmethod
    @safe_async_rpc(default=None)
    async def get_random_spawner_location(
        conn: GrpcConnection, room_name: str = ""
    ) -> Vector3 | None:
        req: FunctionRequest = FunctionRequest(
            subject_name=tag.SubjectTags.SCENE_MANAGER,
            component_name=tag.ComponentTags.SPAWNER,
            action_name=ActionID.GET_RANDOM_SPAWN_LOCATION,
        )
        pack_to_request(value=room_name, request=req)
        resp: FunctionResponse = await LegacyAPI.call_function(conn, req)
        if resp.code is not _SERVE_SUCCESS:
            raise LegacyAPIError(resp.msg, resp.code)
        return parse_from_response(Vector3, resp, 0)

    @staticmethod
    @safe_async_rpc(default=False)
    async def destroy_object(conn: GrpcConnection, object_id: str) -> True:
        req: FunctionRequest = FunctionRequest(
            subject_name=tag.SubjectTags.SCENE_MANAGER,
            component_name=tag.ComponentTags.SPAWNER,
            action_name=ActionID.DESTROY_OBJECT,
        )
        pack_to_request(value=object_id, request=req)
        resp: FunctionResponse = await LegacyAPI.call_function(conn, req)
        if resp.code is not _SERVE_SUCCESS:
            raise LegacyAPIError(resp.msg, resp.code)
        return True

    # ====== AnimComponent ======
    @staticmethod
    @safe_async_rpc(default=[])
    async def get_playable_animation_names(
        conn: GrpcConnection, subject_id: str
    ) -> list[str]:
        req: FunctionRequest = FunctionRequest(
            subject_name=subject_id,
            component_name=tag.ComponentTags.ANIM,
            action_name=ActionID.GET_VALUE_CALL,
        )

        pack_to_request(AttributeIDs.PLAYABLE_ANIMS, req)
        resp: FunctionResponse = await LegacyAPI.call_function(conn, req)

        if resp.code is not _SERVE_SUCCESS:
            raise LegacyAPIError(resp.msg, resp.code)

        return parse_from_response(list[str], resp, 0)

    @staticmethod
    @safe_async_rpc(default=False)
    async def enable_idle_anim(
        conn: GrpcConnection,
        subject_id: str,
        is_enable: bool,
    ) -> bool:
        req: FunctionRequest = FunctionRequest(
            subject_name=subject_id,
            component_name=tag.ComponentTags.ANIM,
            action_name=ActionID.ENABLE_BABY_AI,
        )
        pack_to_request(value=is_enable, request=req)
        resp: FunctionResponse = await LegacyAPI.call_function(conn, req)
        if resp.code is not _SERVE_SUCCESS:
            raise LegacyAPIError(resp.msg, resp.code)
        return True

    @staticmethod
    @safe_async_rpc(default=None)
    async def is_anim_queue_empty(
        conn: GrpcConnection,
        subject_id: str,
    ) -> bool | None:
        req: FunctionRequest = FunctionRequest(
            subject_name=subject_id,
            component_name=tag.ComponentTags.ANIM,
            action_name=ActionID.IS_ALL_ANIM_COMPLETED,
        )
        resp: FunctionResponse = await LegacyAPI.call_function(conn, req)
        if resp.code is not _SERVE_SUCCESS:
            raise LegacyAPIError(resp.msg, resp.code)
        return parse_from_response(bool, resp, 0)

    # ====== FoodEnergyComponent ======
    @staticmethod
    @safe_async_rpc(default=[])
    async def get_food_energy(conn: GrpcConnection, subject_id: str) -> tuple:
        req: FunctionRequest = FunctionRequest(
            subject_name=subject_id,
            component_name=tag.ComponentTags.FOOD_ENERGY,
            action_name=ActionID.GET_VALUE_CALL,
        )

        pack_to_request(AttributeIDs.FOOD_ENERGY, req)
        resp: FunctionResponse = await LegacyAPI.call_function(conn, req)

        if resp.code is not _SERVE_SUCCESS:
            raise LegacyAPIError(resp.msg, resp.code)

        anti_hungry = parse_from_response(float, resp, 0)
        anti_thirsty = parse_from_response(float, resp, 1)

        return anti_hungry, anti_thirsty

    @staticmethod
    @safe_async_rpc(default=False)
    async def set_eatable_energy(
        streamer: LegacyStreamClient,
        subject_id: str,
        anti_hungry: float,
        anti_thirsty: float,
        maxparts_num: int,
    ) -> bool:
        req: FunctionRequest = FunctionRequest(
            subject_name=subject_id,
            component_name=tag.ComponentTags.FOOD_ENERGY,
            action_name=ActionID.SET_VALUE_STREAM,
        )

        pack_to_request(AttributeIDs.FOOD_ENERGY, req)
        pack_to_request(float(anti_hungry), req)
        pack_to_request(float(anti_thirsty), req)
        pack_to_request(int(maxparts_num), req)
        pack_to_request(0, req)  # TODO: 0 is edible
        return await streamer.write(req)

    @staticmethod
    @safe_async_rpc(default=False)
    async def set_drinkable_energy(
        streamer: LegacyStreamClient,
        subject_id: str,
        anti_hungry: float,
        anti_thirsty: float,
        maxparts_num: int,
    ) -> bool:
        req: FunctionRequest = FunctionRequest(
            subject_name=subject_id,
            component_name=tag.ComponentTags.FOOD_ENERGY,
            action_name=ActionID.SET_VALUE_STREAM,
        )

        pack_to_request(AttributeIDs.FOOD_ENERGY, req)
        pack_to_request(float(anti_hungry), req)
        pack_to_request(float(anti_thirsty), req)
        pack_to_request(int(maxparts_num), req)
        pack_to_request(1, req)  # TODO: 1 is beverage
        return await streamer.write(req)

    # ====== ImageComponent ======
    @staticmethod
    @safe_async_rpc(default="")
    async def spawn_camera(
        conn: GrpcConnection,
        subject_id: str,
        camera_name: str,
        location: Vector3,
        rotation: Quaternion,
        width: float,
        height: float,
        stream_name: str | None = None,
        enable_dynamic_shadow: bool = False,
        is_snap_shot: bool = False,
    ) -> str:
        if stream_name is None:
            stream_name = camera_name

        req: FunctionRequest = FunctionRequest(
            subject_name=subject_id,
            component_name=tag.ComponentTags.IMAGE,
            action_name=ActionID.SPAWN_CAMERA,
        )
        pack_to_request(camera_name, req)
        pack_to_request(location, req)
        pack_to_request(rotation, req)
        pack_to_request(is_snap_shot, req)
        pack_to_request(width, req)
        pack_to_request(height, req)
        pack_to_request(enable_dynamic_shadow, req)
        resp: FunctionResponse = await LegacyAPI.call_function(conn, req)

        if resp.code is not _SERVE_SUCCESS:
            raise LegacyAPIError(resp.msg, resp.code)
        camera_id: str = parse_from_response(str, response=resp, index=0)
        return camera_id

    @staticmethod
    @safe_async_rpc(default=False)
    async def attach_cameras_to_sockets(
        conn: GrpcConnection,
        subject_id: str,
        camera_id_list: list[str],
        socket_name_list: list[str],
    ) -> bool:
        req: FunctionRequest = FunctionRequest(
            subject_name=subject_id,
            component_name=tag.ComponentTags.IMAGE,
            action_name=ActionID.ATTACH_CAMERAS_TO_SOCKETS,
        )
        pack_to_request(camera_id_list, req)
        pack_to_request(socket_name_list, req)
        resp: FunctionResponse = await LegacyAPI.call_function(conn, req)

        if resp.code is not _SERVE_SUCCESS:
            raise LegacyAPIError(resp.msg, resp.code)
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def set_camera_intrinsic_params(
        streamer: LegacyStreamClient,
        subject_id: str,
        camera_id: str,
        fov: float,
        width: float,
        height: float,
    ) -> bool:
        req: FunctionRequest = FunctionRequest(
            subject_name=subject_id,
            component_name=tag.ComponentTags.IMAGE,
            action_name=ActionID.SET_VALUE_STREAM,
        )

        pack_to_request(AttributeIDs.CAMERA_INTRINSIC, req)
        pack_to_request(camera_id, req)
        pack_to_request(fov, req)
        pack_to_request(width, req)
        pack_to_request(height, req)

        return await streamer.write(req)

    # ====== PoseComponent ======
    @staticmethod
    @safe_async_rpc(default=None)
    async def get_pose(conn: GrpcConnection, subject_id: str) -> Pose:
        req: FunctionRequest = FunctionRequest(
            subject_name=subject_id,
            component_name=tag.ComponentTags.POSE,
            action_name=ActionID.GET_VALUE_CALL,
        )

        pack_to_request(AttributeIDs.POSE, req)
        resp: FunctionResponse = await LegacyAPI.call_function(conn, req)

        if resp.code is not _SERVE_SUCCESS:
            raise LegacyAPIError(resp.msg, resp.code)
        loc: Vector3 = parse_from_response(Vector3, response=resp, index=0)
        quat: Quaternion = parse_from_response(Quaternion, response=resp, index=1)
        return Pose(loc, quat)

    @staticmethod
    @safe_async_rpc(default=False)
    async def set_pose(conn: GrpcConnection, subject_id: str, pose: Pose) -> bool:
        req: FunctionRequest = FunctionRequest(
            subject_name=subject_id,
            component_name=tag.ComponentTags.POSE,
            action_name=ActionID.CALL_SET_POSE,
        )

        pack_to_request(pose.location, req)
        pack_to_request(pose.rotation, req)
        resp: FunctionResponse = await LegacyAPI.call_function(conn, req)

        if resp.code is not _SERVE_SUCCESS:
            raise LegacyAPIError(resp.msg, resp.code)
        return True

    # ====== ObjectStateComponent ======
    @staticmethod
    @safe_async_rpc(default=False)
    async def set_object_state(conn: GrpcConnection, subject_id: str, state: bool):
        req: FunctionRequest = FunctionRequest(
            subject_name=subject_id,
            component_name=tag.ComponentTags.OBJECT_STATE,
            action_name=ActionID.SET_OBJECT_STATE,
        )

        pack_to_request(state, req)
        resp: FunctionResponse = await LegacyAPI.call_function(conn, req)

        if resp.code is not _SERVE_SUCCESS:
            raise LegacyAPIError(resp.msg, resp.code)
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def set_group_id(conn: GrpcConnection, subject_id: str, group_id: str):
        req: FunctionRequest = FunctionRequest(
            subject_name=subject_id,
            component_name=tag.ComponentTags.OBJECT_STATE,
            action_name=ActionID.SET_GROUP_ID,
        )

        pack_to_request(group_id, req)
        resp: FunctionResponse = await LegacyAPI.call_function(conn, req)

        if resp.code is not _SERVE_SUCCESS:
            raise LegacyAPIError(resp.msg, resp.code)
        return True

    # ====== CollisionShapeComponent ======
    @staticmethod
    @safe_async_rpc(default=None)
    async def get_aabb(
        conn: GrpcConnection, subject_id: str, update_collision=True
    ) -> tuple | None:
        req: FunctionRequest = FunctionRequest(
            subject_name=subject_id,
            component_name=tag.ComponentTags.COLLISION,
            action_name=ActionID.GET_VALUE_CALL,
        )

        pack_to_request(AttributeIDs.AABB, req)
        pack_to_request(update_collision, req)
        resp: FunctionResponse = await LegacyAPI.call_function(conn, req)

        if resp.code is not _SERVE_SUCCESS:
            raise LegacyAPIError(resp.msg, resp.code)

        float_list: list[float] = parse_from_response(list[float], resp, 0)
        min_vertex = Vector3(x=float_list[0], y=float_list[1], z=float_list[2])
        max_vertex = Vector3(x=float_list[3], y=float_list[4], z=float_list[5])
        return min_vertex, max_vertex

    # ====== ScaleComponent ======
    @staticmethod
    @safe_async_rpc(default=None)
    async def get_scale(
        conn: GrpcConnection,
        subject_id: str,
    ) -> Vector3:
        req: FunctionRequest = FunctionRequest(
            subject_name=subject_id,
            component_name=tag.ComponentTags.SCALE,
            action_name=ActionID.GET_VALUE_CALL,
        )
        pack_to_request(AttributeIDs.SCALE, req)
        resp: FunctionResponse = await LegacyAPI.call_function(conn, req)
        return parse_from_response(Vector3, resp, 0)

    @staticmethod
    @safe_async_rpc(default=False)
    async def set_scale(
        streamer: LegacyStreamClient, subject_id: str, new_scale: Vector3
    ) -> bool:
        req: FunctionRequest = FunctionRequest(
            subject_name=subject_id,
            component_name=tag.ComponentTags.SCALE,
            action_name=ActionID.SET_VALUE_STREAM,
        )

        pack_to_request(AttributeIDs.SCALE, req)
        pack_to_request(new_scale, req)

        return await streamer.write(req)
