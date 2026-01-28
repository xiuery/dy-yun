"""
Cache Adapter - 缓存适配器接口
"""
from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import timedelta


class AdapterCache(ABC):
    """缓存适配器抽象基类"""
    
    @abstractmethod
    def string(self) -> str:
        """返回适配器名称"""
        pass
    
    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """获取缓存值"""
        pass
    
    @abstractmethod
    async def set(self, key: str, val: Any, expire: int = 0) -> None:
        """
        设置缓存值
        
        Args:
            key: 键
            val: 值
            expire: 过期时间（秒），0 表示永不过期
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """删除缓存键"""
        pass
    
    @abstractmethod
    async def hash_get(self, hk: str, key: str) -> Optional[str]:
        """从哈希表获取值"""
        pass
    
    @abstractmethod
    async def hash_set(self, hk: str, key: str, val: Any) -> None:
        """设置哈希表值"""
        pass
    
    @abstractmethod
    async def hash_delete(self, hk: str, key: str) -> None:
        """删除哈希表键"""
        pass
    
    @abstractmethod
    async def increase(self, key: str) -> int:
        """递增计数器"""
        pass
    
    @abstractmethod
    async def decrease(self, key: str) -> int:
        """递减计数器"""
        pass
    
    @abstractmethod
    async def expire(self, key: str, duration: timedelta) -> None:
        """设置键的过期时间"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """关闭连接"""
        pass
