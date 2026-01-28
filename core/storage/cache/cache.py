"""
Cache adapter - 缓存适配器
"""
from typing import Optional
from loguru import logger

from core.config.config import CacheConfig
from .adapter import AdapterCache
from .memory import Memory
from .redis import Redis


async def setup_cache(config: CacheConfig, host: str = "default") -> AdapterCache:
    """
    初始化缓存
    
    Args:
        config: 缓存配置
        host: 缓存实例名称
        
    Returns:
        AdapterCache: 缓存适配器实例
    """
    from core.runtime import runtime
    
    adapter: Optional[AdapterCache] = None
    
    if config.driver == "memory":
        logger.info("Initializing memory cache adapter")
        adapter = Memory()
        
    elif config.driver == "redis":
        logger.info(f"Initializing Redis cache: {config.host}:{config.port}")
        try:
            adapter = await Redis.create(
                host=config.host,
                port=config.port,
                db=config.db,
                password=config.password if config.password else None,
            )
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    else:
        raise ValueError(f"Unsupported cache driver: {config.driver}")
    
    # 保存到 runtime
    runtime.set_cache_client(host, adapter)
    logger.success(f"Cache adapter '{adapter.string()}' initialized: {host}")
    
    return adapter


async def close_cache():
    """关闭所有缓存连接"""
    from core.runtime import runtime
    
    await runtime.close_all()
