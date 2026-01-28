# 扩展配置使用说明

## 概述

dy-yun 支持扩展配置功能，允许在配置文件中添加自定义配置项，而无需修改核心配置模型。这个功能参考了 go-admin 的 ExtendConfig 设计。

## 特性

- **灵活扩展**：支持在配置文件中添加任意自定义字段
- **类型安全**：使用 Pydantic 模型验证
- **易于访问**：通过 `settings.extend` 直接访问
- **向后兼容**：不影响现有配置结构

## 配置示例

在配置文件中添加 `extend` 段：

```yaml
# config/settings.yaml 或 config/settings.dev.yaml

extend:
  # 高德地图配置
  amap:
    key: "your-amap-key"
    
  # 微信配置
  wechat:
    app_id: "wx1234567890"
    app_secret: "your-secret"
    
  # 阿里云配置
  aliyun:
    access_key_id: "your-access-key-id"
    access_key_secret: "your-secret"
    oss_endpoint: "oss-cn-hangzhou.aliyuncs.com"
    
  # 自定义配置
  custom:
    debug_mode: true
    feature_flags:
      - "experimental_feature_1"
      - "experimental_feature_2"
    max_upload_size: 10485760  # 10MB
```

## 使用方法

### 1. 基础访问

```python
from core import get_settings

settings = get_settings()

# 访问扩展配置
extend = settings.extend

# 获取配置值
amap_config = extend.amap
wechat_config = extend.wechat
custom_config = extend.custom
```

### 2. 安全访问（推荐）

```python
from core import get_settings

settings = get_settings()
extend = settings.extend

# 使用 hasattr 和 get 方法安全访问
if hasattr(extend, 'amap') and extend.amap:
    amap_key = extend.amap.get('key')
    print(f"高德地图 Key: {amap_key}")

if hasattr(extend, 'custom') and extend.custom:
    debug_mode = extend.custom.get('debug_mode', False)
    print(f"Debug Mode: {debug_mode}")
```

### 3. 在 FastAPI 中使用

```python
from fastapi import APIRouter, Depends
from core import get_settings, Settings

router = APIRouter()

@router.get("/amap/info")
async def get_amap_info(settings: Settings = Depends(get_settings)):
    """获取高德地图配置信息"""
    extend = settings.extend
    
    if hasattr(extend, 'amap') and extend.amap:
        return {
            "service": "amap",
            "configured": True,
            "key_length": len(extend.amap.get('key', ''))
        }
    
    return {"service": "amap", "configured": False}
```

### 4. 在服务层使用

```python
from core import get_settings

class MapService:
    """地图服务"""
    
    def __init__(self):
        settings = get_settings()
        self.extend = settings.extend
        
    def get_amap_key(self) -> str:
        """获取高德地图 Key"""
        if hasattr(self.extend, 'amap') and self.extend.amap:
            return self.extend.amap.get('key', '')
        return ''
    
    def geocode(self, address: str):
        """地理编码"""
        key = self.get_amap_key()
        if not key:
            raise ValueError("AMap key not configured")
        
        # 使用 key 调用高德地图 API
        # ...
        pass
```

### 5. 字典方式访问

```python
from core import get_settings

settings = get_settings()
extend = settings.extend

# 转换为字典
extend_dict = extend.model_dump()

# 遍历所有扩展配置
for key, value in extend_dict.items():
    if value is not None:
        print(f"{key}: {value}")
```

## 扩展配置类定义

如果需要更严格的类型验证，可以修改 `core/config/config.py` 中的 `ExtendConfig` 类：

```python
from typing import Optional, Dict, Any
from pydantic import BaseModel

class AMapConfig(BaseModel):
    """高德地图配置"""
    key: str
    secret: Optional[str] = None

class WeChatConfig(BaseModel):
    """微信配置"""
    app_id: str
    app_secret: str

class ExtendConfig(BaseModel):
    """扩展配置"""
    amap: Optional[AMapConfig] = None
    wechat: Optional[WeChatConfig] = None
    custom: Optional[Dict[str, Any]] = None
    
    class Config:
        extra = "allow"  # 允许额外字段
```

## 最佳实践

1. **分类组织**：按服务类型组织扩展配置（如 amap、wechat、aliyun）
2. **安全访问**：使用 `hasattr` 和 `get` 方法避免 KeyError
3. **默认值**：提供合理的默认值
4. **文档化**：在配置文件中添加注释说明
5. **环境区分**：在不同环境配置文件中设置不同的值

## 与 go-admin 的对比

| 特性 | go-admin | dy-yun |
|------|----------|--------|
| 配置注入 | `config.ExtendConfig = &ext.ExtConfig` | 通过 Settings 类自动加载 |
| 访问方式 | `config.ExtConfig.AMap.Key` | `settings.extend.amap['key']` |
| 类型检查 | 编译时检查 | Pydantic 运行时验证 |
| 灵活性 | 需要定义结构体 | 支持动态字段 |

## 注意事项

1. **性能考虑**：扩展配置在应用启动时一次性加载，不会影响运行时性能
2. **安全性**：敏感信息（如密钥）应通过环境变量或密钥管理服务管理
3. **验证**：Pydantic 会自动验证配置格式，错误会在启动时抛出
4. **热重载**：开发模式下修改配置文件会触发应用重启

## 示例项目

完整示例代码请参考：
- `examples/extend_config_example.py` - 基础使用示例
- `tests/test_extend_config.py` - 单元测试示例

---

更新时间：2026年1月27日
