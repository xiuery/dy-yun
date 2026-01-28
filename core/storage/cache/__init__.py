"""
Cache package - 缓存管理包
"""
from core.storage.cache.adapter import AdapterCache
from core.storage.cache.memory import Memory
from core.storage.cache.redis import Redis
from core.storage.cache.cache import setup_cache, close_cache

__all__ = [
    "AdapterCache",
    "Memory",
    "Redis",
    "setup_cache",
    "close_cache",
]
