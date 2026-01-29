"""
Configuration models - 配置模型
"""
from typing import List
from pydantic import BaseModel, Field


class ApplicationConfig(BaseModel):
    """应用配置"""
    name: str = "dy-yun"
    version: str = "0.1.0"
    mode: str = "dev"
    host: str = "0.0.0.0"
    port: int = 8000
    read_timeout: int = 60
    write_timeout: int = 60
    enable_dp: bool = True


class JWTConfig(BaseModel):
    """JWT 配置"""
    secret_key: str = "dy-yun-secret-key"
    timeout: int = 1440  # Token 过期时间（分钟）


class RateLimitConfig(BaseModel):
    """限流配置"""
    enabled: bool = False
    requests: int = 100
    window: int = 60
    use_redis: bool = False


class DatabaseConfig(BaseModel):
    """数据库配置"""
    driver: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    name: str = "dy_yun"
    username: str = ""
    password: str = ""
    source: str = "sqlite+aiosqlite:///./dy_yun.db"
    max_idle_conns: int = 10
    max_open_conns: int = 100
    conn_max_lifetime: int = 3600


class CacheConfig(BaseModel):
    """缓存配置"""
    driver: str = "memory"
    host: str = "localhost"
    port: int = 6379
    password: str = ""
    db: int = 0


class QueueConfig(BaseModel):
    """队列配置"""
    driver: str = "memory"  # redis, memory
    host: str = "localhost"
    port: int = 6379
    password: str = ""
    db: int = 0
    pool_num: int = 0  # 队列缓冲区大小，0 表示无限制
    consumer_group: str = "default_group"  # Redis 消费者组名称


class LogConfig(BaseModel):
    """日志配置"""
    level: str = "INFO"
    format: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    file: str = "logs/dy-yun.log"
    rotation: str = "500 MB"
    retention: str = "10 days"


class CORSConfig(BaseModel):
    """CORS 配置"""
    allow_origins: List[str] = Field(default_factory=lambda: ["*"])
    allow_credentials: bool = True
    allow_methods: List[str] = Field(default_factory=lambda: ["*"])
    allow_headers: List[str] = Field(default_factory=lambda: ["*"])


class SecurityConfig(BaseModel):
    """安全配置"""
    enable_https: bool = False
    ssl_keyfile: str = ""
    ssl_certfile: str = ""


class ExtendConfig(BaseModel):
    """扩展配置 - 支持自定义配置项"""
    class Config:
        extra = "allow"  # 允许任意额外字段
