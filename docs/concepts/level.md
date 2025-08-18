# 🗺️ 关卡（Level）

## 📖 什么是 Level？

在 Unreal Engine 中，**Level** 是虚拟世界的基本构建单元，它定义了一个仿真场景的空间布局、对象、光照、环境音效等。TongSim 继承了这一设计理念，每一个关卡都是一个**智能体生活仿真环境的载体**。

在 TongSim 中，所有的行为模拟都必须发生在一个已加载的 Level 中。因此，理解和正确使用关卡系统是实现仿真任务的第一步。

---

## 🔁 关卡切换机制

TongSim Python SDK 提供了 同步/异步 接口 `open_level(level_name: str)` 用于加载并切换场景。

这个过程**本质上是异步的**，包含两个关键阶段：

1. **UE 端资源管理**：
   - 卸载当前 Level（释放内存）
   - 加载新 Level（重新构建导航、对象等资源）

2. **Python SDK 端资源清理与初始化**：
   - 自动关闭所有与旧 Level 相关的异步任务与 gRPC 流（如 PG 流、图像流）
   - await 等待 UE 侧 gRPC消息写回

!!! warning "切换关卡会触发环境重置"
    每次调用 `open_level()`，都等价于将整个仿真环境进行一次**重置**。任何Entitiy(实体)对象的引用、gRPC流式连接或状态缓存都会失效。你需要重新调用如 `pg_manager.start_pg_stream()` 等接口重新订阅所需信息。

---

## ✅ 推荐实践

可参考 example 中的 TODO.

---
