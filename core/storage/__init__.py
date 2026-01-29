"""
Storage package - 存储管理包
"""
from core.storage.cache.adapter import AdapterCache
from core.storage.cache.memory import Memory as CacheMemory
from core.storage.cache.redis import Redis as CacheRedis
from core.storage.cache.cache import setup_cache, close_cache

from core.storage.queue.adapter import AdapterQueue, ConsumerFunc
from core.storage.queue.message import Message
from core.storage.queue.memory import Memory as QueueMemory
from core.storage.queue.redis import Redis as QueueRedis
from core.storage.queue.queue import setup_queue, close_queue

__all__ = [
    # Cache
    "AdapterCache",
    "CacheMemory",
    "CacheRedis",
    "setup_cache",
    "close_cache",
    # Queue
    "AdapterQueue",
    "ConsumerFunc",
    "Message",
    "QueueMemory",
    "QueueRedis",
    "setup_queue",
    "close_queue",
]
