"""
Memory Cache Adapter - 内存缓存适配器
"""
import asyncio
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from loguru import logger

from .adapter import AdapterCache


class CacheItem:
    """缓存项"""
    
    def __init__(self, value: str, expired: Optional[datetime] = None):
        self.value = value
        self.expired = expired
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expired is None:
            return False
        return datetime.now() >= self.expired


class Memory(AdapterCache):
    """内存缓存适配器"""
    
    def __init__(self):
        self._items: Dict[str, CacheItem] = {}
        self._lock = asyncio.Lock()
        logger.debug("Memory cache adapter initialized")
    
    def string(self) -> str:
        """返回适配器名称"""
        return "memory"
    
    async def _get_item(self, key: str) -> Optional[CacheItem]:
        """获取缓存项"""
        item = self._items.get(key)
        if item is None:
            return None
        
        if item.is_expired():
            # 过期则删除
            await self.delete(key)
            return None
        
        return item
    
    async def get(self, key: str) -> Optional[str]:
        """获取缓存值"""
        async with self._lock:
            item = await self._get_item(key)
            return item.value if item else None
    
    async def set(self, key: str, val: Any, expire: int = 0) -> None:
        """
        设置缓存值
        
        Args:
            key: 键
            val: 值
            expire: 过期时间（秒），0 表示永不过期
        """
        async with self._lock:
            value_str = str(val)
            expired = None
            if expire > 0:
                expired = datetime.now() + timedelta(seconds=expire)
            
            self._items[key] = CacheItem(value_str, expired)
    
    async def delete(self, key: str) -> None:
        """删除缓存键"""
        async with self._lock:
            self._items.pop(key, None)
    
    async def hash_get(self, hk: str, key: str) -> Optional[str]:
        """从哈希表获取值"""
        hash_key = f"{hk}:{key}"
        return await self.get(hash_key)
    
    async def hash_set(self, hk: str, key: str, val: Any) -> None:
        """设置哈希表值"""
        hash_key = f"{hk}:{key}"
        # 哈希表项默认不过期
        await self.set(hash_key, val, expire=0)
    
    async def hash_delete(self, hk: str, key: str) -> None:
        """删除哈希表键"""
        hash_key = f"{hk}:{key}"
        await self.delete(hash_key)
    
    async def increase(self, key: str) -> int:
        """递增计数器"""
        async with self._lock:
            item = await self._get_item(key)
            if item is None:
                raise KeyError(f"Key '{key}' does not exist")
            
            try:
                current_value = int(item.value)
            except ValueError:
                raise ValueError(f"Value of '{key}' is not an integer")
            
            new_value = current_value + 1
            item.value = str(new_value)
            return new_value
    
    async def decrease(self, key: str) -> int:
        """递减计数器"""
        async with self._lock:
            item = await self._get_item(key)
            if item is None:
                raise KeyError(f"Key '{key}' does not exist")
            
            try:
                current_value = int(item.value)
            except ValueError:
                raise ValueError(f"Value of '{key}' is not an integer")
            
            new_value = current_value - 1
            item.value = str(new_value)
            return new_value
    
    async def expire(self, key: str, duration: timedelta) -> None:
        """设置键的过期时间"""
        async with self._lock:
            item = await self._get_item(key)
            if item is None:
                raise KeyError(f"Key '{key}' does not exist")
            
            item.expired = datetime.now() + duration
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        async with self._lock:
            item = await self._get_item(key)
            return item is not None
    
    async def close(self) -> None:
        """关闭连接（内存缓存无需关闭）"""
        async with self._lock:
            self._items.clear()
        logger.debug("Memory cache cleared")
