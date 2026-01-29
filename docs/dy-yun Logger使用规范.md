# dy-yun Logger 使用规范

## 项目架构分析

### 日志系统架构

```
core/logger/
├── logger.py          # 核心日志配置
└── __init__.py        # 导出接口

使用场景：
├── 中间件层 (common/middleware/)    # 请求日志、错误日志
├── 服务层 (common/services/)        # 业务逻辑日志
├── 存储层 (core/storage/)           # 基础设施日志
└── 路由层 (app/*/routers/)          # API 调用日志
```

### 当前日志实现

**基于 Loguru** - 简单、强大的Python日志库

**核心函数：**
1. `setup_logger(config)` - 初始化日志系统
2. `get_request_logger(request_id)` - 获取带请求ID的日志器

---

## 使用规范

### 1. **中间件层** - 使用 `get_request_logger()`

中间件需要记录请求上下文，**必须**使用带request_id的logger。

```python
# ✅ 正确示例
from core.logger import get_request_logger

async def some_middleware(request: Request, call_next):
    request_id = getattr(request.state, "request_id", "")
    logger = get_request_logger(request_id)
    
    logger.info(f"→ {request.method} {request.url.path}")
    logger.error(f"Error occurred: {error}")
    logger.warning(f"Suspicious activity detected")
```

**应用场景：**
- `common/middleware/logger.py` - 请求日志
- `common/middleware/error_handler.py` - 错误处理
- `common/middleware/auth.py` - 认证日志
- `common/middleware/rate_limit.py` - 限流日志

---

### 2. **服务层/业务层** - 混合使用

业务逻辑层可能需要记录请求上下文，也可能是后台任务。

#### 2.1 有请求上下文时

```python
# ✅ 正确示例 - 在请求处理中
from core.logger import get_request_logger

class SomeService:
    async def process(self, request: Request):
        request_id = getattr(request.state, "request_id", "")
        logger = get_request_logger(request_id)
        
        logger.info("Processing business logic")
        logger.error("Business error occurred", exc_info=True)
```

#### 2.2 无请求上下文时（后台任务、定时任务）

```python
# ✅ 正确示例 - 后台任务
from loguru import logger

async def background_task():
    logger.info("Background task started")
    logger.success("Task completed successfully")
    logger.error("Task failed", exc_info=True)
```

---

### 3. **基础设施层** - 使用 `from loguru import logger`

基础设施组件（数据库、缓存、队列等）不涉及HTTP请求，直接使用loguru。

```python
# ✅ 正确示例 - Redis缓存
from loguru import logger

class Redis:
    async def connect(self):
        logger.info(f"Redis connected: {host}:{port}")
        logger.error(f"Redis connection failed: {e}")
        logger.debug("Redis operation details")
        logger.success("Redis setup complete")
```

**应用场景：**
- `core/storage/cache/redis.py` - 缓存日志
- `core/storage/queue/redis.py` - 队列日志
- `core/database/database.py` - 数据库日志
- `core/config/loader.py` - 配置加载日志

---

## 日志级别使用指南

### 级别定义

| 级别 | 使用场景 | 示例 |
|------|---------|------|
| **DEBUG** | 调试信息，开发环境使用 | `logger.debug("Variable value: {var}")` |
| **INFO** | 常规信息，记录流程 | `logger.info("User logged in")` |
| **SUCCESS** | 成功操作（Loguru特有） | `logger.success("Database connected")` |
| **WARNING** | 警告，不影响运行但需注意 | `logger.warning("Redis fallback to memory")` |
| **ERROR** | 错误，需要关注和处理 | `logger.error("Database query failed")` |
| **CRITICAL** | 严重错误，系统可能崩溃 | `logger.critical("System shutdown")` |

### 使用建议

#### ✅ 正确使用

```python
# 1. 记录异常堆栈
logger.error("Database error", exc_info=True)

# 2. 结构化日志
logger.info(f"User {user_id} performed action {action}")

# 3. 关键操作成功
logger.success("Payment transaction completed")

# 4. 降级提示
logger.warning("Redis unavailable, fallback to memory")

# 5. 调试信息
logger.debug(f"Query params: {params}")
```

#### ❌ 错误使用

```python
# ❌ 不要使用 print
print("This is a log message")  # 错误！

# ❌ 不要记录敏感信息
logger.info(f"User password: {password}")  # 危险！

# ❌ 不要在循环中大量记录DEBUG
for item in large_list:
    logger.debug(f"Processing {item}")  # 性能问题！

# ❌ 不要吞掉异常
try:
    risky_operation()
except:
    pass  # 错误！应该记录日志
```

---

## 项目中的实际应用

### 当前使用模式分析

#### ✅ 良好实践

1. **中间件统一使用 get_request_logger**
   ```python
   # common/middleware/logger.py
   logger = get_request_logger(request_id)
   logger.info(f"→ {request.method} {request.url.path}")
   ```

2. **错误处理记录完整堆栈**
   ```python
   # common/middleware/error_handler.py
   logger.exception(f"Unhandled exception: {str(e)}")
   ```

3. **基础设施使用直接导入**
   ```python
   # core/storage/cache/redis.py
   from loguru import logger
   logger.success(f"Redis connected: {host}:{port}/{db}")
   ```

#### ⚠️ 需要改进的地方

1. **混合使用问题**
   ```python
   # ❌ 当前：common/middleware/handler/auth.py
   from core.logger import get_request_logger
   
   async def authenticator(request: Request):
       logger = get_request_logger()  # ✅ 已修复
       logger.error(f"Authentication error: {e}", exc_info=True)
   ```

2. **缺少结构化日志**
   ```python
   # ⚠️ 可以改进
   logger.info("User logged in")
   
   # ✅ 更好的方式
   logger.bind(user_id=user_id, action="login").info("User logged in")
   ```

---

## 标准模板

### 中间件模板

```python
from core.logger import get_request_logger
from fastapi import Request

async def my_middleware(request: Request, call_next):
    request_id = getattr(request.state, "request_id", "")
    logger = get_request_logger(request_id)
    
    try:
        logger.info(f"Middleware started: {request.url.path}")
        response = await call_next(request)
        logger.info(f"Middleware completed: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Middleware error: {e}", exc_info=True)
        raise
```

### 服务层模板

```python
from core.logger import get_request_logger

class MyService:
    async def process(self, request: Request, data: dict):
        request_id = getattr(request.state, "request_id", "")
        logger = get_request_logger(request_id)
        
        try:
            logger.info(f"Service processing started")
            result = await self._do_work(data)
            logger.success(f"Service completed successfully")
            return result
        except Exception as e:
            logger.error(f"Service error: {e}", exc_info=True)
            raise
```

### 基础设施模板

```python
from loguru import logger

class MyInfrastructure:
    async def initialize(self):
        try:
            logger.info("Initializing infrastructure")
            await self._setup()
            logger.success("Infrastructure ready")
        except Exception as e:
            logger.error(f"Infrastructure failed: {e}", exc_info=True)
            raise
```

---

## 配置说明

### logger.py 配置

```python
from loguru import logger
import sys

def setup_logger(config: LogConfig):
    logger.remove()  # 移除默认处理器
    
    # 控制台输出
    logger.add(
        sys.stdout,
        format=config.format,
        level=config.level,
        colorize=True  # 彩色输出
    )
    
    # 文件输出
    if config.file:
        logger.add(
            config.file,
            format=config.format,
            level=config.level,
            rotation="100 MB",      # 文件大小轮转
            retention="30 days",    # 保留时间
            compression="zip",      # 压缩归档
            encoding="utf-8"
        )
```

### 环境配置

```yaml
# config/settings.dev.yaml
logger:
  level: DEBUG          # 开发环境：详细日志
  file: logs/dev.log
  
# config/settings.yaml
logger:
  level: INFO           # 生产环境：关键日志
  file: logs/app.log
  rotation: "100 MB"
  retention: "30 days"
```

---

## 最佳实践总结

### DO ✅

1. **中间件层必须使用 `get_request_logger(request_id)`**
2. **基础设施层直接 `from loguru import logger`**
3. **记录错误时使用 `exc_info=True` 保留堆栈**
4. **使用合适的日志级别（DEBUG/INFO/ERROR等）**
5. **记录关键业务操作和状态变更**
6. **生产环境设置 INFO 级别，开发环境 DEBUG**

### DON'T ❌

1. **不要使用 `print()` 输出日志**
2. **不要记录敏感信息（密码、token等）**
3. **不要在热路径中记录大量DEBUG日志**
4. **不要吞掉异常不记录**
5. **不要在基础设施层使用 `get_request_logger()`**
6. **不要忘记清理调试日志**

---

## 快速检查清单

开发时自查：

- [ ] 中间件使用了 `get_request_logger(request_id)` 吗？
- [ ] 异常处理添加了 `exc_info=True` 吗？
- [ ] 敏感信息被过滤了吗？
- [ ] 日志级别设置合理吗？
- [ ] 基础设施层避免使用request logger了吗？
- [ ] 生产环境配置为 INFO 级别了吗？

---

## 工具和辅助

### 日志查看命令

```bash
# 实时查看日志
tail -f logs/app.log

# 过滤错误日志
grep "ERROR" logs/app.log

# 查找特定请求
grep "request_id=xxx" logs/app.log

# 统计错误数量
grep -c "ERROR" logs/app.log
```

### 性能监控

```python
# 添加性能日志
import time

start = time.time()
await expensive_operation()
elapsed = time.time() - start
logger.info(f"Operation took {elapsed:.3f}s")
```

---

## 参考资源

- [Loguru 官方文档](https://loguru.readthedocs.io/)
- [Python Logging 最佳实践](https://docs.python.org/3/howto/logging.html)
- 项目文件：`core/logger/logger.py`
- 中间件示例：`common/middleware/logger.py`
