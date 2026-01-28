"""
Logger setup - 日志配置
"""
from loguru import logger
import sys
from pathlib import Path

from core.config.config import LogConfig


def setup_logger(config: LogConfig) -> None:
    """配置日志系统"""
    logger.remove()
    logger.add(sys.stdout, format=config.format, level=config.level, colorize=True)
    if config.file:
        log_path = Path(config.file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            config.file,
            format=config.format,
            level=config.level,
            rotation=config.rotation,
            retention=config.retention,
            compression="zip",
            encoding="utf-8",
        )
    logger.info(f"Logger initialized: level={config.level}")


def get_request_logger(request_id: str = ""):
    """获取带请求 ID 的日志器"""
    if request_id:
        return logger.bind(request_id=request_id)
    return logger
