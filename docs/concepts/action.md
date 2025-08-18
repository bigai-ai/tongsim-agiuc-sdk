# 🧠 Agent 动作系统（Action System）

TongSim SDK 提供了统一的「Agent 动作系统」，用于控制智能体执行具有语义的行为。你可以通过高层能力接口 `AgentActionAbility`，快速调度已有或自定义的 Action，并获得结构化的执行结果。

---

## 🌟 核心能力：AgentActionAbility

所有支持动画控制的实体（Agent）均具备 `AgentActionAbility` 接口，其提供统一的方法来：

- **提交**一个动作到 Agent 的执行队列；
- **同步或异步执行**动作并收集结果；
- **查询当前状态**或动作执行情况；
- **控制智能体的动画行为**（如启用闲置随机动画、查询可播放动画等）；

[API 参考](../api/ability_action.md)

---

## 🏗️ 核心结构说明

### ✅ Action 封装机制

- 每个 `Action` 类继承自 `ActionBase`，内部通过多个 Animation 指令完成具体行为(也可以支持其他 gRPC 调用)；
- 系统提供丰富的内置 Action，如 `WaveHand`, `ShakeHead`, `EatOrDrink` 等等；
- 用户也可以继承 `ActionBase` 来实现自定义动作组合。

[ActionBase API 参考](../api/action_base.md)
[ActionImpl API 参考](../api/action_impl.md)

---

## 🎯 动作结果说明：AnimResultInfo

每个 Action 会拆解为若干 Animation，每个 Animation 的执行将返回一个 `AnimResultInfo`，字段如下：

```python
@dataclass
class AnimResultInfo:
    command_id: int                 # 唯一 ID
    unreal_frame: int               # UE 触发该事件的帧号
    error_code: int                 # 错误码（若失败）
    error_animation_code: int      # 错误的动画标识
    status: Literal["begin", "end", "error"]  # 当前阶段
```

---

## 🦾 动作队列与执行机制

在 TongSim 中，每个 Agent（智能体）维护一套**独立的动作队列系统**，用于组织多个动作（Action）的执行过程。整个机制通过以下几个核心设计实现：

### 每个智能体持有独立的 Action 队列

- 每个 Agent 内部维护一个队列（FIFO），用于存放等待执行的 Action, 连续提交多个动作，系统会自动排队执行，无需用户显式等待上一个完成。
- 所有动作按提交顺序逐一执行，**严格顺序，互不抢占**。

### 提交动作的方式

动作提交提供两种方式，分别对应**是否立即开始执行**：

| 方法名                  | 描述                       |
|-------------------------|----------------------------|
| `enqueue_action()`      | 仅将动作加入队列，不立即执行（同步） |
| `async_enqueue_action()`| 异步版本，支持异步上下文        |
| `do_action()`           | 加入队列并**立即触发执行**（同步） |
| `async_do_action()`     | 异步版本，推荐在协程中使用       |

示例：

```python
agent.enqueue_action(ts.WaveHand())     # 加入队列
agent.do_action()                       # 执行当前队列中的所有动作
```

你也可以将动作组合使用：

```python
agent.enqueue_action(ts.WaveHand())
agent.enqueue_action(ts.ShakeHeadWithDuration(2.0))
agent.do_action()  # 顺序依次执行 Wave -> ShakeHead
```

### 动作执行过程：gRPC 双向流

当 `do_action()` 被调用后，TongSim SDK 会完成以下流程：

1. 将指定 Action 拆解为多个 Animation 命令；
2. 通过底层 gRPC 双向流（`AnimationStreamer`）将每个命令发送至服务器；
3. 每个 Animation 会收到两类响应事件：
   - **BEGIN**：表示已成功在服务器端启动执行；
   - **END**：表示该 Animation 已结束；
   - **ERROR**（可选）：若执行中出错，将收到错误报告。

所有响应事件都将被封装为 `AnimResultInfo` 并返回，用户可根据 `status` 字段判定每步执行状态。

---

### 状态查询方法

以下方法可用于查询当前 Agent 的动作状态：

| 方法名                      | 说明                       |
|-----------------------------|----------------------------|
| `is_action_queue_empty()`   | 判断当前队列是否为空        |
| `get_agent_action_status()` | 返回当前 Agent 的执行状态摘要 |
| `get_taking_entity_id()`    | 获取角色手上拿着的实体 ID（左/右手） |
