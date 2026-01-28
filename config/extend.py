"""
项目扩展配置定义
Project Extend Configuration

此文件用于定义项目特定的扩展配置结构。
核心库（core）中的 ExtendConfig 支持任意字段，
此文件提供项目级别的配置示例和类型定义。

使用方法：
1. 在此文件中定义项目需要的扩展配置类
2. 在配置文件 settings.yaml 中添加对应的 extend 段
3. 通过 settings.extend 访问配置

示例：
    from core import get_settings
    
    settings = get_settings()
    if hasattr(settings.extend, 'amap') and settings.extend.amap:
        amap_key = settings.extend.amap.get('key')
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class AMapConfig(BaseModel):
    """高德地图配置"""
    key: str
    secret: Optional[str] = None


class WeChatConfig(BaseModel):
    """微信配置"""
    app_id: str
    app_secret: str
    token: Optional[str] = None
    encoding_aes_key: Optional[str] = None


class AliyunConfig(BaseModel):
    """阿里云配置"""
    access_key_id: str
    access_key_secret: str
    oss_endpoint: Optional[str] = None
    oss_bucket: Optional[str] = None


# 扩展配置示例
# 可以在配置文件中使用以下结构：
"""
extend:
  amap:
    key: "your-amap-key"
    
  wechat:
    app_id: "wx1234567890"
    app_secret: "your-secret"
    
  aliyun:
    access_key_id: "your-access-key-id"
    access_key_secret: "your-secret"
    oss_endpoint: "oss-cn-hangzhou.aliyuncs.com"
    oss_bucket: "my-bucket"
    
  custom:
    feature_flags:
      - "feature_a"
      - "feature_b"
    max_upload_size: 10485760
"""


def get_amap_key() -> Optional[str]:
    """获取高德地图 Key（便捷方法）"""
    from core import get_settings
    settings = get_settings()
    if hasattr(settings.extend, 'amap') and settings.extend.amap:
        return settings.extend.amap.get('key')
    return None


def get_wechat_config() -> Optional[Dict[str, Any]]:
    """获取微信配置（便捷方法）"""
    from core import get_settings
    settings = get_settings()
    if hasattr(settings.extend, 'wechat') and settings.extend.wechat:
        return settings.extend.wechat
    return None


def get_custom_config(key: str, default: Any = None) -> Any:
    """获取自定义配置（便捷方法）"""
    from core import get_settings
    settings = get_settings()
    if hasattr(settings.extend, 'custom') and settings.extend.custom:
        return settings.extend.custom.get(key, default)
    return default
