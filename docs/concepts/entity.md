# 🧱 Entity：统一的实体表示

TongSim 中的 `Entity` 是对 TongSim 世界中对象（如智能体、家具、相机传感器、一些全局管理器对象等）的统一抽象。它继承 Unreal 中 `Actor + Component` 的组合结构，并在 Python SDK 中通过能力组合（Ability）构建高可拓展的实体表示。

[API 参考](../api/entity_base.md)

---

## Unreal 的结构背景

在 Unreal 中，所有场景对象都是 `Actor`，其行为和属性由挂载的 `Component` 决定。理论上，不同对象应组合不同的组件以表现其功能。

TongSim Unreal 中为了快速支持各种交互逻辑，**几乎所有类型的 Actor 都默认挂载了绝大部分类型的 Component**，即使这些组件在实际运行中毫无意义。导致如下问题：

例如：

> 一个空调（AirConditioner）Actor 内也可能挂载了 `FoodComponent`，导致它在接口层也“可以被吃掉”。

这类“无意义能力”的混杂让通信层的 Actor 表达变得臃肿、模糊，也让 Python 端难以精准地表达一个对象“能做什么”。

---

## ✅ Entity + Ability

为了重构实体逻辑，TongSim Python SDK 引入 Ability 重组 Entity：

### Entity 的职责

- 持有 Entity ID 与所有组件 ID
- 提供能力判断与访问（Ability）
- 不包含实际组件数据，仅作为行为路由中心

### Ability 是什么？

[Ability](ability.md) 是一组接口协议（Protocol），代表某种功能能力：

- `CameraAbility`：图像采集能力
- `AssetAbility`：资产信息能力

每种 Ability 均对应一个实现类（Impl），由 SDK 内部根据组件配置自动匹配生成。

### 使用方式示例

```python
if entity.has_ability(CameraAbility):
    camera = entity.as_(CameraAbility)
    camera.start_imagedata_streaming(rgb=True)
```

SDK 会根据组件结构，自动判断是否支持该能力并绑定实现。

!!! info "推荐使用组合实体类型"
    除了 `as_(Ability)` 的方式，我们更推荐使用**组合好的实体类**（如 `AgentEntity`, `CameraEntity`），这些类在定义时已绑定好常用能力，并提供更清晰的代码提示与封装。
    <!-- 详见：[组合实体类型说明](./mixin_entity.md) -->

---

## 获取 Entity 的方式

你可以通过多种方式创建或获取 Entity：

### 🆕 spawn_entity()

创建新的实体对象（如放置一个物品、生成一个 agent 等）：

```python
entity = ue.spawn_entity(
    entity_type=ts.BaseObjectEntity,
    blueprint="BP_Cup",
    location=Vector3(0.0, 0.0, 100.0),
)
```

若你已定义好自定义 Entity 类（如 `MyCustomEntity`），可传入 `entity_type=MyCustomEntity` 实现封装。

- **blueprint 名称可以参考 [TongAI 资产库](https://asset-tongai.mybigai.ac.cn/)**

### 📌 entity_from_id()

若你已知实体的唯一 ID，可通过此方法快速恢复实体对象：

```python
entity = ue.entity_from_id(ts.BaseObjectEntity, entity_id="BP_Cup_C_1")
```

相比 `get_entity_by_name`，该接口性能更优。

### 🔍 get_entity_by_name()

可通过实体名称模糊搜索并恢复实体：

```python
entity = ue.get_entity_by_name(ts.BaseObjectEntity, name="Cup")
```

内部基于 UE 的 object 名称进行匹配，适合测试和非精确场景。

### 📦 get_entities_by_rdf_type()

根据类型（如 `"cup"`, `"tv"`）批量获取一个场景中所有该类型的实体：

```python
cups = ue.get_entities_by_rdf_type(ts.BaseObjectEntity, rdf_type="cup")
```

适用于泛化任务执行或语义任务规划。

---
