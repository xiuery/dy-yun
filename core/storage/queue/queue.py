"""
Queue Factory - 队列工厂函数
"""
from typing import Optional
from loguru import logger
from core.config import QueueConfig
from core.runtime import runtime

from .adapter import AdapterQueue
from .memory import Memory
from .redis import Redis


async def setup_queue(
    config: QueueConfig,
    host: str = "default"
) -> AdapterQueue:
    """
    根据配置创建队列适配器
    
    Args:
        config: 队列配置对象
        host: 队列标识名称
        
    Returns:
        AdapterQueue: 队列适配器实例
        
    Raises:
        ValueError: 不支持的队列驱动类型
    """
    driver = config.driver.lower()
    
    logger.debug(f"Initializing {driver} queue adapter: {host}")
    
    if driver == "memory":
        adapter = Memory(pool_num=getattr(config, "pool_num", 0))
    
    elif driver == "redis":
        adapter = await Redis.create(
            host=config.host,
            port=config.port,
            db=config.db,
            password=config.password or None,
            consumer_group=getattr(config, "consumer_group", "default_group")
        )
    
    else:
        raise ValueError(f"Unsupported queue driver: {driver}")
    
    # 保存到运行时容器
    runtime.set_queue_client(host, adapter)
    
    logger.info(f"Queue adapter '{driver}' initialized: {host}")
    return adapter


async def close_queue(host: str = "default") -> None:
    """
    关闭指定的队列适配器
    
    Args:
        host: 队列标识名称
    """
    adapter = runtime.get_queue_client(host)
    if adapter:
        await adapter.close()
        logger.info(f"Queue adapter closed: {host}")
