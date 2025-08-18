本项目使用 [pytest](https://docs.pytest.org/en/stable/) 作为测试框架，配合 `uv` 统一执行测试命令。你可以通过运行测试来验证核心 API 行为。

---

## 📝 编写第一个测试用例

在tests下创建一个测试文件 `test_example.py`:

```python
# test_example.py

def add(a, b):
    return a + b

def test_add():
    assert add(1, 2) == 3
```

> ✅ `pytest` 会自动识别以 `test_` 开头的函数作为测试用例。

在终端中运行:

```bash
uv run pytest -k test_add
```

你将看到如下输出:

```text
collected 1 item

test_example.py .                                           [100%]

1 passed in 0.01s
```

---

## 🧩 conftest.py 简介

`tests/conftest.py` 中定义了全局共享的测试工具，目前包括:

- ✅ `--gprc-ip` : 可以通过命令行参数控制 gRPC 测试连接地址
- ✅ `conn_main`, `conn_alt`: 基于连接封装的 session 级 fixture，可在多个测试中复用
- ✅ `setup_logging`: 初始化日志系统

### 📦 fixture

`fixture` 是 pytest 提供的一种可复用的测试“准备函数”。

```python
import pytest

@pytest.fixture
def sample_list():
    return [1, 2, 3]

def test_len(sample_list):
    assert len(sample_list) == 3
```

> ✅ 测试函数中只要写上 `sample_list` 参数，pytest 就会自动调用对应的 fixture 并传入返回值。

---

## 🧠 理解 assert 断言

Python 的 `assert` 是测试中最常用的语句。

```python
assert 2 + 2 == 4     # ✅ 通过
assert len("hi") == 3 # ❌ 失败，将报错
```

失败时 `pytest` 会自动显示表达式的值，帮助调试。

- ✅ 所有 `assert` 都应具备明确的**判断目标**
- ✅ 失败时提供足够的信息（如日志、异常栈）

---

## 📁 测试文件与函数命名规范

| 规则                  | 示例                |
|-----------------------|---------------------|
| 文件名以 `test_` 开头 | `test_math.py`      |
| 函数名以 `test_` 开头 | `test_add()`        |
| 测试文件可位于任意目录 | 推荐放在 `tests/` 文件夹中 |

---

## 📌 常用命令速查

```bash
uv run pytest -s . --grpc-ip=127.0.0.1                                          # 连接本地的 TongSim Unreal 运行所有测试脚本
uv run pytest tests/connection/test_grpc_connection.py                          # 运行指定文件
uv run pytest -k test_unary_api                                                 # 仅运行指定函数（支持模糊匹配）
```

---

如需了解更多测试技巧，可参考:

- [pytest 官方文档](https://docs.pytest.org/)
- [Python 测试实战书籍推荐](https://realpython.com/python-testing/)
