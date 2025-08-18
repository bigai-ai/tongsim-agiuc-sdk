# 🐍 TongSim Python SDK 安装指南

!!! danger "⚠️ 重要：本仓库为 **比赛专用精简版**（请先阅读）"
    **TongSim（本次开源）仅供比赛使用，功能经过大幅裁剪。**

    - 安装**比赛版本 TongSim**请转到 **比赛 Env 仓库文档**：[`Env Docs`](https://github.com/bigai-ai/tongsim-indoor-nav-env)。
    - 下方出现的**安装方法**描述的是**院内完整版本 TongSim**的安装逻辑，供参考；如需体验**完整版本**，请联系内部人员。
    - 本次比赛发布版本为**专用精简版**的构建：大量**传感、交互、资产、动作**等功能未包含；

TongSim Python SDK 提供了控制 TongSim Unreal 仿真平台的核心 API。
你可以通过 **院内 PyPI 镜像源** 安装，或从源码构建开发环境。

---

## 📦 从院内 PyPI 镜像源安装

TongSim Python SDK 可以通过院内 PyPI 镜像源完成安装，支持 `uv` 与 `conda` 两种常见环境管理工具。请根据你的项目管理偏好选择对应方式。

=== "🔧 使用 uv 安装（推荐）"

    推荐使用 `uv` 作为现代项目管理工具，兼容性强，速度快。

    ```toml
    # pyproject.toml 中配置镜像源索引
    [tool.uv.sources]
    tongsim = { index = "bigai" }
    tongsim-api-protocol = { index = "bigai" }

    [[tool.uv.index]]
    name = "bigai"
    url = "https://nexus.mybigai.ac.cn/repository/pypi/simple"
    ```

    然后安装：

    ```bash
    uv add tongsim
    ```

    !!! note "关于 uv 与镜像源"
        由于 `tongsim` 依赖 `tongsim-api-protocol`，两者均需从院内镜像源下载。建议在 `pyproject.toml` 中将其索引显式绑定为 `bigai`，以避免 uv 拉取失败的问题。

=== "🐍 使用 conda 安装"

    如果你更习惯使用 `conda` 管理 Python 环境，可以使用以下步骤：

    ```bash
    conda create -n tongsim python=3.12 -y
    conda activate tongsim

    # 配置 pip 使用镜像源
    pip config set global.index-url https://nexus.mybigai.ac.cn/repository/pypi/simple

    # 安装 SDK
    pip install tongsim
    ```

### 🔗 镜像源地址：

- **镜像源 Index**：
  `https://nexus.mybigai.ac.cn/repository/pypi/simple`

- **浏览镜像源包与版本：**
  [点击进入TongSim版本查询页面 🔍](https://nexus.mybigai.ac.cn/#browse/browse:pypi-host:tongsim)

---

## 🔧 从源码构建安装

如需调试 Python SDK，可直接从 Git 拉取源码。

### 📁 Git 仓库地址

```bash
git clone https://gitlab.mybigai.ac.cn/tongsim/tongsim-python.git
cd tongsim-python
```

### uv 初始化

```bash
uv sync
```

### 🚀 运行示例

```bash
uv run python examples/demo.py
```

---

## ✅ 安装确认

```bash
python -c "import tongsim; print(tongsim.__version__)"
```

---

## 📌 相关说明

- `tongsim-api-protocol` 是一个与 TongSim Unreal 通信所用的 proto 定义生成模块，必须从镜像源安装

---

## 📚 推荐阅读

- [开发环境设置指南](../dev_guide/setup.md)
- [常用命令参考](../dev_guide/cli.md)
