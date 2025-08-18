
## 🐍 Python 开发环境

本项目使用 [uv](https://hellowac.github.io/uv-zh-cn/) 进行依赖管理与运行工具，替代 `pip + venv` 等传统方案。

建议你查阅官方文档熟悉 `uv` 的基本使用方式，或参考我们准备的[项目常用命令](./cli.md)。

### 初始化项目依赖

[安装uv](https://hellowac.github.io/uv-zh-cn/getting-started/installation/)后，请在项目根目录下运行:

```bash
uv sync --all-groups                # 该命令会安装所有分组的依赖，包括开发、测试、文档等。
uv run pre-commit install           # 注册 pre-commit
```

---

## 🧪 Git 分支

本项目采用主流的 **分支协作模型**，结合开源社区实践与内部开发流程，确保代码质量、协作效率与版本发布的有序性。

### 主干分支（永久存在）

| 分支名 | 说明 |
|--------|------|
| `main` | 生产主分支，用于发布稳定版本。适配 CI 自动发布流程。为保护主干质量，**请勿在 `main` 上直接开发**。 |
| `dev`  | 开发主分支，用于合并日常功能、文档与测试开发分支，经过验证后再合并到 `main` |

### 功能分支（临时分支）

| 分支名规则      | 说明 |
|----------------|------|
| `feat/xxx-xxx`  | ✨ 功能开发分支，来源于 `dev`，提交功能开发相关内容 |
| `doc/xxx-xxx`   | 📝 文档编辑分支，来源于 `dev`，用于补充或修复文档内容 |
| `fix/xxx`       | 🐛 Bug 修复（通常是紧急问题或用户反馈） |
| `refactor/xxx`  | 🧹 代码重构（重写实现，不改变外部行为） |
| `perf/xxx`      | ⚡ 性能优化（提升运行效率、减少资源占用等） |
| `chore/xxx`     | 🧰 杂项维护（依赖升级、配置调整、CI 优化等） |

### 推荐开发流程

1. **创建功能分支**

   从 `dev` 分支拉出新分支:

   ```bash
   git switch dev
   git pull
   git checkout -b feat/your-feature-name
   ```

2. **提交代码 & 合并请求**

   开发完成后提交 Merge Request（MR）到 `dev` 分支，需至少一位团队成员 Review 后方可合并。

   > ✅ 建议使用 `Squash` 方式合并，以保持 `dev` 分支历史简洁。

---

## 🧹 代码质量检查（Pre-commit）

本项目使用 [`pre-commit`](https://pre-commit.com/) 自动化工具，在提交代码前自动执行一系列代码质量检查与格式化操作，确保提交代码符合规范、清洁、无语法隐患。

---

### 安装 Git 提交钩子

```bash
uv run pre-commit install
```

安装后，Git 会在每次执行 `git commit` 前自动运行以下检查项:

- 去除尾部空格（`trailing-whitespace`）
- 修复缺失或重复的文件结尾空行（`end-of-file-fixer`）
- 检查配置文件语法（`.toml` / `.yaml` / `.json`）
- 检查是否存在未解决的合并冲突标记（`check-merge-conflict`）
- 校验依赖是否与锁文件一致（`uv-sync`）
- 检查 `uv.lock` 文件是否需要更新（`uv-lock`）
- 使用 [`ruff`](https://docs.astral.sh/ruff/) 进行代码检查与自动修复（`--fix` 模式）
- 使用 `ruff format` 进行统一代码格式化

---

### 手动运行所有检查

```bash
uv run pre-commit run --all-files
```

该命令会在整个项目范围内执行所有启用的钩子，常用于 CI 前本地验证或一次性修复项目旧代码。

---

!!! tip "VSCode 插件建议"
    为获得最佳体验，建议安装以下插件来实现代码编辑阶段的自动检查与修复:

    - 🐍 **Ruff** — 实时 Lint 与自动格式化
    - 🎨 **Black Formatter** — 辅助处理格式化（尽管本项目使用 `ruff format`）
    - ⚡ **Pylance** — 快速、类型感知的 Python 分析引擎

    安装后请在 VSCode 设置中启用 `"Format on Save"` 以自动执行代码风格修复。

---

## 📚 文档开发

本项目使用 [MkDocs](https://www.mkdocs.org/) 作为静态文档生成工具，配合 [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) 主题提供良好的文档可读性和交互体验。

文档内容位于 `docs/` 目录，配置文件为 `mkdocs.yml`，支持多语言、模块化组织、代码高亮、标签页、版本切换等高级功能。

### 安装文档相关依赖

请先确保已经安装项目的 `docs` 分组依赖:

```bash
uv sync --group docs
```

---

### 启动本地文档开发服务器

运行以下命令在本地启动开发服务器，支持热更新:

```bash
uv run mkdocs serve
```

默认地址为: <http://127.0.0.1:8000>（可配置）

---

### 本地验证构建是否正常

在本地构建静态站点，确认无错误:

```bash
uv run mkdocs build
```

构建结果将输出到 `public/` 目录（可配置）。

---

## 🚀 项目打包与发布

本项目使用 [`uv`](https://docs.astral.sh/uv/) 进行构建与发布。

### 手动发布（推荐用于内测或私有部署）

以发布到 BIGAI 的 Nexus 私有 PyPI 源为例:

```bash
uv build
uv publish --publish-url https://nexus.mybigai.ac.cn/repository/pypi-host
```

上述命令会:

- 构建 `dist/*.whl` 包和 `*.tar.gz` 源码包
- 上传到指定的镜像源中（支持认证）

---

### 自动发布（CI/CD）

自动发布流程，将在以下场景自动触发:

- Push 带有 `vX.Y.Z` Git标签（如 `v0.3.1a4`）时

---

!!! tip "发布前检查建议"
    - **请务必确保版本号已更新！**
    - 可在本地打包后，检查 `dist/*.whl` 进行发布前验证

---

## 📂 项目结构概览

```text
TongSim-python-sdk/
├── docs/                     # MkDocs 文档目录
├── examples/                 # 功能示例目录
├── src/                      # 主代码目录
├── tests/                    # 单元测试脚本目录
├── mkdocs.yml                # MkDocs 配置文件
├── pyproject.toml            # 项目配置文件（由 uv 解析）
└── README.md                 # 项目说明文档
```

---

## 🔗 参考链接

- [uv 官方文档](https://docs.astral.sh/uv/)
- [pre-commit 官网](https://pre-commit.com/)
- [ruff 文档](https://docs.astral.sh/ruff/)
- [MkDocs 官网](https://www.mkdocs.org/)
- [MkDocs Material 官网](https://squidfunk.github.io/mkdocs-material/)
