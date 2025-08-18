# TongSim AGIUC SDK

> **Competition**: The 1st Industry–University Artificial General Intelligence Competition（第一届产学结合高校通用人工智能大赛）

---

## 概览

**TongSim AGIUC SDK** 围绕 **TongSim**（基于 Unreal Engine 的智能体仿真/训练平台）提供 Python 开发工具与示例，
帮助本次大赛的 **竞赛选手** 与 **研究者** 快速接入**感知 → 决策 → 动作执行**流水线，搭建任务与评测流程。

---

## ⚠️ 公告（Competition Edition）
本仓库为**比赛专用的删减版 TongSim**。仅提供**便于 RL 训练机器人移动**相关的能力与资产（如：基础定位/移动、场景状态信息获取），
**不包含**完整版中的高级能力与大规模资产库。  
如对体验**完整版 TongSim**感兴趣（包含更丰富的传感、物理、交互工具链），欢迎联系：wukunlun@bigai.ai。

---

## 📚 文档
- **GitHub Pages（MkDocs）**：https://bigai-ai.github.io/tongsim-agiuc-sdk/
- 本地预览：
  ```bash
  uv run mkdocs serve -a 0.0.0.0:8000
  ```

> 提交 PR 时请同步更新 `docs/` 下的内容与示例，确保 README 与站点一致。

---

## 相关链接
- [大赛官方网站参考](https://agiuc.mybigai.ac.cn/)
- [TongSim 介绍网站](https://open.bigai.ai/tongsim)
- [TongSim-AGIUC-Env Github](https://github.com/bigai-ai/tongsim-indoor-nav-env)

---

## 主要特性

- 🧱 **统一 SDK 接口**：屏蔽 UE/gRPC 细节，提供清晰 Python API。  
- 🧭 **场景/实体控制**：关卡加载、实体查询/生成、姿态与运动控制。  
- 👀 **感知管线**：图像 / PG 等多模态数据的订阅与拉取（按需）。  
- 🔁 **同步/异步封装**：对外提供同步 API，并提供等价异步 API；内部统一事件循环保证安全调度。

---

## 支持环境

- **操作系统**：Windows 10/11、Ubuntu 22.04
- **Python**：3.11–3.13（推荐 3.12+）

> 具体依赖以 `pyproject.toml` 为准。

---

## 安装与环境准备

本项目推荐使用 [`uv`](https://hellowac.github.io/uv-zh-cn/) 进行依赖与环境管理（亦可使用 `pip`，但不作为推荐路径）。

### 1) 安装 `uv`
参考官网完成安装。

### 2) 同步依赖并安装提交钩子
```bash
# 安装项目依赖（包含默认依赖组）
uv sync

# 安装 Git 提交钩子（自动进行代码检查/格式化等）
uv run pre-commit install
```

---

## 开发与贡献

欢迎 Issue / PR！在提交之前请先：

```bash
# 运行全量 pre-commit 检查
uv run pre-commit run --all-files
```

建议遵循：
- **Conventional Commits**（如 `feat:` / `fix:` / `docs:` 等）  
- 提交粒度小、PR 描述清晰可复现  
- 为核心功能与 Bug 修复补充测试与文档（并同步更新 `docs/` 与示例）

---

## 常见问题（FAQ）

**Q: UE/TongSim 端需要做什么准备？**  
A: 确保目标 UE 工程启动了对应的 gRPC 服务，并开放 **`5056`** 与 **`50025`** 端口（如有自定义端口，以工程实际配置为准）。

**Q: SDK 是否线程安全/并发友好？**  
A: 同时提供**同步**与**异步** API，面向**单个 Unreal 实例**使用场景。内部通过**统一事件循环**调度异步任务，从而在异步逻辑层面保证线程安全；并发策略以实现为准。

---

## 许可证

请参考 `LICENSE`
