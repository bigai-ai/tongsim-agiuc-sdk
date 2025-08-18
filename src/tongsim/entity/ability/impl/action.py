"""
tongsim.entity.ability.impl.action

定义 AgentActionAbility 接口及其具体实现 AgentActionAbilityImpl。

- `AgentActionAbility`: 角色动画执行的接口，提供同步与异步执行方法。
- `AgentActionAbilityImpl`: 接口实现类，基于 AnimationStreamer 提供 Action 的执行与结果收集功能。
"""

import asyncio
from typing import Protocol

from google.protobuf.json_format import MessageToDict

from tongsim.connection.grpc import AnimationStreamer, LegacyAPI, UnaryAPI
from tongsim.connection.tags import ComponentTags
from tongsim.entity.ability.base import AbilityImplBase
from tongsim.entity.ability.registry import AbilityRegistry
from tongsim.entity.action.base import ActionBase
from tongsim.entity.entity import Entity
from tongsim.logger import get_logger
from tongsim.type.anim import AnimCmdHandType, AnimResultInfo

_logger = get_logger("animation")

__all__ = ["AgentActionAbility"]


class AgentActionAbility(Protocol):
    """
    AgentActionAbility 定义了角色动画执行的相关接口。

    该接口用于管理 Action 执行及结果收集，包括同步与异步执行方法。
    每个 Action 由若干 Animation 组成，`do_action()` 和 `async_do_action()` 方法将统一负责执行并收集结果。
    """

    async def async_enqueue_action(
        self, action: ActionBase, track_result: bool = False
    ) -> ActionBase:
        """
        异步将 Action 加入执行队列，不阻塞当前流程。

        Args:
            action (ActionBase): 要加入队列的 Action 对象。
            track_result (bool): 是否跟踪 Action 的执行结果，默认为 False。

        Returns:
            ActionBase: 已加入队列的 Action 对象。
        """

    def enqueue_action(
        self, action: ActionBase, track_result: bool = False
    ) -> ActionBase:
        """
        同步将 Action 加入队列。

        Args:
            action (ActionBase): 要加入队列的 Action 对象。
            track_result (bool): 是否跟踪 Action 的执行结果，默认为 False。

        Returns:
            ActionBase: 已加入队列的 Action 对象。
        """

    async def async_do_action(
        self, action: ActionBase | None = None, cancel_on_error: bool = False
    ) -> list[AnimResultInfo] | None:
        """
        异步执行指定的 Action 对象，并收集 Animation 结果。

        如果 `action` 为 None，则执行当前队列中的所有 Action。

        Args:
            action (ActionBase | None): 要执行的 Action 对象。如果为 None，则执行队列中的所有 Action。
            cancel_on_error (bool): 遇到异常时是否取消剩余 Animation，默认为 False。

        Returns:
            list[AnimResultInfo] | None: 每个 Animation 的执行结果，或 None（若 action 为 None）。

        """

    def do_action(
        self, action: ActionBase | None = None, cancel_on_error: bool = False
    ) -> list[AnimResultInfo] | None:
        """
        同步执行指定的 Action 对象，并收集 Animation 结果。

        如果 `action` 为 None，则执行当前队列中的所有 Action。

        Args:
            action (ActionBase | None): 要执行的 Action 对象。如果为 None，则执行队列中的所有 Action。
            cancel_on_error (bool): 遇到异常时是否取消剩余 Animation，默认为 False。

        Returns:
            list[AnimResultInfo] | None: 每个 Animation 的执行结果，或 None（若 action 为 None）。

        """

    async def async_get_playable_animation_names(self) -> list[str]:
        """
        异步获取当前智能体可播放的动画名称列表。

        Returns:
            list[str]: 可用动画名称的字符串列表。
        """

    def get_playable_animation_names(self) -> list[str]:
        """
        获取当前智能体可播放的动画名称列表（同步接口）。

        Returns:
            list[str]: 可用动画名称的字符串列表。
        """

    def enable_idle_random_anim(self, is_enable: bool) -> bool:
        """
        启用或禁用智能体的闲置状态随机动画（同步接口）。

        当启用后，智能体在没有执行其他动作时，将自动播放预定义的随机闲置动画。

        Args:
            is_enable (bool): 是否启用随机闲置动画。True 表示启用，False 表示禁用。

        Returns:
            bool: 操作是否成功。True 表示设置成功，False 表示失败。
        """

    async def async_enable_idle_random_anim(self, is_enable: bool) -> bool:
        """
        启用或禁用智能体的闲置状态随机动画（异步接口）。

        当启用后，智能体在没有执行其他动作时，将自动播放预定义的随机闲置动画。

        Args:
            is_enable (bool): 是否启用随机闲置动画。True 表示启用，False 表示禁用。

        Returns:
            bool: 操作是否成功。True 表示设置成功，False 表示失败。
        """

    def is_action_queue_empty(self) -> bool:
        """
        判断当前智能体的动作队列是否为空（同步接口）。

        如果队列为空，表示当前没有待执行的动作。

        Returns:
            bool: 若队列为空返回 True，否则返回 False。
        """

    async def async_is_action_queue_empty(self) -> bool:
        """
        判断当前智能体的动作队列是否为空（异步接口）。

        如果队列为空，表示当前没有待执行的动作。

        Returns:
            bool: 若队列为空返回 True，否则返回 False。
        """

    def get_agent_action_status(self) -> dict:
        """
        获取当前智能体的动作状态信息（同步接口）。

        Returns:
            dict: 动作状态信息字典
        """

    async def async_get_agent_action_status(self) -> dict:
        """
        获取当前智能体的动作状态信息（异步接口）。

        Returns:
            dict: 动作状态信息字典
        """

    def get_taking_entity_id(self, which_hand: AnimCmdHandType) -> str | None:
        """
        获取指定手上当前拿着的对象 ID（同步接口）。

        Args:
            which_hand (AnimCmdHandType): 哪只手

        Returns:
            str | None: 被拿取对象的实体 ID，若未拿取任何对象则返回 None。
        """

    async def async_get_taking_entity_id(
        self, which_hand: AnimCmdHandType
    ) -> str | None:
        """
        获取指定手上当前拿着的对象 ID（异步接口）。

        Args:
            which_hand (AnimCmdHandType): 哪只手
        Returns:
            str | None: 被拿取对象的实体 ID，若未拿取任何对象则返回 None。
        """

    def set_emotion(self, emotion: dict) -> None:
        """
        设置智能体的情绪状态（同步接口）。

        Args:
            emotion (dict): 情绪状态的字典表示。支持的情绪类型["happy", "angry", "horror", "sad","disgust","surprise","worry"],范围在[0,1]之间
        """

    async def async_set_emotion(self, emotion: dict) -> None:
        """
        设置智能体的情绪状态（异步接口）。

        Args:
            emotion (dict): 情绪状态的字典表示。支持的情绪类型["happy", "angry", "horror", "sad","disgust","surprise","worry"]，范围在[0,1]之间
        """

    def set_enable_physics_body(self, is_enable: bool) -> bool:
        """
        设定是否开启人物的物理碰撞（同步接口）。

        Args:
            is_enable (bool): 是否开启。

        Returns:
            是否成功设置。
        """

    async def async_set_enable_physics_body(self, is_enable: bool) -> bool:
        """
        设定是否开启人物的物理碰撞（异步接口）。

        Args:
            is_enable (bool): 是否开启。

        Returns:
            是否成功设置。
        """

    def set_move_ability(
        self,
        walk_speed: float,
        run_speed: float,
        jump_z_velocity: float,
        crouch_speed: float,
        move_friction: float = 0.5,
    ) -> bool:
        """
        设置运动参数（同步接口）只适用于InputAnimation动作的状态。

        Args:
             walk_speed (float): 行走速度
             run_speed (float): 奔跑速度
             jump_z_velocity (float): 跳跃z轴初速度
             crouch_speed (float): 蹲伏移动速度
             move_friction (float): 撞到障碍物后的摩擦系数
        """

    async def async_set_move_ability(
        self,
        walk_speed: float,
        run_speed: float,
        jump_z_velocity: float,
        crouch_speed: float,
        move_friction: float = 0.5,
    ) -> bool:
        """
        设置运动参数（异步接口）只适用于InputAnimation动作的状态。

        Args:
             walk_speed (float): 行走速度
             run_speed (float): 奔跑速度
             jump_z_velocity (float): 跳跃z轴初速度
             crouch_speed (float): 蹲伏移动速度
             move_friction (float): 撞到障碍物后的摩擦系数
        """


@AbilityRegistry.register(AgentActionAbility)
class AgentActionAbilityImpl(AbilityImplBase):
    def __init__(self, entity: Entity, streamer: AnimationStreamer):
        super().__init__(entity)
        self._anim_component_id: str = entity.get_component_id(ComponentTags.ANIM)
        self._attachment_component_id: str = entity.get_component_id(
            ComponentTags.CHAR_ATTACHMENT
        )
        self._face_component_id: str = entity.get_component_id(ComponentTags.EMOTION)
        self._attribute_component_id: str = entity.get_component_id(
            ComponentTags.CHAR_ATTRIBUTE
        )
        self._anim_streamer: AnimationStreamer = streamer
        # 注册资源析构回调，提交到事件循环中执行
        # weakref.finalize(self, self._schedule_streamer_close)

    @classmethod
    async def create(cls, entity: Entity) -> "AgentActionAbilityImpl":
        anim_component_id = entity.get_component_id(ComponentTags.ANIM)
        streamer = AnimationStreamer(
            entity.context.conn,
            entity.context.loop,
            entity.id,
            anim_component_id,
        )
        await streamer.start()
        return cls(entity, streamer)

    @classmethod
    def is_applicable(cls, entity: Entity) -> bool:
        return entity.has_component_type(
            ComponentTags.ANIM
        ) and entity.has_component_type(ComponentTags.CHAR_ATTACHMENT)

    async def async_enqueue_action(
        self, action: ActionBase, track_result: bool = False
    ) -> ActionBase:
        action.initialize(self, self._anim_streamer, self._context, track_result)
        await action.run()
        return action

    def enqueue_action(
        self, action: ActionBase, track_result: bool = False
    ) -> ActionBase:
        return self._context.sync_run(self.async_enqueue_action(action, track_result))

    async def async_do_action(
        self, action: ActionBase | None = None, cancel_on_error: bool = False
    ) -> list[AnimResultInfo] | None:
        if action:
            await self.async_enqueue_action(action, track_result=True)

        # 执行动作逻辑
        await UnaryAPI.do_task(
            self._context.conn, self._entity_id, self._anim_component_id
        )

        if action:
            return await action.collect_results(cancel_on_error)
        return None

    def do_action(
        self, action: ActionBase | None = None, cancel_on_error: bool = False
    ) -> list[AnimResultInfo] | None:
        return self._context.sync_run(self.async_do_action(action, cancel_on_error))

    async def async_get_playable_animation_names(self) -> list[str]:
        return await LegacyAPI.get_playable_animation_names(
            self._context.conn_legacy, self._entity_id
        )

    def get_playable_animation_names(self) -> list[str]:
        return self._context.sync_run(self.async_get_playable_animation_names())

    def enable_idle_random_anim(self, is_enable: bool) -> bool:
        return self._context.sync_run(self.async_enable_idle_random_anim(is_enable))

    async def async_enable_idle_random_anim(self, is_enable: bool) -> bool:
        return await LegacyAPI.enable_idle_anim(
            self._context.conn_legacy, self._entity_id, is_enable
        )

    def is_action_queue_empty(self) -> bool:
        return self._context.sync_run(self.async_is_action_queue_empty())

    async def async_is_action_queue_empty(self) -> bool:
        return await LegacyAPI.is_anim_queue_empty(
            self._context.conn_legacy, self._entity_id
        )

    def get_agent_action_status(self) -> dict:
        return self._context.sync_run(self.async_get_agent_action_status())

    async def async_get_agent_action_status(self) -> dict:
        resp = await UnaryAPI.get_component_pg(
            self._context.conn, self._anim_component_id
        )
        pg_dict: dict = MessageToDict(
            resp,
            preserving_proto_field_name=True,
            always_print_fields_with_no_presence=True,
        )
        return pg_dict.get(
            "animation",
        )

    def get_taking_entity_id(self, which_hand: AnimCmdHandType) -> str | None:
        return self._context.sync_run(
            self.async_get_taking_entity_id(which_hand=which_hand)
        )

    async def async_get_taking_entity_id(
        self, which_hand: AnimCmdHandType
    ) -> str | None:
        entity_id = await UnaryAPI.get_entity_id_in_hand(
            self._context.conn, self._attachment_component_id, which_hand=which_hand
        )
        if entity_id == "":
            return None
        return entity_id

    def set_emotion(self, emotion: dict) -> None:
        self._context.sync_run(self.async_set_emotion(emotion=emotion))

    async def async_set_emotion(self, emotion: dict) -> None:
        await UnaryAPI.set_emotion(
            self._context.conn, self._face_component_id, emotions=emotion
        )

    def set_move_ability(
        self,
        walk_speed: float,
        run_speed: float,
        jump_z_velocity: float,
        crouch_speed: float,
        move_friction: float = 0.5,
    ) -> bool:
        return self._context.sync_run(
            self.async_set_move_ability(
                walk_speed, run_speed, jump_z_velocity, crouch_speed, move_friction
            )
        )

    async def async_set_move_ability(
        self,
        walk_speed: float,
        run_speed: float,
        jump_z_velocity: float,
        crouch_speed: float,
        move_friction: float = 0.5,
    ) -> bool:
        return await UnaryAPI.set_move_ability(
            self._context.conn,
            self._attribute_component_id,
            walk_speed,
            run_speed,
            jump_z_velocity,
            crouch_speed,
            move_friction,
        )

    def set_enable_physics_body(self, is_enable: bool) -> bool:
        return self._context.sync_run(self.async_set_enable_physics_body(is_enable))

    async def async_set_enable_physics_body(self, is_enable: bool) -> bool:
        return await UnaryAPI.set_enable_physics_body(
            self._context.conn, self._attribute_component_id, is_enable
        )

    def __del__(self):
        loop = self._context.loop.loop
        if loop.is_running():
            loop.call_soon_threadsafe(asyncio.create_task, self._anim_streamer.stop())
