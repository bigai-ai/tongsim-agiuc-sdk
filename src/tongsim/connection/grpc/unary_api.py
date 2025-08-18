from collections.abc import Sequence

from tongsim_api_protocol import basic_pb2
from tongsim_api_protocol.component.animation.animation_pb2_grpc import (
    AnimationServiceStub,
)
from tongsim_api_protocol.component.attachment_pb2 import ObjectInHandParam
from tongsim_api_protocol.component.attachment_pb2_grpc import AttachmentServiceStub
from tongsim_api_protocol.component.character_attribute_pb2 import MoveAttribute
from tongsim_api_protocol.component.character_attribute_pb2_grpc import (
    CharacterAttributeServiceStub,
)
from tongsim_api_protocol.component.door_state_pb2 import DoorStateRequest
from tongsim_api_protocol.component.door_state_pb2_grpc import DoorServiceStub
from tongsim_api_protocol.component.face_pb2 import (
    EmotionRequest,
    EmotionState,
    SpeakTextWithTongOSRequest,
)
from tongsim_api_protocol.component.face_pb2_grpc import FaceServiceStub
from tongsim_api_protocol.component.object_state_pb2 import (
    ActiveState,
    IsPowered,
    SetGroupIDRequest,
    SetLightColorRequest,
    SetObjectUITextRequest,
)
from tongsim_api_protocol.component.object_state_pb2_grpc import ObjectStateServiceStub
from tongsim_api_protocol.component.pose_pb2_grpc import PoseServiceStub
from tongsim_api_protocol.component.spawner_pb2 import (
    SpawnObjectRequest,
    SpawnObjectResponse,
)
from tongsim_api_protocol.subject.subject_pb2 import ComponentsMap
from tongsim_api_protocol.subject.subject_pb2_grpc import SubjectServiceStub
from tongsim_api_protocol.subsystem.camera_pb2 import (
    AttachCameraToTargetSocketRequest,
    CameraConfig,
    CancelImageStreamRequest,
    CreateCustomRenderRequest,
    GetCameraImageRequest,
    GetCameraImageResponse,
    GetCameraIntrinsicParamsRequest,
    GetCameraIntrinsicParamsResponse,
    SetCameraIntrinsicParamsRequest,
    SpawnCameraRequest,
    SpawnCameraResponse,
    TargetCameraMode,
    TargetCharacter,
)
from tongsim_api_protocol.subsystem.camera_pb2_grpc import CameraServiceStub
from tongsim_api_protocol.subsystem.debug_draw_pb2 import (
    Box,
    Boxes,
    Coordinates,
    DebugDrawRequest,
    Line,
    Lines,
)
from tongsim_api_protocol.subsystem.debug_draw_pb2_grpc import DebugDrawServiceStub
from tongsim_api_protocol.subsystem.distribution_pb2 import ServerURL
from tongsim_api_protocol.subsystem.distribution_pb2_grpc import DistributionServiceStub
from tongsim_api_protocol.subsystem.map_pb2 import (
    MapRoomInfo,
    NavMeshPolys,
    NavPointInRinglikeParams,
    RoomNameRequest,
)
from tongsim_api_protocol.subsystem.map_pb2_grpc import MapServiceStub
from tongsim_api_protocol.subsystem.open_world_pb2 import (
    NPCMovetoLocationRequest,
    NPCPickUpRequst,
    NPCPlayAnimationRequst,
    NPCPutDownRequst,
    NPCTurnAroundRequst,
)
from tongsim_api_protocol.subsystem.open_world_pb2_grpc import OpenWorldServiceStub
from tongsim_api_protocol.subsystem.pg_pb2 import ComponentPG, PGFrequency, SubjectPG
from tongsim_api_protocol.subsystem.pg_pb2_grpc import PGServiceStub
from tongsim_api_protocol.subsystem.record_pb2 import FinishResponse, StartRecord
from tongsim_api_protocol.subsystem.record_pb2_grpc import RecordServiceStub
from tongsim_api_protocol.subsystem.save_game_pb2_grpc import SaveGameServiceStub
from tongsim_api_protocol.subsystem.scene_pb2 import (
    AttachObjectToTargetRequest,
    BoxTraceParams,
    ContainerInteractiveParams,
    ContainerPlacedObjectInfo,
    ContainerTakeOutObjectInfo,
    DebugSpawnAllRdfObjectsRequest,
    ExecCommandRequest,
    FileContent,
    FindClosestAgentRequest,
    FindClosestDoorRequest,
    FindClosestObjectByTypeRequest,
    GetNavMeshRequest,
    GetNavMeshResponse,
    GetObjectByRdfRequest,
    GetSubjectsInViewFrustumWithAABBCullingRequest,
    ObjectListResponse,
    RequestDebugPrint,
    SphereTraceParams,
    StepRequest,
    TraceCollisionChannel,
    TraceRequest,
    TraceSubjects,
)
from tongsim_api_protocol.subsystem.scene_pb2_grpc import SceneServiceStub
from tongsim_api_protocol.subsystem.segment_pb2 import SetSegmentIdRequest
from tongsim_api_protocol.subsystem.segment_pb2_grpc import SegmentServiceStub

from tongsim.math.geometry import Quaternion, Transform, Vector3
from tongsim.type import AnimCmdHandType, ViewModeType

from .core import GrpcConnection
from .type import CameraImageRequest, CameraImageWrapper
from .utils import proto_to_sdk, safe_async_rpc, sdk_to_proto


class UnaryAPI:
    """
    Proto unary_unary 接口封装成原生 Python 静态方法。
    """

    # === bigai.ue.component.animation ===
    @staticmethod
    @safe_async_rpc(default=False)
    async def do_task(conn: GrpcConnection, subject_id: str, component_id: str) -> bool:
        stub = conn.get_stub(AnimationServiceStub)
        await stub.DoTask(
            basic_pb2.EmptyRequest(
                subject=basic_pb2.Subject(id=subject_id),
                component=basic_pb2.Component(id=component_id),
            ),
            timeout=2.0,
        )
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def stop_current_wait_anim(conn: GrpcConnection, component_id: str) -> bool:
        stub = conn.get_stub(AnimationServiceStub)
        await stub.StopCurrentWaitAnim(
            basic_pb2.EmptyRequest(
                component=basic_pb2.Component(id=component_id),
            ),
            timeout=2.0,
        )
        return True

    # === bigai.ue.component.attachment ===
    @staticmethod
    @safe_async_rpc(default="")
    async def get_entity_id_in_hand(
        conn: GrpcConnection, component_id: str, which_hand: AnimCmdHandType
    ) -> bool:
        stub = conn.get_stub(AttachmentServiceStub)
        resp: basic_pb2.Subject = await stub.GetObjectInHand(
            ObjectInHandParam(
                component=basic_pb2.Component(id=component_id),
                which_hand_action=int(which_hand),
            ),
            timeout=2.0,
        )
        return resp.id

    # === bigai.ue.component.doorstate ===
    @staticmethod
    @safe_async_rpc(default=False)
    async def set_door_state(
        conn: GrpcConnection, component_id: str, door_state: float
    ) -> bool:
        stub = conn.get_stub(DoorServiceStub)
        await stub.SetDoorState(
            DoorStateRequest(
                component=basic_pb2.Component(id=component_id), door_state=door_state
            ),
            timeout=2.0,
        )

    # === bigai.ue.component.face ===
    @staticmethod
    @safe_async_rpc(default=False)
    async def set_emotion(
        conn: GrpcConnection,
        component_id: str,
        emotions: dict[str, float],
    ) -> bool:
        stub = conn.get_stub(FaceServiceStub)

        await stub.SetEmotion(
            EmotionRequest(
                component=basic_pb2.Component(id=component_id),
                emotion_state=EmotionState(emotion=emotions),
            ),
            timeout=2.0,
        )
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def speak_text_with_tongos(
        conn: GrpcConnection,
        component_id: str,
        text: str,
        speaker_id: str | None = None,
    ) -> bool:
        stub = conn.get_stub(FaceServiceStub)

        await stub.SpeakTextWithTongOS(
            SpeakTextWithTongOSRequest(
                component=basic_pb2.Component(id=component_id),
                text=text,
                speaker_id=speaker_id,
            ),
            timeout=2.0,
        )
        return True

    # === bigai.ue.component.objectstate ===

    @staticmethod
    @safe_async_rpc(default=None)
    async def get_interact_location(
        conn: GrpcConnection, subject_id: str, component_id: str
    ) -> Vector3:
        stub = conn.get_stub(ObjectStateServiceStub)
        resp: basic_pb2.Vector3 = await stub.GetInteractLocation(
            basic_pb2.EmptyRequest(
                subject=basic_pb2.Subject(id=subject_id),
                component=basic_pb2.Component(id=component_id),
            ),
            timeout=2.0,
        )
        return proto_to_sdk(resp)

    @staticmethod
    @safe_async_rpc(default=None)
    async def get_place_location(
        conn: GrpcConnection, subject_id: str, component_id: str
    ) -> Vector3:
        stub = conn.get_stub(ObjectStateServiceStub)
        resp: basic_pb2.Vector3 = await stub.GetPlaceLocation(
            basic_pb2.EmptyRequest(
                subject=basic_pb2.Subject(id=subject_id),
                component=basic_pb2.Component(id=component_id),
            ),
            timeout=2.0,
        )
        return proto_to_sdk(resp)

    @staticmethod
    @safe_async_rpc(default=None)
    async def get_asset_name(
        conn: GrpcConnection, subject_id: str, component_id: str
    ) -> str:
        stub = conn.get_stub(ObjectStateServiceStub)
        resp: basic_pb2.String = await stub.GetAssetName(
            basic_pb2.EmptyRequest(
                subject=basic_pb2.Subject(id=subject_id),
                component=basic_pb2.Component(id=component_id),
            ),
            timeout=2.0,
        )
        return resp.string

    @staticmethod
    @safe_async_rpc(default=False)
    async def set_group_id(
        conn: GrpcConnection, component_id: str, groud_id: str
    ) -> bool:
        stub = conn.get_stub(ObjectStateServiceStub)
        await stub.SetGroupID(
            SetGroupIDRequest(
                component=basic_pb2.Component(id=component_id),
                groud_id=groud_id,
            ),
            timeout=2.0,
        )
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def get_is_powered(
        conn: GrpcConnection, subject_id: str, component_id: str
    ) -> bool:
        stub = conn.get_stub(ObjectStateServiceStub)
        resp: basic_pb2.Bool = await stub.GetIsPowered(
            basic_pb2.EmptyRequest(
                subject=basic_pb2.Subject(id=subject_id),
                component=basic_pb2.Component(id=component_id),
            ),
            timeout=2.0,
        )
        return resp.bool

    @staticmethod
    @safe_async_rpc(default=False)
    async def set_is_powered(
        conn: GrpcConnection, component_id: str, new_is_powered: bool
    ) -> bool:
        stub = conn.get_stub(ObjectStateServiceStub)
        await stub.SetIsPowered(
            IsPowered(
                component=basic_pb2.Component(id=component_id), is_power=new_is_powered
            ),
            timeout=2.0,
        )
        return True

    @staticmethod
    @safe_async_rpc(default="")
    async def get_group_id(
        conn: GrpcConnection, subject_id: str, component_id: str
    ) -> str:
        stub = conn.get_stub(ObjectStateServiceStub)
        resp: basic_pb2.String = await stub.GetGroupID(
            basic_pb2.EmptyRequest(
                subject=basic_pb2.Subject(id=subject_id),
                component=basic_pb2.Component(id=component_id),
            ),
            timeout=2.0,
        )
        return resp.string

    @staticmethod
    @safe_async_rpc(default="")
    async def get_type(conn: GrpcConnection, subject_id: str, component_id: str) -> str:
        stub = conn.get_stub(ObjectStateServiceStub)
        resp: basic_pb2.String = await stub.GetType(
            basic_pb2.EmptyRequest(
                subject=basic_pb2.Subject(id=subject_id),
                component=basic_pb2.Component(id=component_id),
            ),
            timeout=2.0,
        )
        return resp.string

    @staticmethod
    @safe_async_rpc(default=[])
    async def get_entity_ids_in_same_group(
        conn: GrpcConnection, subject_id: str, component_id: str
    ) -> list[str]:
        stub = conn.get_stub(ObjectStateServiceStub)
        resp: basic_pb2.Subjects = await stub.GetSubjectsInSameGroup(
            basic_pb2.EmptyRequest(
                subject=basic_pb2.Subject(id=subject_id),
                component=basic_pb2.Component(id=component_id),
            ),
            timeout=2.0,
        )
        return [subject.id for subject in resp.subjects]

    @staticmethod
    @safe_async_rpc(default=False)
    async def get_active_state(
        conn: GrpcConnection, subject_id: str, component_id: str
    ) -> bool:
        stub = conn.get_stub(ObjectStateServiceStub)
        resp: ActiveState = await stub.GetActiveState(
            basic_pb2.EmptyRequest(
                subject=basic_pb2.Subject(id=subject_id),
                component=basic_pb2.Component(id=component_id),
            ),
            timeout=2.0,
        )
        return resp.is_active

    # === bigai.ue.component.pose ===

    @staticmethod
    @safe_async_rpc(default=None)
    async def get_forward_vector(
        conn: GrpcConnection, subject_id: str, component_id: str
    ) -> Vector3:
        stub = conn.get_stub(PoseServiceStub)
        resp: basic_pb2.Vector3 = await stub.GetForwardVector(
            basic_pb2.EmptyRequest(
                subject=basic_pb2.Subject(id=subject_id),
                component=basic_pb2.Component(id=component_id),
            ),
            timeout=2.0,
        )
        return proto_to_sdk(resp)

    @staticmethod
    @safe_async_rpc(default=None)
    async def get_right_vector(
        conn: GrpcConnection, subject_id: str, component_id: str
    ) -> Vector3:
        stub = conn.get_stub(PoseServiceStub)
        resp: basic_pb2.Vector3 = await stub.GetRightVector(
            basic_pb2.EmptyRequest(
                subject=basic_pb2.Subject(id=subject_id),
                component=basic_pb2.Component(id=component_id),
            ),
            timeout=2.0,
        )
        return proto_to_sdk(resp)

    # TODO: get_pose 和 set_pose 的方法 TongSim C++ 侧未实现:
    # @staticmethod
    # @safe_async_rpc(default=None)
    # async def get_pose(conn: GrpcConnection, component_id: str) -> Pose:
    #     stub = conn.get_stub(PoseServiceStub)
    #     resp: basic_pb2.Pose = await stub.GetPose(
    #         basic_pb2.Component(id=component_id), timeout=5.0
    #     )
    #     return proto_to_sdk(resp)

    # @staticmethod
    # @safe_async_rpc(default=False)
    # async def set_pose(conn: GrpcConnection, component_id: str, pose: Pose) -> bool:
    #     stub = conn.get_stub(PoseServiceStub)
    #     await stub.SetPose(
    #         SetPoseRequest(
    #             component=basic_pb2.Component(id=component_id), pose=sdk_to_proto(pose)
    #         ),
    #         timeout=5.0,
    #     )
    #     return True

    # === bigai.ue.subject.subject ===
    @staticmethod
    @safe_async_rpc(default=None)
    async def query_components(
        conn: GrpcConnection, subject_id: str
    ) -> dict[str, str] | None:
        stub = conn.get_stub(SubjectServiceStub)
        resp: ComponentsMap = await stub.QueryComponents(
            basic_pb2.Subject(id=subject_id), timeout=2.0
        )
        return dict(resp.components_map.items())

    # === bigai.ue.subsystem.camera ===
    @staticmethod
    @safe_async_rpc(default=None)
    async def get_camera_image(
        conn: GrpcConnection, image_request: CameraImageRequest
    ) -> CameraImageWrapper:
        stub = conn.get_stub(CameraServiceStub)
        resp: GetCameraImageResponse = await stub.GetCameraImage(
            GetCameraImageRequest(camera_config=image_request.to_proto()), timeout=10.0
        )
        return CameraImageWrapper(resp.camera_image_res)

    @staticmethod
    @safe_async_rpc(default=False)
    async def cancel_image_stream(conn: GrpcConnection, image_stream_name: str) -> bool:
        stub = conn.get_stub(CameraServiceStub)
        req = CancelImageStreamRequest(stream_name=image_stream_name)
        await stub.CancelImageStream(req, timeout=2.0)
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def spawn_camera(
        conn: GrpcConnection,
        camera_name: str,
        location: Vector3,
        rotation: Quaternion,
        fov: float = 90.0,
        width: float = 1280.0,
        height: float = 720.0,
        stream_name: str | None = None,
    ) -> str:
        if stream_name is None:
            stream_name = camera_name
        stub = conn.get_stub(CameraServiceStub)
        req: SpawnCameraRequest = SpawnCameraRequest(
            camera_name=camera_name,
            stream_name=stream_name,
            location=sdk_to_proto(location),
            rotation=sdk_to_proto(rotation),
            resolution=basic_pb2.Vector2(x=width, y=height),
            fov=fov,
        )
        resp: SpawnCameraResponse = await stub.SpawnCamera(req, timeout=5.0)
        return resp.camera_name

    @staticmethod
    @safe_async_rpc(default=False)
    async def spawn_hf_camera(
        conn: GrpcConnection,
        camera_id: str,
        frequency: int,
        socket: str,
        rgb: bool = True,
        depth: bool = False,
        segmentation: bool = False,
        attach_owner: str = "",
        fov: float = 90.0,
        width: int = 1280,
        height: int = 720,
    ) -> bool:
        stub = conn.get_stub(CameraServiceStub)
        req: CreateCustomRenderRequest = CreateCustomRenderRequest(
            render_config=CameraConfig(
                camera_id=camera_id,
                b_rgb=rgb,
                b_depth=depth,
                b_segmentation=segmentation,
            ),
            width=width,
            height=height,
            frequency=frequency,
            fov=fov,
            attach_socket_name=socket,
            attach_owner=attach_owner,
        )
        await stub.CreateCustomRender(req, timeout=5.0)
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def attach_camera_to_target_socket(
        conn: GrpcConnection,
        camera_id: str,
        target_id: str,
        socket_name: str,
    ) -> bool:
        stub = conn.get_stub(CameraServiceStub)
        req = AttachCameraToTargetSocketRequest(
            camera_name=camera_id,
            target_name=target_id,
            socket_name=socket_name,
        )
        await stub.AttachCameraToTargetSocket(req, timeout=2.0)
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def set_camera_intrinsic_params(
        conn: GrpcConnection,
        camera_id: str,
        fov: float,
        width: int,
        height: int,
    ) -> bool:
        stub = conn.get_stub(CameraServiceStub)
        req = SetCameraIntrinsicParamsRequest(
            camera_name=camera_id, fov=fov, width=width, height=height
        )
        await stub.SetCameraIntrinsicParams(req, timeout=2.0)
        return True

    @staticmethod
    @safe_async_rpc(default=[0.0, 0, 0])
    async def get_camera_intrinsic_params(
        conn: GrpcConnection,
        camera_id: str,
    ) -> tuple[float, int, int]:
        stub = conn.get_stub(CameraServiceStub)
        resp: GetCameraIntrinsicParamsResponse = await stub.GetCameraIntrinsicParams(
            GetCameraIntrinsicParamsRequest(camera_name=camera_id), timeout=2.0
        )
        return resp.fov, resp.width, resp.height

    @staticmethod
    @safe_async_rpc(default=False)
    async def switch_camera_mode(conn: GrpcConnection, view_mode: ViewModeType) -> bool:
        stub = conn.get_stub(CameraServiceStub)
        await stub.SwitchCameraMode(
            TargetCameraMode(camera_mode=view_mode),
            timeout=2.0,
        )
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def camera_switch_character(conn: GrpcConnection, character_id: str) -> bool:
        stub = conn.get_stub(CameraServiceStub)
        await stub.SwitchCharacter(
            TargetCharacter(subject=basic_pb2.Subject(id=character_id)),
            timeout=2.0,
        )
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def set_camera_mode_socket(conn: GrpcConnection, socket_name: str) -> bool:
        stub = conn.get_stub(CameraServiceStub)
        await stub.SetFirstCameraModeSocket(
            basic_pb2.String(string=socket_name),
            timeout=2.0,
        )
        return True

    # === bigai.ue.subsystem.distribution ===
    @staticmethod
    @safe_async_rpc(default=False)
    async def sync_connect_to_ue_server(conn: GrpcConnection, url: str) -> bool:
        stub = conn.get_stub(DistributionServiceStub)
        await stub.SyncConnectToUEServer(ServerURL(url=url), timeout=20.0)
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def sync_disconnect_from_server(conn: GrpcConnection) -> bool:
        stub = conn.get_stub(DistributionServiceStub)
        await stub.SyncDisconnectFromServer(basic_pb2.Empty(), timeout=20.0)
        return True

    # === bigai.ue.subsystem.map ===
    @staticmethod
    @safe_async_rpc(default=[])
    async def get_room_info(conn: GrpcConnection) -> list[dict]:
        stub = conn.get_stub(MapServiceStub)
        resp: MapRoomInfo = await stub.GetMapRoomInfo(
            basic_pb2.EmptyRequest(), timeout=2.0
        )
        return [
            {
                "room_name": room.room_name,
                "room_category": room.room_rdf,
                "boxes": [
                    {
                        "min": proto_to_sdk(box.min_vertex),
                        "max": proto_to_sdk(box.max_vertex),
                    }
                    for box in room.box
                ],
            }
            for room in resp.room_info
        ]

    @staticmethod
    @safe_async_rpc(default=[])
    async def get_nevmesh_polys_in_room(
        conn: GrpcConnection, room_name: str
    ) -> list[list[Vector3]]:
        stub = conn.get_stub(MapServiceStub)
        resp: NavMeshPolys = await stub.GetNavMeshPoly(
            RoomNameRequest(RoomName=room_name), timeout=2.0
        )
        return [[proto_to_sdk(vec) for vec in poly.vector] for poly in resp.NavPoly]

    # === bigai.ue.subsystem.scene ===
    @staticmethod
    @safe_async_rpc(default=False)
    async def attach_object_to_target(
        conn: GrpcConnection,
        object_id: str,
        target_id: str,
        loc: Vector3 | None = None,
        quat: Quaternion | None = None,
        socket_name: str | None = None,
    ) -> bool:
        stub = conn.get_stub(SceneServiceStub)
        await stub.AttachObjectToTarget(
            AttachObjectToTargetRequest(
                object_id=object_id,
                target_id=target_id,
                location=sdk_to_proto(loc) if loc else None,
                rotation=sdk_to_proto(quat) if quat else None,
                socket_name=socket_name,
            ),
            timeout=2.0,
        )
        return True

    @staticmethod
    @safe_async_rpc(default=[])
    async def get_subjects_in_view_frustum_with_aabb_culling(
        conn: GrpcConnection,
        camera_loc: Vector3,
        camera_rot: Quaternion,
        fov: float,
        view_width: float,
        view_height: float,
        depthbuffer_width: int,
        depthbuffer_height: int,
        near_clip: float = 0.0,
        far_clip: float = 2097152.0,
    ) -> list[str]:
        stub = conn.get_stub(SceneServiceStub)
        resp: basic_pb2.Subjects = await stub.GetSubjectsInViewFrustumWithAABBCulling(
            GetSubjectsInViewFrustumWithAABBCullingRequest(
                fov=fov,
                camera_pose=basic_pb2.Pose(
                    location=basic_pb2.Vector3(
                        x=camera_loc.x, y=camera_loc.y, z=camera_loc.z
                    ),
                    rotation=basic_pb2.Quaternion(
                        x=camera_rot.x, y=camera_rot.y, z=camera_rot.z, w=camera_rot.w
                    ),
                ),
                view_width=view_width,
                view_height=view_height,
                near_clip=near_clip,
                far_clip=far_clip,  # UE 最大可见距离
                depthbuffer_width=depthbuffer_width,
                depthbuffer_height=depthbuffer_height,
            ),
            timeout=4.0,
        )
        return [vo.id for vo in resp.subjects]

    @staticmethod
    @safe_async_rpc(default=None)
    async def get_nearest_nav_point(
        conn: GrpcConnection, location: Vector3
    ) -> Vector3 | None:
        stub = conn.get_stub(SceneServiceStub)
        resp: basic_pb2.Vector3 = await stub.GetNearestNavPoint(
            sdk_to_proto(location), timeout=5.0
        )
        return proto_to_sdk(resp)

    @staticmethod
    @safe_async_rpc(default=0.0)
    async def get_fps(conn: GrpcConnection) -> float:
        stub = conn.get_stub(SceneServiceStub)
        resp: basic_pb2.Float = await stub.GetFPS(basic_pb2.Empty(), timeout=2.0)
        return resp.float

    @staticmethod
    @safe_async_rpc(default="")
    async def find_closest_object_by_type(
        conn: GrpcConnection,
        location: Vector3,
        max_dist: float,
        object_type: str | None = None,
    ) -> str:
        stub = conn.get_stub(SceneServiceStub)
        resp: basic_pb2.Subject = await stub.FindClosestObjectByType(
            FindClosestObjectByTypeRequest(
                location=sdk_to_proto(location),
                max_dist=max_dist,
                object_type=object_type,
            ),
            timeout=2.0,
        )
        return resp.id

    @staticmethod
    @safe_async_rpc(default=[])
    async def get_container_doors(conn: GrpcConnection, component_id: str) -> list[str]:
        stub = conn.get_stub(SceneServiceStub)
        resp: basic_pb2.Components = await stub.GetContainerDoors(
            basic_pb2.Component(id=component_id)
        )
        return list(resp.components)

    @staticmethod
    @safe_async_rpc(default="")
    async def find_closest_door(
        conn: GrpcConnection, location: Vector3, max_dist: float
    ) -> str:
        stub = conn.get_stub(SceneServiceStub)
        resp: basic_pb2.Component = await stub.FindClosestDoor(
            FindClosestDoorRequest(location=sdk_to_proto(location), max_dist=max_dist),
            timeout=2.0,
        )
        return resp.id

    @staticmethod
    @safe_async_rpc(default="")
    async def find_closest_agent(
        conn: GrpcConnection, location: Vector3, max_dist: float
    ) -> str:
        stub = conn.get_stub(SceneServiceStub)
        resp: basic_pb2.Subject = await stub.FindClosestAgent(
            FindClosestAgentRequest(location=sdk_to_proto(location), max_dist=max_dist),
            timeout=2.0,
        )
        return resp.id

    @staticmethod
    @safe_async_rpc(default=None)
    async def get_nav_target(
        conn: GrpcConnection,
        start_location: Vector3,
        target_location: Vector3,
        stop_distance: float,
    ) -> tuple:
        stub = conn.get_stub(SceneServiceStub)
        resp: GetNavMeshResponse = await stub.GetNavTarget(
            GetNavMeshRequest(
                start_location=sdk_to_proto(start_location),
                target_location=sdk_to_proto(target_location),
                stop_distance=stop_distance,
            ),
            timeout=2.0,
        )
        return (
            proto_to_sdk(resp.location),
            resp.b_reach,
            proto_to_sdk(resp.stop_location),
        )

    @staticmethod
    @safe_async_rpc(default=[])
    async def get_object_by_rdf(conn: GrpcConnection, rdf_type: str) -> list[str]:
        stub = conn.get_stub(SceneServiceStub)
        resp: ObjectListResponse = await stub.GetObjectByRdf(
            GetObjectByRdfRequest(rdf_name=rdf_type), timeout=2.0
        )
        return list(resp.object_list)

    @staticmethod
    @safe_async_rpc(default=[])
    # TODO: 该接口实际上返回的是 list[component_id], 但 protobuf 定义是 subject_id
    async def get_all_passable_doors(conn: GrpcConnection) -> list[str]:
        stub = conn.get_stub(SceneServiceStub)
        resp: basic_pb2.Subjects = await stub.GetAllPassableDoors(
            basic_pb2.EmptyResponse(), timeout=2.0
        )  # TODO: fix send response in protobuf
        return [subject.id for subject in resp.subjects]

    @staticmethod
    @safe_async_rpc(default=[])
    # TODO: 该接口实际上返回的是 list[component_id], 但 protobuf 定义是 subject_id
    async def get_all_impassable_doors(conn: GrpcConnection) -> list[str]:
        stub = conn.get_stub(SceneServiceStub)
        resp: basic_pb2.Subjects = await stub.GetAllImpassableDoors(
            basic_pb2.EmptyResponse(), timeout=2.0
        )  # TODO: fix send response in protobuf
        return [subject.id for subject in resp.subjects]

    @staticmethod
    @safe_async_rpc(default="")
    async def spawn_object(
        conn: GrpcConnection,
        blueprint: str,
        location: Vector3,
        rotation: Quaternion | None = None,
        scale: Vector3 | None = None,
        desired_name: str = "",
        is_simulating_physics: bool = True,
        is_vr_grippable=True,
        should_spawn_if_collision: bool = True,
        base_mesh: str = "",
        edible_mesh: str = "",
    ) -> str:
        if rotation is None:
            rotation = Quaternion()
        if scale is None:
            scale = Vector3(1.0, 1.0, 1.0)
        stub = conn.get_stub(SceneServiceStub)
        req: SpawnObjectRequest = SpawnObjectRequest(
            bp_name=blueprint,
            location=sdk_to_proto(location),
            rotation=sdk_to_proto(rotation),
            scale=sdk_to_proto(scale),
            desired_name=desired_name,
            b_sim_physics=is_simulating_physics,
            b_vr_grippalbe=is_vr_grippable,
            b_should_spawn_if_collision=should_spawn_if_collision,
            sm_name=base_mesh,
            esm_name=edible_mesh,
        )
        resp: SpawnObjectResponse = await stub.SpawnObject(req, timeout=20.0)
        return resp.unique_name

    @staticmethod
    @safe_async_rpc(default=("", ""))
    async def get_asset_file_content(conn: GrpcConnection, asset_path: str) -> tuple:
        stub = conn.get_stub(SceneServiceStub)
        resp: FileContent = await stub.GetAssetFileContent(
            basic_pb2.AssetPath(path=asset_path), timeout=20.0
        )
        return resp.last_modified, resp.content

    @staticmethod
    @safe_async_rpc(default=False)
    async def exec_console_command(conn: GrpcConnection, console_command: str) -> bool:
        stub = conn.get_stub(SceneServiceStub)
        req = ExecCommandRequest(command=console_command)
        await stub.ExecCommand(req, timeout=3600.0)
        return True

    @staticmethod
    @safe_async_rpc(default=None)
    async def get_placed_info_from_container(
        conn: GrpcConnection, subject_id: str, component_id: str
    ) -> dict | None:
        stub = conn.get_stub(SceneServiceStub)
        req: ContainerInteractiveParams = ContainerInteractiveParams(
            component=basic_pb2.Component(id=component_id),
            subject=basic_pb2.Subject(id=subject_id),
        )
        resp: ContainerPlacedObjectInfo = await stub.GetPlacedObjectInfoFromContainer(
            req, timeout=2.0
        )
        return {
            "is_valid": resp.b_success,
            "move_location": proto_to_sdk(resp.move_location),
            "place_location": proto_to_sdk(resp.place_location),
            "place_rotation": proto_to_sdk(resp.place_quater),
        }

    @staticmethod
    @safe_async_rpc(default=None)
    async def get_take_out_info_from_container(
        conn: GrpcConnection, subject_id: str, component_id: str
    ) -> dict | None:
        stub = conn.get_stub(SceneServiceStub)
        req: ContainerInteractiveParams = ContainerInteractiveParams(
            component=basic_pb2.Component(id=component_id),
            subject=basic_pb2.Subject(id=subject_id),
        )
        resp: ContainerTakeOutObjectInfo = await stub.GetTakeOutObjectInfoFromContainer(
            req, timeout=2.0
        )
        return {
            "is_valid": resp.b_success,
            "move_location": proto_to_sdk(resp.move_location),
        }

    @staticmethod
    @safe_async_rpc(default=False)
    async def debug_spawn_all_rdf_objects(
        conn: GrpcConnection, rdf_type: Sequence[str], place_distance: float = 100.0
    ) -> bool:
        stub = conn.get_stub(SceneServiceStub)
        req: DebugSpawnAllRdfObjectsRequest = DebugSpawnAllRdfObjectsRequest(
            rdf=rdf_type,
            distance=place_distance,
        )
        await stub.DebugSpawnAllRdfObjects(req)
        return True

    # === bigai.ue.subsystem.segment ===
    @staticmethod
    @safe_async_rpc(default=False)
    async def set_segment_id(
        conn: GrpcConnection, segment_id_map: dict[str, int]
    ) -> bool:
        stub = conn.get_stub(SegmentServiceStub)
        req = SetSegmentIdRequest(id_map=segment_id_map)
        await stub.SetSegmentId(req, timeout=2.0)
        return True

    # === bigai.ue.subsystem.pg ===
    @staticmethod
    @safe_async_rpc(default=False)
    async def set_pg_frequency(conn: GrpcConnection, freq: int) -> bool:
        stub = conn.get_stub(PGServiceStub)
        req = PGFrequency(frequency=freq)
        await stub.SetPGFrequency(req, timeout=2.0)
        return True

    @staticmethod
    @safe_async_rpc(default={})
    async def get_subject_pg(conn: GrpcConnection, subject_id: str) -> SubjectPG:
        stub = conn.get_stub(PGServiceStub)
        req = basic_pb2.Subject(id=subject_id)
        return await stub.GetObjectPG(req, timeout=2.0)

    @staticmethod
    @safe_async_rpc(default={})
    async def get_component_pg(conn: GrpcConnection, component_id: str) -> ComponentPG:
        stub = conn.get_stub(PGServiceStub)
        req = basic_pb2.Component(id=component_id)
        return await stub.GetComponentPG(req, timeout=2.0)

    # === bigai.ue.subsystem.record ===
    @staticmethod
    @safe_async_rpc(default=False)
    async def start_capture(
        conn: GrpcConnection, file_name: str, directory_path: str, frame_rate: int
    ) -> bool:
        stub = conn.get_stub(RecordServiceStub)
        req = StartRecord(
            file_name=file_name,
            directory_path=directory_path,
            frame_rate=frame_rate,
        )
        await stub.StartCapture(req, timeout=2.0)
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def pause_capture(conn: GrpcConnection) -> bool:
        stub = conn.get_stub(RecordServiceStub)
        req = basic_pb2.EmptyResponse()
        await stub.PauseCapture(req, timeout=2.0)
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def resume_capture(conn: GrpcConnection) -> bool:
        stub = conn.get_stub(RecordServiceStub)
        req = basic_pb2.EmptyResponse()
        await stub.ResumeCapture(req, timeout=2.0)
        return True

    @staticmethod
    @safe_async_rpc(default={})
    async def finish_capture(conn: GrpcConnection) -> dict:
        stub = conn.get_stub(RecordServiceStub)
        req = basic_pb2.EmptyResponse()
        resp: FinishResponse = await stub.FinishCapture(req, timeout=5.0)
        return {
            "success": resp.b_successed,
            "path": resp.out_path,
            "name": resp.video_name,
        }

    # === bigai.ue.subsystem.open_world ===
    @staticmethod
    @safe_async_rpc(default=False)
    async def npc_moveto_location(
        conn: GrpcConnection, npc_id: str, location: Vector3
    ) -> bool:
        stub = conn.get_stub(OpenWorldServiceStub)
        await stub.NPCMovetoLocation(
            NPCMovetoLocationRequest(
                npc_id=npc_id,
                location=sdk_to_proto(location),
            ),
        )
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def npc_play_animation(
        conn: GrpcConnection, npc_id: str, anim_name: str
    ) -> bool:
        stub = conn.get_stub(OpenWorldServiceStub)
        await stub.NPCPlayAnimation(
            NPCPlayAnimationRequst(
                npc_id=npc_id,
                anim_name=anim_name,
            ),
        )
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def npc_turnaround(
        conn: GrpcConnection,
        npc_id: str,
        object_id: str | None = None,
        location: Vector3 | None = None,
        degree: float | None = None,
    ) -> bool:
        stub = conn.get_stub(OpenWorldServiceStub)
        await stub.NPCTurnAround(
            NPCTurnAroundRequst(
                npc_id=npc_id,
                object_id=object_id,
                location=sdk_to_proto(location),
                degree=degree,
            ),
        )
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def npc_pickup(conn: GrpcConnection, npc_id: str, object_id: str) -> bool:
        stub = conn.get_stub(OpenWorldServiceStub)
        await stub.NPCPickUp(
            NPCPickUpRequst(
                npc_id=npc_id,
                object_id=object_id,
            ),
        )
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def npc_putdown(
        conn: GrpcConnection,
        npc_id: str,
        object_id: str,
        location: Vector3,
        rotation: Quaternion,
    ) -> bool:
        stub = conn.get_stub(OpenWorldServiceStub)
        await stub.NPCPutDown(
            NPCPutDownRequst(
                npc_id=npc_id,
                object_id=object_id,
                location=sdk_to_proto(location),
                rotation=sdk_to_proto(rotation),
            ),
        )
        return True

    # === bigai.ue.subsystem.debugdraw ===
    @staticmethod
    @safe_async_rpc(default=False)
    async def debug_draw_coordinates(
        conn: GrpcConnection,
        world_transform: Transform,
        coordinates_local_transforms: Sequence[Transform],
        time_length: float,
        line_width: float = 1.0,
        axis_length: float = 5.0,
    ) -> bool:
        stub = conn.get_stub(DebugDrawServiceStub)
        req = DebugDrawRequest(
            world_transform=sdk_to_proto(world_transform),
            time_length=time_length,
            line_width=line_width,
            coordinates=Coordinates(
                coordinates=[
                    sdk_to_proto(trans) for trans in coordinates_local_transforms
                ],
                axis_length=axis_length,
            ),
        )
        await stub.DebugDrawElements(req, timeout=2.0)
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def debug_draw_lines(
        conn: GrpcConnection,
        world_transform: Transform,
        line_local_locations: Sequence[tuple[Vector3, Vector3]],
        time_length: float,
        line_width: float = 1.0,
    ) -> bool:
        stub = conn.get_stub(DebugDrawServiceStub)
        req = DebugDrawRequest(
            world_transform=sdk_to_proto(world_transform),
            time_length=time_length,
            line_width=line_width,
            lines=Lines(
                lines=[
                    Line(point1=sdk_to_proto(p1), point2=sdk_to_proto(p2))
                    for p1, p2 in line_local_locations
                ]
            ),
        )
        await stub.DebugDrawElements(req, timeout=2.0)
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def debug_draw_boxes(
        conn: GrpcConnection,
        world_transform: Transform,
        local_boxes: Sequence[tuple[Transform, Vector3, Vector3]],
        time_length: float,
        line_width: float = 1.0,
    ) -> bool:
        stub = conn.get_stub(DebugDrawServiceStub)
        req = DebugDrawRequest(
            world_transform=sdk_to_proto(world_transform),
            time_length=time_length,
            line_width=line_width,
            boxes=Boxes(
                boxes=[
                    Box(
                        box_transform=sdk_to_proto(transform),
                        box_center=sdk_to_proto(center),
                        box_extent=sdk_to_proto(extent),
                    )
                    for transform, center, extent in local_boxes
                ]
            ),
        )
        await stub.DebugDrawElements(req, timeout=2.0)
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def set_light_color(
        conn: GrpcConnection,
        component_id: str,
        color: Vector3,
    ) -> bool:
        stub = conn.get_stub(ObjectStateServiceStub)
        req = SetLightColorRequest(
            component=basic_pb2.Component(id=component_id),
            color=basic_pb2.Vector3(
                x=color.x,
                y=color.y,
                z=color.z,
            ),
        )
        await stub.SetLightColor(req, timeout=2.0)
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def step(
        conn: GrpcConnection, step_time: float, time_flow_rate: float
    ) -> bool:
        stub = conn.get_stub(SceneServiceStub)
        req = StepRequest(step_time=step_time, time_flow_rate=time_flow_rate)
        await stub.Step(req, timeout=5.0)
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def set_move_ability(
        conn: GrpcConnection,
        attribute_component_id: str,
        walk_speed: float,
        run_speed: float,
        jump_z_velocity: float,
        crouch_speed: float,
        move_friction: float = 0.5,
    ) -> bool:
        stub = conn.get_stub(CharacterAttributeServiceStub)
        req = MoveAttribute(
            component=basic_pb2.Component(id=attribute_component_id),
            walk_speed=walk_speed,
            run_speed=run_speed,
            jump_velocity=jump_z_velocity,
            crouch_speed=crouch_speed,
            move_friction=move_friction,
        )
        await stub.SetMoveAbility(req, timeout=2.0)
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def load_game(conn: GrpcConnection, save_context: str) -> bool:
        stub = conn.get_stub(SaveGameServiceStub)
        return await stub.LoadGame(save_context, timeout=5.0)

    @staticmethod
    @safe_async_rpc(default="")
    async def save_game(conn: GrpcConnection) -> str:
        stub = conn.get_stub(SaveGameServiceStub)
        return await stub.SaveGame(basic_pb2.EmptyResponse(), timeout=5.0)

    @staticmethod
    @safe_async_rpc(default=False)
    async def set_enable_physics_body(
        conn: GrpcConnection, component_id: str, is_enable: bool
    ) -> bool:
        stub = conn.get_stub(CharacterAttributeServiceStub)
        req = basic_pb2.BoolRequest(
            component=basic_pb2.Component(id=component_id), bool=is_enable
        )
        await stub.SetIsEnablePhysicsBody(req, timeout=2.0)
        return True

    @staticmethod
    @safe_async_rpc(default=False)
    async def print_text_to_screen(
        conn: GrpcConnection,
        print_str: str,
        color: Vector3,
        duration: float = 5.0,
    ) -> bool:
        stub = conn.get_stub(SceneServiceStub)
        req = RequestDebugPrint(
            debug_str=print_str,
            color=sdk_to_proto(color),
            duration=duration,
        )
        await stub.DebugPrint(req, timeout=2.0)
        return True

    @staticmethod
    @safe_async_rpc(default=[])
    async def get_asset_list(conn: GrpcConnection) -> list[str]:
        stub = conn.get_stub(SceneServiceStub)
        req = basic_pb2.EmptyRequest()
        response: basic_pb2.StringArray = await stub.GetAssetList(req, timeout=5.0)
        return [s.str for s in response.string]

    @staticmethod
    @safe_async_rpc(default=False)
    async def set_game_pause(conn: GrpcConnection, is_pause: bool) -> bool:
        stub = conn.get_stub(SceneServiceStub)
        req = basic_pb2.Bool(bool=is_pause)
        await stub.SetGamePause(req, timeout=2.0)
        return True

    @staticmethod
    @safe_async_rpc(default=Vector3())
    async def get_nav_point_ringlike(
        conn: GrpcConnection,
        center: Vector3,
        min_radius: float,
        max_radius: float,
        room: str,
    ) -> Vector3:
        stub = conn.get_stub(MapServiceStub)
        req = NavPointInRinglikeParams(
            center=sdk_to_proto(center),
            inner_radius=min_radius,
            outer_radius=max_radius,
            room_name=room,
        )
        response: basic_pb2.Vector3 = await stub.GetNavPointInRinglike(req, timeout=5.0)
        return proto_to_sdk(response)

    @staticmethod
    @safe_async_rpc(default=[])
    async def sphere_trace(
        conn: GrpcConnection,
        start: Vector3,
        end: Vector3,
        radius: float,
        ignore_subject_id: list[str],
        is_multi: bool = False,
    ) -> list[str]:
        stub = conn.get_stub(SceneServiceStub)
        req = TraceRequest(
            start=sdk_to_proto(start),
            end=sdk_to_proto(end),
            trace_collision_channel=TraceCollisionChannel.ECC_VISIBILITY,
            is_multi=is_multi,
            sphere_trace_params=SphereTraceParams(radius=radius),
            ignore_subjects=basic_pb2.Subjects(
                subjects=[
                    basic_pb2.Subject(id=ignore_subject_id)
                    for ignore_subject_id in ignore_subject_id
                ]
            ),
        )
        resp: TraceSubjects = await stub.Trace(req, timeout=2.0)
        return [trace_subject.subject_id for trace_subject in resp.trace_subjects]

    @staticmethod
    @safe_async_rpc(default=[])
    async def box_trace(
        conn: GrpcConnection,
        start: Vector3,
        end: Vector3,
        box_half_size: Vector3,
        rotation: Quaternion,
        ignore_subject_id: list[str],
        is_multi: bool = False,
    ) -> list[str]:
        stub = conn.get_stub(SceneServiceStub)
        req = TraceRequest(
            start=sdk_to_proto(start),
            end=sdk_to_proto(end),
            trace_collision_channel=TraceCollisionChannel.ECC_VISIBILITY,
            is_multi=is_multi,
            box_trace_params=BoxTraceParams(
                box_half_size=sdk_to_proto(box_half_size),
                rotation=sdk_to_proto(rotation),
            ),
            ignore_subjects=basic_pb2.Subjects(
                subjects=[
                    basic_pb2.Subject(id=ignore_subject_id)
                    for ignore_subject_id in ignore_subject_id
                ]
            ),
        )
        resp: TraceSubjects = await stub.Trace(req, timeout=2.0)
        return [trace_subject.subject_id for trace_subject in resp.trace_subjects]

    @staticmethod
    @safe_async_rpc(default=[])
    async def get_room_array(
        conn: GrpcConnection,
    ) -> list[str]:
        stub = conn.get_stub(MapServiceStub)
        req = basic_pb2.Empty()
        response: basic_pb2.StringArray = await stub.GetRoomArray(req, timeout=2.0)
        return [s.str for s in response.string]

    @staticmethod
    @safe_async_rpc(default=Vector3())
    async def get_random_spawn_location(
        conn: GrpcConnection,
        room: str,
    ) -> Vector3:
        stub = conn.get_stub(MapServiceStub)
        req = basic_pb2.String(string=room)
        response: basic_pb2.Vector3 = await stub.GetRandomSpawnLocation(
            req, timeout=5.0
        )
        return proto_to_sdk(response)

    @staticmethod
    @safe_async_rpc(default="")
    async def get_room_name_from_location(
        conn: GrpcConnection,
        location: Vector3,
    ) -> str:
        stub = conn.get_stub(MapServiceStub)
        req = sdk_to_proto(location)
        response: basic_pb2.String = await stub.GetRoomNameFromLocation(
            req, timeout=2.0
        )
        return response.string

    @staticmethod
    @safe_async_rpc(default=False)
    async def set_ui_text(
        conn: GrpcConnection,
        component_id: str,
        text: str,
    ) -> bool:
        stub = conn.get_stub(ObjectStateServiceStub)
        req = SetObjectUITextRequest(
            component=basic_pb2.Component(id=component_id), text=text
        )
        await stub.SetObjectUIText(req, timeout=2.0)
        return True
