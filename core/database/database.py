"""
Database initialization - 数据库初始化
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from loguru import logger

from core.config.config import DatabaseConfig


async def setup_database(config: DatabaseConfig, host: str = "default") -> None:
    """初始化数据库连接"""
    from core.runtime import runtime
    
    logger.info(f"Initializing database: {host} => {config.source}")
    engine = create_async_engine(
        config.source,
        echo=config.driver == "sqlite",
        pool_size=config.max_idle_conns,
        max_overflow=config.max_open_conns - config.max_idle_conns,
        pool_recycle=config.conn_max_lifetime,
        pool_pre_ping=True,
    )
    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    runtime.set_db_engine(host, engine)
    runtime.set_db_session_maker(host, session_maker)
    logger.success(f"Database {host} connected successfully")


async def create_tables():
    """创建所有表"""
    from core.runtime import runtime
    from core.database.base import Base
    
    engine = runtime.get_db_engine("default")
    if not engine:
        logger.error("Database engine not initialized")
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


async def close_database():
    """关闭数据库连接"""
    from core.runtime import runtime
    
    await runtime.close_all()
    logger.info("Database connections closed")
