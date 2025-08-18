"""
connection.grpc.type.acoustics
"""

from dataclasses import dataclass, field

from tongsim_api_protocol.subsystem.acoustics_manager_pb2 import AudioDataChunk

__all__ = ["AudioDataWrapper"]


@dataclass(slots=True)
class AudioDataWrapper:
    """
    高性能 wrapper: 仅引用 proto，不复制字段。
    提供 memoryview 支持，避免音频字段拷贝。
    """

    _audio_data_grpc_message: AudioDataChunk = field(repr=False)

    def __post_init__(self):
        if not isinstance(self._audio_data_grpc_message, AudioDataChunk):
            raise TypeError("Expected AudioDataChunk proto")

    @property
    def stream_id(self) -> str:
        return self._audio_data_grpc_message.stream_id

    @property
    def audio_data(self) -> memoryview:
        return memoryview(self._audio_data_grpc_message.audio_data or b"")
