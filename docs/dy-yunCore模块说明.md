# Core 模块重构说明

## 概述
参考 go-admin-core 的包结构，将 dy-yun 的 core 模块拆分为多个子包，提高代码的可维护性和模块化程度。

## 新的包结构

```
core/
├── __init__.py              # 核心包入口，导出所有公共接口
├── config/                  # 配置管理包
│   ├── __init__.py
│   ├── models.py           # 配置模型定义
│   └── loader.py           # 配置加载器
├── database/               # 数据库管理包
│   ├── __init__.py
│   ├── base.py            # SQLAlchemy Base 类
│   └── database.py        # 数据库初始化和连接管理
├── cache/                 # 缓存管理包
│   ├── __init__.py
│   └── cache.py          # 缓存适配器（支持 Redis/Memory）
├── logger/               # 日志管理包
│   ├── __init__.py
│   └── logger.py        # 日志配置和初始化
├── errors/              # 错误和异常包
│   ├── __init__.py
│   └── exceptions.py   # 自定义异常类
└── runtime/            # 运行时容器包
    ├── __init__.py
    └── runtime.py     # 全局运行时依赖注入容器

```

## 变更内容

### 1. 配置管理 (config/)
- **models.py**: 包含所有配置模型
  - `DatabaseConfig` - 数据库配置
  - `CacheConfig` - 缓存配置
  - `ApplicationConfig` - 应用配置
  - `JWTConfig` - JWT 配置
  - `LogConfig` - 日志配置
  - `CORSConfig` - CORS 配置
  - `SecurityConfig` - 安全配置

- **loader.py**: 配置加载逻辑
  - `Settings` - 全局配置类
  - `load_config()` - 从文件加载配置
  - `get_settings()` - 获取配置单例
  - `set_config_path()` - 设置配置文件路径

### 2. 数据库管理 (database/)
- **base.py**: SQLAlchemy 声明式基类
  - `Base` - 所有数据库模型的基类

- **database.py**: 数据库连接和初始化
  - `setup_database()` - 初始化数据库连接
  - `create_tables()` - 创建数据库表
  - `close_database()` - 关闭数据库连接

### 3. 缓存管理 (cache/)
- **cache.py**: 缓存适配器
  - `setup_cache()` - 初始化缓存（支持 Redis/Memory）
  - `close_cache()` - 关闭缓存连接

### 4. 日志管理 (logger/)
- **logger.py**: 日志系统
  - `setup_logger()` - 配置日志系统
  - `get_request_logger()` - 获取带请求 ID 的日志器

### 5. 错误处理 (errors/)
- **exceptions.py**: 自定义异常
  - `APIException` - API 异常基类
  - `AuthenticationError` - 认证错误
  - `PermissionDenied` - 权限拒绝
  - `NotFound` - 资源未找到
  - `ValidationError` - 验证错误
  - `DatabaseError` - 数据库错误

### 6. 运行时容器 (runtime/)
- **runtime.py**: 全局运行时容器
  - `Runtime` - 运行时容器类
  - `runtime` - 全局运行时实例
  - `get_db()` - 获取数据库会话（FastAPI Depends）
  - `get_cache()` - 获取缓存客户端
  - `get_logger()` - 获取日志器
  - `get_config()` - 获取配置

## 导入方式

### 从顶层 core 包导入（推荐）
```python
from core import (
    Settings, get_settings,                    # 配置
    Base, setup_database, create_tables,       # 数据库
    setup_cache, close_cache,                  # 缓存
    setup_logger, get_request_logger,          # 日志
    APIException, NotFound, ValidationError,   # 异常
    runtime, get_db, get_cache, get_logger,   # 运行时
)
```

### 从子包导入
```python
from core.config import Settings, DatabaseConfig, CacheConfig
from core.database import Base, setup_database
from core.cache import setup_cache
from core.logger import setup_logger
from core.errors import APIException, NotFound
from core.runtime import runtime, get_db
```

## 迁移指南

### 1. 更新导入语句
将旧的导入：
```python
from core.exceptions import APIException  # 旧
```

更新为：
```python
from core.errors import APIException      # 新
```

### 2. Base 类导入
将旧的导入：
```python
from core.runtime import Base  # 旧
```

更新为：
```python
from core.database import Base  # 新
# 或者
from core import Base  # 也可以
```

## 优势

1. **更好的代码组织**: 每个功能模块独立成包，职责清晰
2. **易于维护**: 相关代码聚合在一起，便于查找和修改
3. **可扩展性**: 可以轻松添加新的子包（如 storage、server 等）
4. **符合最佳实践**: 参考了成熟的 go-admin-core 架构
5. **向后兼容**: 通过 `core/__init__.py` 维持原有的导入接口

## 已删除的文件

以下文件已被拆分到对应的子包中：
- `core/config.py` → `core/config/`
- `core/database.py` → `core/database/`
- `core/cache.py` → `core/cache/`
- `core/logger.py` → `core/logger/`
- `core/exceptions.py` → `core/errors/`
- `core/runtime.py` → `core/runtime/`

## 测试验证

所有核心功能已通过导入测试：
```bash
# 测试核心导入
python -c "from core import Settings, Base, runtime; print('✓ OK')"

# 测试子包导入
python -c "from core.config import Settings; from core.database import Base; print('✓ OK')"

# 测试模型导入
python -c "from common.base.model import BaseModel; print('✓ OK')"

# 测试主程序导入
python -c "from main import *; print('✓ OK')"
```

## 后续计划

可以根据需要继续添加以下子包（参考 go-admin-core）：
- `storage/` - 存储管理（文件存储、对象存储等）
- `queue/` - 消息队列
- `locker/` - 分布式锁
- `server/` - 服务器相关工具

---
重构完成时间：2026年1月27日
