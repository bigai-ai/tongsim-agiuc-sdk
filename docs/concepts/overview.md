# 🌐 TongSim 架构概览

TongSim 是一个虚拟智能体仿真平台，主要由以下核心组件构成：

- **TongSim Unreal**
- **TongSim Python SDK**
- **TongSim WebSignalServer (信令服务器)**
- **TongSim Audio2Face (口型算法服务)**

这几个组件协同构建了一个可交互、可扩展的虚拟世界仿真框架。

![TongSim Framework](./images/tongsim_framework.excalidraw.png)

---

## 🕹️ TongSim Unreal

TongSim Unreal 使用 **Unreal Engine (UE)** 研发，是虚拟智能体生活仿真的核心运行环境。

它主要具备以下特性和设计：

- **3D 仿真环境与智能体行为支持**
    - 可加载和配置多样化任务场景，支持自定义扩展。
    - 提供图像、声音、点云等多维度感知数据获取，满足智能体感知和推理需求。
    - 支持通过动作接口驱动智能体完成移动、交互、物体操作等任务。
    - 提供两类仿真机制：
        - *物理仿真*：基于刚体、流体、软体等算法实现高精度物理状态仿真。
        - *因果逻辑仿真*：用于物理仿真难以高效覆盖的复杂现象，以简化因果逻辑高效模拟任务逻辑。

- **分布式架构设计**
  可通过加入多个 **TongSim UE Client** 分担仿真计算压力，实现多机协同的并发环境仿真，目前主要用于多智能体环境。

- **VR 交互支持**
  可连接 **TongSim VR Client**，支持用户通过 VR 设备以投影进入虚拟世界，与场景或智能体交互。

- **高效接口通信**
  启动时自动启动 **gRPC Server**，支持 TongSim Python SDK 等外部模块通过 gRPC 通信实现场景控制、数据采集、智能体驱动和动作分发。

---

## 🧠 TongSim Python SDK

TongSim Python SDK 是 TongSim 的官方客户端开发工具包。它作为 **gRPC Client** 与 TongSim Unreal 交互，通过 gRPC 通信实现：

- 定义环境和场景
- 获取观测信息（如场景状态、智能体状态）
- 驱动智能体行为，执行任务

开发者可以基于 TongSim Python SDK 快速构建各类智能体交互逻辑、任务规划、行为控制等。

---

## 📡 TongSim WebSignalServer（信令服务器）

TongSim WebSignalServer 是 TongSim 的流媒体服务组件，负责：

- 与 TongSim Unreal 通过 **Pixel Streaming**（底层通信协议为 WebRTC）对接
- 实现云游戏式的视频流、音频流订阅
- 实现输入设备交互的远程传递（如网页端输入设备的键鼠、手柄指令）

借助 WebSignalServer，用户可以无需本地安装复杂客户端，通过浏览器即可访问虚拟世界。

---

## 👄 TongSim Audio2Face

TongSim Audio2Face 是 TongSim 提供的口型算法服务，主要功能包括：

- 接收流式文本输出或音频 buffer
- 实时生成智能体口型动画
- 自动驱动智能体嘴部动作以匹配语音或文本

该模块可与 TongSim Unreal 智能体表情系统无缝对接，为虚拟角色提供更加生动的口型表现。

---

> 💡 后续文档将详细介绍 TongSim Python SDK 模块的工作原理与接口设计。
