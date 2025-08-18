"""
logger.py

- 带前缀的日志格式: [TongSim][模块名] 消息
- 支持动态设置各个模块日志等级
- 统一日志文件输出
"""

import logging
from datetime import datetime
from pathlib import Path

__all__ = ["get_logger", "initialize_logger", "set_log_level"]


class _TongSimFormatter(logging.Formatter):
    """日志格式: [TongSim][模块名] 消息体"""

    def __init__(self, module_name: str):
        super().__init__()
        self.module_name = module_name

    def format(self, record: logging.LogRecord) -> str:
        try:
            msg = record.msg.format(*record.args)
        except Exception:
            msg = str(record.msg)
        record.getMessage = lambda: f"[TongSim][{self.module_name}] {msg}"
        return super().format(record)


class _LoggerManager:
    """内部日志管理器（模块内私有单例）"""

    def __init__(self):
        self._default_level: int = logging.WARNING
        self._loggers: dict[str, logging.Logger] = {}
        self._file_handler: logging.Handler | None = None

    def configure(
        self,
        level: int = logging.INFO,
        log_to_file: bool = False,
        log_dir: str = "logs",
    ):
        """初始化日志配置"""

        # 配置 logger 的等级
        self._default_level = level
        for module in self._loggers:
            self._loggers[module].setLevel(level)

        # 配置 logger 文件输出
        if log_to_file and self._file_handler is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            path = Path(log_dir)
            path.mkdir(parents=True, exist_ok=True)
            file_path = path / f"TongSim-{timestamp}.log"
            handler = logging.FileHandler(file_path, encoding="utf-8")
            handler.setFormatter(
                logging.Formatter("[{asctime}] [{levelname}] {message}", style="{")
            )
            self._file_handler = handler
            for logger in self._loggers.values():
                logger.addHandler(handler)

    def get_logger(self, module_name: str) -> logging.Logger:
        """获取指定模块的 logger 实例"""
        if module_name in self._loggers:
            return self._loggers[module_name]

        logger = logging.getLogger(f"TongSim.{module_name}")
        logger.propagate = False  #  logger 是“树结构”的, 这一步配置不往上传递
        logger.setLevel(self._default_level)

        # 控制台输出
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(_TongSimFormatter(module_name))
        logger.addHandler(stream_handler)

        # 文件输出
        if self._file_handler:
            logger.addHandler(self._file_handler)

        self._loggers[module_name] = logger
        return logger

    def set_module_level(self, module: str, level: int):
        """动态设置模块的日志等级"""
        if module in self._loggers:
            self._loggers[module].setLevel(level)
        else:
            raise ValueError(f"Logger for module '{module}' has not been created yet.")


# 私有单例实例
_logger_manager = _LoggerManager()

# ===== 公共接口 =====


def initialize_logger(
    level: int = logging.INFO, log_to_file: bool = False, log_dir: str = "logs"
):
    """
    配置日志默认等级和文件输出选项，应在程序入口调用一次。
    :param level: 默认日志等级（如 logging.INFO）
    :param log_to_file: 是否输出日志到文件
    :param log_dir: 日志文件目录，默认 logs/
    """
    _logger_manager.configure(level, log_to_file, log_dir)


def get_logger(module: str) -> logging.Logger:
    """
    获取模块 logger。日志前缀格式: [TongSim][模块名]
    :param module: 模块名字符串
    """
    return _logger_manager.get_logger(module)


def set_log_level(module: str, level: int):
    """
    设置指定模块的日志等级。
    :param module: 模块名字符串
    :param level: 日志等级，例如 logging.DEBUG、logging.ERROR
    """
    _logger_manager.set_module_level(module, level)
