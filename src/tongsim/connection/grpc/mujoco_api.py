from tongsim_api_protocol.subsystem.mujoco_manager_pb2 import (
    SpawnObjectRequest,
    SpawnObjectResponse,
)
from tongsim_api_protocol.subsystem.mujoco_manager_pb2_grpc import (
    MujocoManagerServiceStub,
)

from tongsim.math import Vector3

from .core import GrpcConnection
from .utils import safe_async_rpc, sdk_to_proto

_SERVE_INIT = 0
_SERVE_SUCCESS = 1

__all__ = ["MujocoAPI"]


class MujocoAPI:
    """
    Mujoco联通UE的所有方法。
    TODO: 全部迁移到到基于 tongsim_api_protocol 的通信中。
    """

    # === tongos.service.ServiceInterface ===
    @staticmethod
    @safe_async_rpc(default=False)
    async def spawn_object(
        conn: GrpcConnection,
        desired_name: str,
        loc: Vector3,
    ) -> str:
        stub = conn.get_stub(MujocoManagerServiceStub)
        resp: SpawnObjectResponse = await stub.SpawnObject(
            SpawnObjectRequest(desired_name=desired_name, location=sdk_to_proto(loc)),
            timeout=5.0,
        )

        return resp.Object_name
