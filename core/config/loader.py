"""
Configuration loader - 配置加载器
"""
import os
from typing import Optional
from pathlib import Path
import yaml
from pydantic import Field
from pydantic_settings import BaseSettings

from core.config.config import (
    ApplicationConfig,
    JWTConfig,
    RateLimitConfig,
    DatabaseConfig,
    CacheConfig,    QueueConfig,    QueueConfig,
    LogConfig,
    CORSConfig,
    SecurityConfig,
    ExtendConfig,
)


class Settings(BaseSettings):
    """全局配置"""
    application: ApplicationConfig = Field(default_factory=ApplicationConfig)
    jwt: JWTConfig = Field(default_factory=JWTConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    queue: QueueConfig = Field(default_factory=QueueConfig)
    log: LogConfig = Field(default_factory=LogConfig)
    cors: CORSConfig = Field(default_factory=CORSConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    extend: ExtendConfig = Field(default_factory=ExtendConfig)
    
    class Config:
        env_prefix = ""
        case_sensitive = False


def load_config(config_path: str = "config/settings.yaml") -> Settings:
    """加载配置文件"""
    config_file = Path(config_path)
    if not config_file.exists():
        print(f"Warning: Config file {config_path} not found, using defaults")
        return Settings()
    with open(config_file, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    return Settings(**config_data)


settings: Optional[Settings] = None
config_file_path: str = "config/settings.yaml"


def set_config_path(path: str) -> None:
    """设置配置文件路径"""
    global config_file_path, settings
    config_file_path = path
    settings = None  # 重置配置单例，强制重新加载


def get_settings() -> Settings:
    """获取配置单例"""
    global settings
    if settings is None:
        # 优先从环境变量读取配置路径（支持 reload 模式）
        config_path = os.environ.get("DY_YUN_CONFIG_FILE", config_file_path)
        settings = load_config(config_path)
    return settings
