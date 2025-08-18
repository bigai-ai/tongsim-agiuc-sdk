from dataclasses import dataclass

from tongsim.connection.grpc import AnimCmd
from tongsim.entity.action.base import ActionBase


@dataclass(slots=True)
class Interact(ActionBase):
    """
    动作: 交互对象状态。

    用于控制对象状态（如开/关），可应用于灯、按钮、机器开关等。

    Attributes:
        object_id (str): 目标对象的唯一 ID。
        new_object_state (bool): 希望设置的状态，True 表示开启/激活，False 表示关闭/停用。
    """

    object_id: str
    new_object_state: bool

    def validate(self) -> None:
        if not isinstance(self.object_id, str):
            raise TypeError(f"object_id must be str, got {type(self.object_id)}")
        if not isinstance(self.new_object_state, bool):
            raise TypeError(
                f"new_object_state must be bool, got {type(self.new_object_state)}"
            )

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.touch_object_state(
                target_id=self.object_id, new_state=self.new_object_state
            )
        )


@dataclass(slots=True)
class SwitchChannel(ActionBase):
    """
    动作: 切换对象频道（如电视等多频道设备）。

    Attributes:
        object_id (str): 目标对象的唯一 ID。
        new_object_channel (str): 目标对象要切换到的新频道标识，通常为频道名称或编号字符串。
    """

    object_id: str
    new_object_channel: str

    def validate(self) -> None:
        if not isinstance(self.object_id, str):
            raise TypeError(f"object_id must be str, got {type(self.object_id)}")
        if not isinstance(self.new_object_channel, str):
            raise TypeError(
                f"new_object_channel must be str, got {type(self.new_object_state)}"
            )

    async def execute(self) -> None:
        await self.submit(
            AnimCmd.set_object_channel(
                target_id=self.object_id, new_channel=self.new_object_channel
            )
        )
