"""
Storage Initializer - 存储组件初始化器
"""
from loguru import logger
from core.config import Settings
from core.storage import setup_cache, setup_queue
from core.runtime import runtime


async def setup_storage(settings: Settings) -> None:
    """
    初始化所有存储组件
    
    Args:
        settings: 应用配置
    """
    await setup_cache_adapter(settings)
    await setup_queue_adapter(settings)


async def setup_cache_adapter(settings: Settings) -> None:
    """
    初始化缓存适配器
    
    Args:
        settings: 应用配置
    """
    try:
        cache_adapter = await setup_cache(settings.cache, host="default")
        logger.success(f"Cache adapter initialized: {cache_adapter.string()}")
    except Exception as e:
        logger.error(f"Cache setup error: {e}")
        raise


async def setup_queue_adapter(settings: Settings) -> None:
    """
    初始化队列适配器
    
    Args:
        settings: 应用配置
    """
    try:
        queue_adapter = await setup_queue(settings.queue, host="default")
        logger.success(f"Queue adapter initialized: {queue_adapter.string()}")
        
        # 在后台运行队列消费者
        import asyncio
        asyncio.create_task(queue_adapter.run(), name="queue_runner")
        logger.info("Queue consumer started in background")
        
    except Exception as e:
        logger.error(f"Queue setup error: {e}")
        # 队列初始化失败不应该阻止应用启动
        logger.warning("Application will continue without queue support")


async def close_storage() -> None:
    """关闭所有存储组件"""
    # 获取缓存适配器并关闭
    cache = runtime.get_cache_client("default")
    if cache:
        await cache.close()
        logger.info("Cache adapter closed")
    
    # 获取队列适配器并关闭
    queue = runtime.get_queue_client("default")
    if queue:
        await queue.shutdown()
        await queue.close()
        logger.info("Queue adapter closed")
