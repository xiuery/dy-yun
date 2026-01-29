"""
Redis Cache Adapter - Redis缓存适配器
"""
from datetime import timedelta
from typing import Any, Optional, Union
from redis import asyncio as aioredis
from loguru import logger

from .adapter import AdapterCache


class Redis(AdapterCache):
    """Redis缓存适配器"""
    
    def __init__(self, client: aioredis.Redis):
        """
        初始化Redis适配器
        
        Args:
            client: aioredis客户端实例
        """
        self.client = client
        logger.debug("Redis cache adapter initialized")
    
    @classmethod
    async def create(
        cls,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        **kwargs
    ) -> "Redis":
        """
        创建Redis适配器实例
        
        Args:
            host: Redis主机
            port: Redis端口
            db: 数据库编号
            password: 密码
            **kwargs: 其他redis连接参数
        """
        client = await aioredis.from_url(
            f"redis://{host}:{port}/{db}",
            password=password if password else None,
            encoding="utf-8",
            decode_responses=True,
            **kwargs
        )
        
        # 测试连接
        await client.ping()
        logger.success(f"Redis connected: {host}:{port}/{db}")
        
        return cls(client)
    
    def string(self) -> str:
        """返回适配器名称"""
        return "redis"
    
    async def get(self, key: str) -> Optional[str]:
        """获取缓存值"""
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    async def set(self, key: str, val: Any, expire: int = 0) -> None:
        """
        设置缓存值
        
        Args:
            key: 键
            val: 值
            expire: 过期时间（秒），0 表示永不过期
        """
        try:
            if expire > 0:
                await self.client.setex(key, expire, str(val))
            else:
                await self.client.set(key, str(val))
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            raise
    
    async def delete(self, key: str) -> None:
        """删除缓存键"""
        try:
            await self.client.delete(key)
        except Exception as e:
            logger.error(f"Redis DEL error: {e}")
            raise
    
    async def hash_get(self, hk: str, key: str) -> Optional[str]:
        """从哈希表获取值"""
        try:
            return await self.client.hget(hk, key)
        except Exception as e:
            logger.error(f"Redis HGET error: {e}")
            return None
    
    async def hash_set(self, hk: str, key: str, val: Any) -> None:
        """设置哈希表值"""
        try:
            await self.client.hset(hk, key, str(val))
        except Exception as e:
            logger.error(f"Redis HSET error: {e}")
            raise
    
    async def hash_delete(self, hk: str, key: str) -> None:
        """删除哈希表键"""
        try:
            await self.client.hdel(hk, key)
        except Exception as e:
            logger.error(f"Redis HDEL error: {e}")
            raise
    
    async def increase(self, key: str) -> int:
        """递增计数器"""
        try:
            return await self.client.incr(key)
        except Exception as e:
            logger.error(f"Redis INCR error: {e}")
            raise
    
    async def decrease(self, key: str) -> int:
        """递减计数器"""
        try:
            return await self.client.decr(key)
        except Exception as e:
            logger.error(f"Redis DECR error: {e}")
            raise
    
    async def expire(self, key: str, duration: Union[int, timedelta]) -> None:
        """
        设置键的过期时间
        
        Args:
            key: 键
            duration: 过期时间（秒数或timedelta对象）
        """
        try:
            if isinstance(duration, timedelta):
                seconds = int(duration.total_seconds())
            else:
                seconds = int(duration)
            await self.client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis EXPIRE error: {e}")
            raise
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error: {e}")
            return False
    
    # ========== Sorted Set 操作 ==========
    
    async def zremrangebyscore(self, key: str, min_score: float, max_score: float) -> int:
        """
        移除有序集合中指定分数区间的成员
        
        Args:
            key: 键
            min_score: 最小分数
            max_score: 最大分数
            
        Returns:
            删除的成员数量
        """
        try:
            return await self.client.zremrangebyscore(key, min_score, max_score)
        except Exception as e:
            logger.error(f"Redis ZREMRANGEBYSCORE error: {e}")
            raise
    
    async def zcard(self, key: str) -> int:
        """
        获取有序集合的成员数量
        
        Args:
            key: 键
            
        Returns:
            成员数量
        """
        try:
            return await self.client.zcard(key)
        except Exception as e:
            logger.error(f"Redis ZCARD error: {e}")
            raise
    
    async def zrange(self, key: str, start: int, end: int, withscores: bool = False):
        """
        获取有序集合指定范围内的成员
        
        Args:
            key: 键
            start: 起始索引
            end: 结束索引
            withscores: 是否返回分数
            
        Returns:
            成员列表或(成员,分数)元组列表
        """
        try:
            return await self.client.zrange(key, start, end, withscores=withscores)
        except Exception as e:
            logger.error(f"Redis ZRANGE error: {e}")
            raise
    
    async def zadd(self, key: str, mapping: dict) -> int:
        """
        向有序集合添加成员
        
        Args:
            key: 键
            mapping: {成员: 分数} 字典
            
        Returns:
            添加的成员数量
        """
        try:
            return await self.client.zadd(key, mapping)
        except Exception as e:
            logger.error(f"Redis ZADD error: {e}")
            raise
    
    async def close(self) -> None:
        """关闭连接"""
        try:
            await self.client.close()
            logger.debug("Redis connection closed")
        except Exception as e:
            logger.error(f"Redis close error: {e}")
    
    def get_client(self) -> aioredis.Redis:
        """获取原生Redis客户端（用于高级操作）"""
        return self.client
