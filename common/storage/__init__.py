"""
Common Storage Package - 存储组件包
"""
from common.storage.initialize import (
    setup_storage,
    setup_cache_adapter,
    setup_queue_adapter,
    close_storage,
)

__all__ = [
    "setup_storage",
    "setup_cache_adapter",
    "setup_queue_adapter",
    "close_storage",
]
