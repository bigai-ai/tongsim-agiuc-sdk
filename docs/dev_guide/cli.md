本页面汇总了 TongSim 项目开发过程中常用的命令行指令，涵盖依赖安装、代码检查、测试、文档构建等场景。建议配合 `uv` 工具使用，可提升运行效率和依赖一致性。

---

## ⚡ `uv` 常用命令

> `uv` 是本项目的统一依赖管理与执行工具，用于替代 `pip`、`poetry`、`pipenv` 等传统工具组合。

```bash
uv sync                 # 安装默认依赖（默认组）
uv sync --all-groups   # 安装所有依赖（包括 dev/test/docsd 等）
uv sync --group docs   # 仅安装文档开发所需依赖
```

```bash
uv run ./examples/xxx.py       # 执行 Python 脚本
```

### ⚙️ 依赖项管理

```bash
uv add numpy                            # 将 `numpy` 添加到默认分组
uv add mkdocs --group docs              # 将 `mkdocs` 添加到 docs 分组

uv remove numpy                         # 移除 `numpy` 包

uv add tongsim-api-protocol --upgrade-package tongsim-api-protocol     # 升级 `tongsim-api-protocol` 包
```

!!! tip "依赖分组建议"
    注意使用 `--group` 明确指定依赖用途，例如:

    - `docs`: 文档相关依赖（如 `mkdocs`, `material`）
    - `test`: 测试相关依赖（如 `pytest`, `coverage`）
    - `dev`: 开发辅助工具（如 `ruff`, `pre-commit`）

    这样可以在协作开发中避免不必要的依赖冗余。

### 🔒 锁定依赖版本（手动）

如需更新 `uv.lock` 文件，可手动执行:

```bash
uv lock
```

---

## 🧪 测试命令（`pytest`）

```bash
uv run pytest -s --grpc-ip=127.0.0.1
```

常用参数:

```bash
uv run pytest -s             # 允许标准输出直接显示在控制台中
uv run pytest -k keyword     # 运行匹配指定关键字的测试
uv run pytest --maxfail=3    # 最多失败 3 个后停止
```

---

## ✅ 代码质量检查（`pre-commit`）

```bash
uv run pre-commit install      # 安装提交钩子（首次设置）
uv run pre-commit run --all-files  # 手动执行全部检查器
```

`pre-commit` 中已集成:

- 空格、空行、合并冲突检测
- JSON/YAML/TOML 配置语法校验
- `ruff` 检查与格式化
- `uv-sync` 检查依赖锁一致性

---

## 🧹 代码风格检查与格式化

### 使用 [`ruff`](https://docs.astral.sh/ruff/)

```bash
uv run ruff check .                    # 执行静态代码检查
uv run ruff check --fix                # 自动修复部分错误
uv run ruff check --select I --fix     # 修复 import 顺序
uv run ruff format                     # 格式化整个项目
```

---

### 使用 [`black`](https://black.readthedocs.io/en/stable/)（如需）

> 本项目默认使用 `ruff format`，但兼容 `black`

```bash
uv run black .
```

---

## 📚 文档构建（`mkdocs`）

```bash
uv run mkdocs serve             # 启动本地文档开发服务
uv run mkdocs serve -a 0.0.0.0:8001  # 指定端口和监听地址
uv run mkdocs build             # 构建静态文档（输出到 public/）
```

文档入口配置在 `mkdocs.yml`，内容位于 `docs/` 目录。

---

## 🚀 打包与发布（`uv` 构建）

```bash
uv build
uv publish --publish-url https://nexus.mybigai.ac.cn/repository/pypi-host
```

- `uv build` 会生成 `.whl` 和 `.tar.gz` 包至 `dist/` 目录
- `uv publish` 用于上传包到私有镜像（BIGAI Nexus PyPI）
