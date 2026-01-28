"""
Core runtime module - 运行时依赖注入容器
"""
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from loguru import logger

if TYPE_CHECKING:
    from core.storage.cache.adapter import AdapterCache
    from core.storage.queue.adapter import AdapterQueue


class Runtime:
    """全局运行时容器，管理数据库、缓存、队列、日志等资源"""
    
    def __init__(self):
        self._db_engines: Dict[str, Any] = {}
        self._db_sessions: Dict[str, async_sessionmaker] = {}
        self._cache_clients: Dict[str, "AdapterCache"] = {}
        self._queue_clients: Dict[str, "AdapterQueue"] = {}
        self._logger = logger
        self._config: Optional[Dict[str, Any]] = None
        
    def set_config(self, config: Dict[str, Any]) -> None:
        """设置配置"""
        self._config = config
        
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return self._config or {}
        
    def set_db_engine(self, host: str, engine: Any) -> None:
        """设置数据库引擎"""
        self._db_engines[host] = engine
        
    def get_db_engine(self, host: str = "default"):
        """获取数据库引擎"""
        return self._db_engines.get(host)
        
    def set_db_session_maker(self, host: str, session_maker: async_sessionmaker) -> None:
        """设置数据库会话工厂"""
        self._db_sessions[host] = session_maker
        
    def get_db_session_maker(self, host: str = "default") -> async_sessionmaker:
        """获取数据库会话工厂"""
        return self._db_sessions.get(host)
        
    def set_cache_client(self, host: str, client: "AdapterCache") -> None:
        """设置缓存客户端"""
        self._cache_clients[host] = client
        
    def get_cache_client(self, host: str = "default") -> Optional["AdapterCache"]:
        """获取缓存客户端"""
        return self._cache_clients.get(host)
    
    def set_queue_client(self, host: str, client: "AdapterQueue") -> None:
        """设置队列客户端"""
        self._queue_clients[host] = client
    
    def get_queue_client(self, host: str = "default") -> Optional["AdapterQueue"]:
        """获取队列客户端"""
        return self._queue_clients.get(host)
        
    def get_logger(self):
        """获取日志器"""
        return self._logger
        
    async def close_all(self):
        """关闭所有资源"""
        for engine in self._db_engines.values():
            await engine.dispose()
        for client in self._cache_clients.values():
            await client.close()
        for client in self._queue_clients.values():
            await client.close()


# 全局运行时实例
runtime = Runtime()


async def get_db(host: str = "default"):
    """获取数据库会话（FastAPI Depends）"""
    session_maker = runtime.get_db_session_maker(host)
    if not session_maker:
        raise RuntimeError(f"Database session maker for '{host}' not initialized")
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_cache(host: str = "default") -> Optional["AdapterCache"]:
    """获取缓存适配器（FastAPI Depends）"""
    return runtime.get_cache_client(host)


async def get_queue(host: str = "default") -> Optional["AdapterQueue"]:
    """获取队列适配器（FastAPI Depends）"""
    return runtime.get_queue_client(host)


def get_logger():
    """获取日志器（FastAPI Depends）"""
    return runtime.get_logger()


def get_config() -> Dict[str, Any]:
    """获取配置（FastAPI Depends）"""
    return runtime.get_config()
