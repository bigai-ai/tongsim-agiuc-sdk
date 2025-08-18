# 🧩 Ability：实体能力的解耦封装机制

Ability 是 TongSim SDK 中对虚拟世界对象功能的抽象，它允许开发者以**模块化、可组合的方式**，访问和控制场景中实体的各种行为与属性。

---

## 谁来实现 Ability？

Ability 的实现类由 SDK 内部自动注册，统一继承自基类 `AbilityImplBase`，该类具备如下特性：

- 持有对应实体的 entity ID 和 world context
- 可访问组件 ID 与连接信息（gRPC / stream）
- 可通过异步或同步方式发起底层通信调用

---

## 能力的调用流程

调用流程如下：

1. 从 `Entity` 实例中调用 `as_()` 方法获取能力接口（如 `CameraAbility`）
2. SDK 自动检测能力是否可用（调用 `is_applicable`）
3. 动态加载实现类（如 `CameraAbilityImpl`）并绑定上下文
4. 调用能力方法，即完成功能调用

```python
if entity.has_ability(ConsumableEnergyAbility):
    energy = entity.as_(ConsumableEnergyAbility).get_consumable_energy()
```

支持同步和异步版本，推荐同步接口用于主线程控制，异步接口用于高性能场景。

---

## API 参考

### Action

[Action 能力 API](../api/ability_action.md)

定义了角色动画执行的相关接口。

---

### Asset

[Asset 能力 API](../api/ability_asset.md)

提供对象的资产配置信息的获取接口。

---

### Camera

[Camera 能力 API](../api/ability_camera.md)

相机能力接口定义。

---

### ConsumableEnergy

[ConsumableEnergy 能力 API](../api/ability_consumable_energy.md)

定义了食物与饮品能量管理的接口。

---

### Interactable

[Interactable 能力 API](../api/ability_interactable.md)

定义了支持交互控制的实体能力接口。

---

### Powerable

[Powerable 能力 API](../api/ability_powerable.md)

定义了具备通电状态管理的实体能力接口。


### Scene

[Scene 能力 API](../api/ability_scene.md)

空间能力接口，提供 Entity 的位置、旋转、朝向向量等能力。
