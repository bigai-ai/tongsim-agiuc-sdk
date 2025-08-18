# 🌟 TongSim 安装选择总览

!!! danger "⚠️ 重要：本仓库为 **比赛专用精简版**（请先阅读）"
    **TongSim（本次开源）仅供比赛使用，功能经过大幅裁剪。**

    - 安装**比赛版本 TongSim**请转到 **比赛 Env 仓库文档**：[`Env Docs`](https://github.com/bigai-ai/tongsim-indoor-nav-env)。
    - 下方出现的**安装方法**描述的是**院内完整版本 TongSim**的安装逻辑，供参考；如需体验**完整版本**，请联系内部人员。
    - 本次比赛发布版本为**专用精简版**的构建：大量**传感、交互、资产、动作**等功能未包含；

欢迎使用 **TongSim**。在开始安装前，请根据您的系统和用途选择合适的安装方式，**并注意对应的版本分支选择**。

---

## 💡 分支 / 版本说明

!!! note "为什么存在多个分支？"
    TongSim 在核心功能上保持一致，但为了适配不同的应用场景，会在不同分支会定制不同的地图、模型等资产配置。用户可根据需求选择合适的分支安装使用。

---

### 🖥️ Windows 客户端发布版

通过 SVN 拉取可运行的打包版本（包含 EXE、资源和配置文件），适合直接运行体验。

- 可选分支：
  - TongAI 发布版：`http://svn.mybigai.ac.cn:18080/svn/Demo/trunk/AIBabyUE5Client`
  - TongLoop 发布版：`http://svn.mybigai.ac.cn:18080/svn/TongLoop/trunk/windows_client/`

- SVN 地址示例：

```bash
svn checkout http://svn.mybigai.ac.cn:18080/svn/Demo/trunk/AIBabyUE5Client
```

---

### 🧰 Windows 编辑器版

通过 SVN 拉取 Unreal 项目资源，可在 TongSim 发布的 UE 编辑器中打开，支持自定义蓝图、关卡、角色等。

- 可选分支：
  - TongAI 编辑器：`http://svn.mybigai.ac.cn:18080/svn/TongSim/trunk`
  - TongAI 引擎：`http://svn.mybigai.ac.cn:18080/svn/Demo/trunk/TongUnrealEngine`
  - TongLoop 编辑器：`http://svn.mybigai.ac.cn:18080/svn/TongLoop/trunk/project/`
  - TongLoop 引擎：`http://svn.mybigai.ac.cn:18080/svn/TongLoop/trunk/engine/`

- SVN 地址示例：

```bash
svn checkout http://svn.mybigai.ac.cn:18080/svn/TongSim/trunk
```

---

### 🐳 Docker 镜像（适用于 Ubuntu）

TongSim 提供了预构建的镜像，支持 GUI 与 Headless 模式，适合大规模仿真任务和云端部署。

- 可选镜像标签：
  - TongAI 项目使用：`harbor.mybigai.ac.cn/tongsim/tongai`
  - TongLoop 项目使用：`harbor.mybigai.ac.cn/tongsim/tongloop`

- Harbor 镜像拉取示例：

```bash
docker pull harbor.mybigai.ac.cn/tongsim/tongai:latest
```

Harbor 地址（登录后可查看所有镜像）：
👉 [HARBOR 镜像地址](https://harbor.mybigai.ac.cn/harbor/projects)

---


## 🚀 安装选项一览

| 🖥️ 操作系统 | 📦 安装方式 | ✅ 场景推荐 |
|------------|-------------|------------|
| Windows    | 客户端发布版（SVN 拉取 + EXE 启动） | 推荐需要快速体验的用户。适合演示、测试、录制 Demo。无需开发环境配置。 |
| Windows    | 编辑器发布版（SVN 拉取 + UE 编辑器） | 推荐需要修改地图、角色、蓝图逻辑等内容的用户。 |
| Linux（Ubuntu） | Docker 镜像运行 | 推荐在服务器上进行批量仿真、模型训练或远程部署用户使用。无需图形界面。 |

---

## 🔑 如何选择？

- ✅ **快速体验 TongSim** → 使用 **Windows 发布版** 或 **Docker 镜像**
- ✅ **在 Linux / 云端 / 无界面环境运行** → 使用 **Docker 镜像**
- ✅ **需要开发或修改 UE 环境内容** → 使用 **编辑器发布版**
- ✅ **需要修改底层 UE 引擎或项目功能** → 使用 **源码版 UE 引擎 + TongSim UE 项目**

---

## 📌 相关文档

- [Windows 平台安装指南](windows_client_installation.md)
- [Ubuntu Docker 镜像安装指南](ubuntu_docker_installation.md)

---

## ⚠️ 注意事项

!!! warning "路径命名规范"
    请确保所有安装路径 **不包含中文、空格或特殊字符**，以避免资源加载错误或依赖解析失败。
