# 📘 TongSim Parsing Graph (PG) 文档

## ✨ 简介

TongSim 的 Parsing Graph（PG）是环境中所有对象状态的结构化表示。默认的 PG 数据通过 gRPC 协议流式推送，采用 **增量更新机制** —— 仅当字段值发生变化时才写出数据，以提升性能与效率。

PG 结构由多个 `Subject`（实体）组成，每个主体包含多个 `Component`（组件），每个 component 负责 subject 对应模块的功能、状态或属性。

---

## 🔍 PG 格式详解

TongSim 的 Parsing Graph（PG）以帧为单位推送，是一个嵌套的结构数据，描述了场景中所有对象及其组件的状态信息。结构由 `PGResponse` 顶层消息开始，包含多个 `SubjectPG`，每个主体又包含多个 `ComponentPG`。

---

### 🧍 每个对象描述：`SubjectPG`

```protobuf
message SubjectPG {
  Subject subject = 1;
  repeated ComponentPG component_pg = 2;
  bool subject_destroyed = 3;
}
```

| 字段名              | 类型                   | 说明                                   |
|---------------------|------------------------|----------------------------------------|
| `subject`           | `Subject`              | 对象的唯一标识，包含 name / id 等信息 |
| `component_pg`      | `repeated ComponentPG` | 对象上挂载的所有组件的状态数据         |
| `subject_destroyed` | `bool`                 | 对象是否已销毁                         |

#### 📌 说明

- **一个 subject 被销毁后，在 PG 字典中将带有字段 `is_subject_destroyed: true`**
  （例如：面包 A 被切成了面包 B 和 C，PG 中保留面包 A 的信息，用于推断 B 和 C 的来源）

---

### 🧩 每个组件描述：`ComponentPG`

| 字段名               | 类型     | 说明                                     |
|----------------------|----------|------------------------------------------|
| `component`          | `Component` | 组件唯一标识                         |
| `component_destroyed`| `bool`   | 组件是否已被销毁                         |
| `pose`               | `Pose`   | 世界坐标系中的组件位置和朝向             |
| `scale`              | `Vector3`| 组件的缩放比例                           |
| `aabb`               | `AABB`   | 组件的包围盒信息                         |
| ...                  | ...      | 以下为实际挂载的组件数据结构（详见下文）|

> ℹ️ 注意：每个组件结构仅在其有实际数据时才会被填充，PG 采用 **增量更新机制**，未变化字段不会重新推送。

---

接下来的章节将按 `ComponentPG` 中的各类组件 逐条详细说明其字段内容。

## 🔍 各属性详解

### 🧱 通用字段（所有组件共享）

**以下字段在所有 `ComponentPG` 中均可用，用于表示组件的空间状态与生命周期状态。**

#### 📑 字段定义

| 字段名              | 类型       | 说明                                         |
|---------------------|------------|----------------------------------------------|
| `component`         | `Component`| 组件的唯一标识信息（包含组件名、类型等）     |
| `component_destroyed`| `bool`    | 该组件是否已被销毁，`true` 表示不再有效       |
| `pose`              | `Pose`     | 组件在世界坐标系下的位置与朝向                |
| `scale`             | `Vector3`  | 组件的缩放因子（x, y, z）                     |
| `aabb`              | `AABB`     | 组件的轴对齐包围盒 |

---


### `ue_collision_vertexes`

**该组件提供了实体简单碰撞体相关的几何信息，主要用于表示 Mesh 或物理实体的顶点数据。**

#### 📑 字段定义

| 字段名       | 类型                   | 说明                   |
|--------------|------------------------|------------------------|
| `vertexes`   | `repeated Vector3`     | 该组件对应的简单碰撞顶点，通常来自模型的碰撞数据。|

> 每个 `Vector3` 表示一个三维空间中的点，具有 `x, y, z` 三个浮点坐标。

---

### `character_energy`

**该组件维护了智能体自身的能量属性。其中的属性当智能体交互时会自动变化，例如吃东西时角色会恢复饥饿值，移动时会消耗体力**

#### 📑 字段定义

| 字段名            | 类型     | 说明                   |
|------------------|----------|------------------------|
| `energy.hungry` | `float`  | 当前饥饿值             |
| `energy.thirsty` | `float`  | 当前饥渴值           |
| `energy.stamina`   | `bool`   | 当前体力值          |
| `max_walk_distance`   | `float`   | 当前体力下可以移动的距离上限  |

---

### `food_energy`

**该组件描述了一个物体作为食物或饮品时的营养与消耗属性，常用于能量补充机制中，例如角色进食/饮水后恢复体力、减少饥渴值等。**

#### 📑 字段定义

| 字段名           | 类型              | 说明                                         |
|------------------|-------------------|----------------------------------------------|
| `edible_category`| `enum EEdibleCategory` | 可食用类别，支持三类：`EATABLE`, `DRINKABLE`, `NONE` |
| `anti_hungry`    | `float`           | 减少饥饿值的能力（通常用于固体食物）           |
| `anti_thirsty`   | `float`           | 减少口渴值的能力（通常用于饮品）               |
| `cubage`         | `float`           | 食物/饮品的总体积                            |
| `residue_volume` | `float`           | 当前剩余体积，动态变化                        |

> `edible_category` 的取值：
> - `EATABLE`: 固体食物（例如苹果）
> - `DRINKABLE`: 液体饮品（例如水）
> - `NONE`: 不可食用

---

### `capsule`

**该组件表示一个胶囊体碰撞结构，用于人型角色碰撞检测。胶囊体由一个圆柱体与两个半球组成，是虚幻引擎中常用的碰撞体形状。**

#### 📑 字段定义

| 字段名         | 类型     | 说明                                     |
|----------------|----------|------------------------------------------|
| `radius`       | `float`  | 胶囊体的半径                          |
| `half_height`  | `float`  | 胶囊体的半高         |

---

### `dirts`

**该组件表示物体上的污渍，常用于清洁类任务环境交互中。每个污渍结构包含其在三维空间中的位置、大小、旋转等信息。**

#### 📑 字段定义

| 字段名             | 类型         | 说明                                 |
|--------------------|--------------|--------------------------------------|
| `dirt_name`        | `string`     | 污渍名称或类型标识（如 `"milk"`） |
| `location`         | `Vector3`    | 污渍在组件局部坐标系中的位置         |
| `rotation`         | `Quaternion` | 污渍的方向（四元数表示）             |
| `size`             | `Vector3`    | 污渍的尺寸（宽高深）                 |
| `b_dirt_destroyed` | `bool`       | 是否该污渍已被移除                   |

> 每个 `ComponentPG` 中可包含多个 `Dirts` 项，表示复数个污渍实例。

---

### `object_in_hand`

**该组件表示智能体当前手中所持有的对象状态，区分左手、右手以及双手。**

#### 📑 字段定义

| 字段名   | 类型     | 说明                              |
|----------|----------|-----------------------------------|
| `left`   | `string` | 左手持有物体的名称      |
| `right`  | `string` | 右手持有物体的名称      |
| `two`    | `string` | 双手持有的物体名称 |

> 当某个字段为空字符串时表示对应手部未持有任何物体。

---

### `object_state`

**该组件用于表达物体的通用状态。(很多信息都包含在其中~)**

#### 📑 字段定义

| 字段名                    | 类型                                 | 说明 |
|---------------------------|--------------------------------------|------|
| `b_state_active`          | `bool`                               | 物体状态是否激活（比如空调是否打开） |
| `group_id`                | `string`                             | 所属的Group逻辑分组标识符 |
| `object_type`             | `string`                             | **物体的Rdf Type标签**|
| `place_object`            | `repeated string`                    | 该物体上放置了哪些其他物体（ID 列表） |
| `control_object`          | `repeated string`                    | 该物体可以控制哪些对象（和其他对象有相同的 GroupID） |
| `control_by_object`       | `repeated string`                    | 该物体被哪些对象控制（和其他对象有相同的 GroupID） |
| `attach_to_object`        | `string`                             | 附着在其他对象上时，其他对象 ID |
| `owns`                    | `string`                             | OwnsTo对象 ID |
| `liquid_type`             | `string`                             | 液体类型|
| `color`                   | `string`                             | 颜色描述|
| `shape`                   | `string`                             | 形状描述|
| `lookslike`               | `string`                             | 视觉近似描述|
| `wearing`                 | `repeated string`                    | 当前智能体穿戴了哪些物体 |
| `wearingby`               | `string`                             | 当前物体被谁穿戴 |
| `luminance`               | `float`                              | 亮度（0~1或其他范围） |
| `interaction_location_list` | `map<string, Vector3>`              | 支持交互的位置坐标（key为交互类型，如interact,place,stand等）|
| `is_part_of`              | `string`                             | 当前物体是其他物体的一部分，该值是其他物体的 id |
| `decrease_temperature`    | `float`                              | 交互时导致的温度变化值（表示物体是否制冷等） |
| `is_beside`               | `string`                             | （推测是该物体邻近的其他对象？）|
| `channel`                 | `string`                             | 电视频道 |
| `is_Powered`              | `bool`                               | 当前物体是否有供电 |
| `interaction_pose_list`   | `map<string, Pose>`                  | 支持交互的位置Transform坐标，旋转，缩放（key为交互类型，如interact,place,stand等） |
| `relation_subjects_list`  | `map<string, Subjects>`              | 仅支持电线连接的物体列表， key 是`"plug"`） |
| `check_point_list`        | `map<string, Pose>`                  | seek一个物体的，检查点列表（key为交互类型，default和其他，front, back等） |
| `b_lock`                  | `bool`                               | 门和抽屉是否上锁 |
| `hanging_on`              | `string`                             | 当前悬挂在哪个对象上 |
| `in_container_object`     | `string`                             | 被包含的容器对象 ID |
| `in_container_component`  | `string`                             | 被包含的容器组件名称 |
| `in_container_door`       | `repeated string`                    | 被包含的容器门名称列表 |

> 该组件广泛用于一切实体~。

---

### `container_state`

**该组件用于描述容器类对象的状态信息，包括空间体积、已放置物体、门组件等内容。典型应用场景包括抽屉、箱子、冰箱。**

#### 📑 字段定义

| 字段名           | 类型                    | 说明                                      |
|------------------|-------------------------|-------------------------------------------|
| `box`            | `AABB`                  | 容器的空间包围盒（轴对齐包围盒）          |
| `transform`      | `Transform`             | 容器在世界空间下的变换信息（位置+旋转+缩放） |
| `residue_volume` | `float`                 | 暂未实现                          |
| `place_objects`  | `repeated string`       | 当前放置在容器中的对象名称/ID              |
| `door_components`| `repeated string`       | 该容器所包含的门组件 |

> `place_objects` 和 `door_components` 是逻辑建模的关键，支持动态增删物体与门部件状态同步。

---

### `door_state`

**该组件用于描述门类组件的状态，包括其当前开关状态、通行性、最大开合角度/距离、类型以及附加信息。**

#### 📑 字段定义

| 字段名                          | 类型                          | 说明                                               |
|---------------------------------|-------------------------------|----------------------------------------------------|
| `door_name`                     | `string`                      | 门的名称标识（通常为组件名或唯一标识符）           |
| `b_impassable_door`             | `bool`                        | 该门是否为不可通行门（冰箱柜子等均为不可通行） |
| `transform`                     | `Transform`                   | 门的世界空间变换（位置 + 旋转 + 缩放）              |
| `max_open_angular_or_distance` | `float`                       | 门的最大开启角度（旋转门）或移动距离（滑动门）     |
| `open_angular_or_distance`      | `float`                       | 当前门的开合角度/距离                               |
| `b_closed`                      | `bool`                        | 门是否关闭（当角度或距离比例大于百分之六十视为打开） |
| `door_type`                     | `enum DoorType`               | 门的类型(旋转门或滑动门)             |
| `impassable_door_additional_info` | `ImpassableDoorAdditionalInfo` | 不可通行门的附加信息（与 oneof 联合使用）         |
| `passable_door_additional_info`   | `PassableDoorAdditionalInfo`   | 可通行门的附加信息（与 oneof 联合使用）           |

---

### `xr_info`

**该组件用于描述 NPC 在虚拟现实（VR）或动作捕捉（MoCap）场景下的 输入状态、姿态数据和交互状态。**

#### 📑 字段定义

| 字段名                  | 类型                         | 说明 |
|-------------------------|------------------------------|------|
| `vr_info`               | `VRInfo`                     | 当处于 VR 模式时，包含左右手的世界坐标姿态 |
| `motion_capture_info`   | `MoCapInfo`                  | 当处于动作捕捉模式时，包含骨骼动画数据与角色模型类型 |
| `camera_pose`           | `Pose`                       | NPC 第一视角摄像机的世界坐标姿态 |
| `object_in_hand`        | `ObjectInHand`               | 当前左右手或双手持有的对象（与 `object_in_hand` 组件结构一致） |
| `is_lefthand_pointing`  | `bool`                       | 左手是否正在指向某物 |
| `is_righthand_pointing` | `bool`                       | 右手是否正在指向某物 |
| `camera_param`          | `CamParam`                   | 摄像机参数（分辨率、FOV 等） |
| `action_mock_event_index` | `int32`                    | 当前模拟的动作事件索引，通常用于数据标注与调试 |

---

#### 🎭 XR 模式子结构

##### `VRInfo`

| 字段名          | 类型   | 说明                  |
|-----------------|--------|-----------------------|
| `left_hand_pose`| `Pose` | 左手的世界坐标姿态   |
| `right_hand_pose`| `Pose`| 右手的世界坐标姿态   |

##### `MoCapInfo`

| 字段名                | 类型                        | 说明                                      |
|-----------------------|-----------------------------|-------------------------------------------|
| `mocap_character_type`| `enum EMoCapCharacterType`  | 当前使用的动作捕捉角色类型               |
| `bones_data`          | `repeated Bone`             | 所有骨骼的动画数据（含位姿）             |

###### `EMoCapCharacterType` 枚举值包括：

- `UE4_DEFAULT`：默认虚幻引擎模型
- `TSHIRT_MOM`：T恤妈妈
- `SMALL_EYE_BOY`：小眼男孩
- `TSHIRT_DAD`：T恤爸爸
- `HOODIE_MOM`：卫衣妈妈
- `KINDERGARTEN_TEACHER`：幼儿园老师

> 该组件用于 VR、全身动作捕捉 NPC。

---

### `common_attribute`

**该组件用于描述物体或角色的通用属性。**

#### 📑 字段定义

| 字段名           | 类型              | 说明                            |
|------------------|-------------------|---------------------------------|
| `sleepy`         | `float`           | 使用此物体，降低疲倦程度。与character attribute 重合。范围（0，1），越高表现可降低困度越大|  |
| `boredom`        | `float`           | 使用此物体，降低无聊程度。与character attribute 重合。范围（0，1），越高表现可降低无聊度越大|
| `asset`          | `float`           | 此物体价值属性。范围（0，1），越高表现价值属性越高 |
| `common_struct`  | `CommonStruct`    | 常规物理/处理属性（见下方）      |
| `relation_struct`| `RelationStruct`  | 与其他对象的来源关系（见下方）  |

---

#### 🧱 `CommonStruct`

| 字段名     | 类型    | 说明                   |
|------------|---------|------------------------|
| `mass`     | `float` | 物体的质量             |
| `cutnumber`| `float` | 被切分成的份数（如蛋糕）|
| `welldone` | `bool`  | 是否已完成处理（如煮熟）|

---

#### 🔗 `RelationStruct`

| 字段名      | 类型     | 说明                     |
|-------------|----------|--------------------------|
| `sourcefrom`| `string` | 此物体来源于哪个父物体，如切面包，面包片来源于大面包 |

---

### `camera_param`

**该组件用于描述相机的核心参数。**

#### 📑 字段定义

| 字段名      | 类型     | 说明                                |
|-------------|----------|-------------------------------------|
| `fov`       | `float`  | 相机视野角度（Field of View，单位为度） |
| `width`     | `float`  | 相机输出图像宽度（像素）              |
| `height`    | `float`  | 相机输出图像高度（像素）              |
| `luminance` | `float`  | 当前视场亮度值（影响曝光模拟）         |

---

### `character_attribute`

**该组件用于描述角色当前的生理与环境感知状态，如疲倦程度、情绪状态、体温与环境光照等。**

#### 📑 字段定义

| 字段名      | 类型     | 说明                               |
|-------------|----------|------------------------------------|
| `sleepy`    | `float`  | 疲倦值             |
| `boredom`   | `float`  | 无聊程度       |
| `temperature` | `float`| 当前角色体温（单位为摄氏度） |
| `luminance` | `float`  | 当前环境感知到的光照强度             |

---

### `taking_component`

**该组件表示手部抓取物体信息**

#### 📑 字段定义

| 字段名        | 类型     | 说明                                     |
|---------------|----------|------------------------------------------|
| `take_object` | `string` | 当前正在拿取的目标对象名称或唯一标识符   |

---

### `television`

**该组件用于描述多媒体设备（如电视机、显示器）的内容播放状态。**

#### 📑 字段定义

| 字段名         | 类型     | 说明                                |
|----------------|----------|-------------------------------------|
| `num_of_shows` | `int32`  | 当前播放中的节目数量（频道数） |
| `description`  | `string` | 当前播放内容的简要描述（可用于语义推理） |

---

### `acoustic`

**该组件用于表示对象所携带或正在播放的音频信息。**

#### 📑 字段定义

| 字段名   | 类型         | 说明                                 |
|----------|--------------|--------------------------------------|
| `chunk`  | `ChunkData`  | 包含音频内容的数据块（详见下方）     |

---

#### 🧱 `ChunkData`

| 字段名 | 类型   | 说明                          |
|--------|--------|-------------------------------|
| `data` | `bytes`| 原始音频数据（PCM 32 二进制流） |

---

### `animation`

**该组件用于描述角色当前的动画表现状态，包括骨骼姿态、整体动作类型、头手状态等信息**

#### 📑 字段定义

| 字段名                | 类型                        | 说明                                  |
|-----------------------|-----------------------------|---------------------------------------|
| `bone_list`           | `map<string, Vector3>`      | 所有骨骼节点的名称与局部位置映射     |
| `current_speed`       | `float`                     | 当前移动的速度     |
| `full_body_type`      | `enum EFullBodyType`        | 全身动作状态（详见下方）             |
| `upper_body_type`     | `enum EUpperBodyType`       | 上半身动作状态                       |
| `left_hand_state_type`| `enum EHandStateType`       | 左手状态                             |
| `right_hand_state_type`| `enum EHandStateType`      | 右手状态                             |
| `head_state_type`     | `enum EHeadStateType`       | 头部状态                             |

---

#### 🧍 `EFullBodyType`（全身状态）

- `STANDING`: 站立
- `SLEEPING`: 躺下/睡觉
- `SITTING`: 坐着
- `STANDON`: 爬上某个物体后的状态
- `WALKING`: 正在走

#### 🧥 `EUpperBodyType`（上半身状态）

- `BODY_IDLE`: 静止
- `RAISE_HAND`: 举手
- `NOD_HEAD`: 点头
- `SHAKE_HEAD`: 摇头
- `CHAT`: 说话中
- `ROMP_PLAY`: 把玩
- `WIPE`: 擦拭
- `EAT_OR_DRINK`: 吃或喝
- `WAVE_HAND`: 招手

#### ✋ `EHandStateType`（手部状态）

- `HAND_IDLE`: 空闲
- `HAND_REACHING`: 伸手
- `POINTING_AT`: 指向

#### 🧠 `EHeadStateType`（头部状态）

- `HEAD_IDLE`: 静止
- `LOOKING_AT`: 注视某目标

---

### `character_movement_state`

**该组件用于表示角色当前的移动状态，包括线性速度、旋转速率以及特殊移动姿态（如蹲伏）**

#### 📑 字段定义

| 字段名               | 类型        | 说明                                     |
|----------------------|-------------|------------------------------------------|
| `velocity`           | `Vector3`   | 当前的移动速度向量（单位为 cm/s）         |
| `angular_yaw_velocity` | `float`   | 当前绕 Yaw（垂直轴）的旋转速度（单位为 °/s） |
| `is_crouching`       | `bool`      | 是否处于蹲伏姿态                        |

---

### `emotion_state`

**该组件用于表达角色当前的情绪状态，采用键值对结构记录多种情绪及其强度。**

#### 📑 字段定义

| 字段名   | 类型                   | 说明                             |
|----------|------------------------|----------------------------------|
| `emotion`| `map<string, float>`   | 各种情绪及其强度（取值范围为 0~1） |

> 支持的键：`"happy"`, `"sad"`, `"angry"`, `"fear"` 。值越高表示该情绪越强烈。

---

### `view_info`

**该组件用于描述相机视角的参数与位姿**

#### 📑 字段定义

| 字段名        | 类型        | 说明                                  |
|---------------|-------------|---------------------------------------|
| `camera_pose` | `Pose`      | 当前相机视角的世界坐标位姿（位置 + 朝向） |
| `camera_param`| `CamParam`  | 相机参数（视野角、分辨率、亮度等，详见 `camera_param` 组件） |
