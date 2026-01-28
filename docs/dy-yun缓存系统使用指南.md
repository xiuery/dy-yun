# 缓存系统使用指南

## 概述

dy-yun 的缓存系统参考 go-admin-core/storage/cache 设计，提供统一的缓存接口，支持 Redis 和 Memory 两种适配器。

## 架构设计

```
core/cache/
├── adapter.py      # AdapterCache 抽象基类
├── memory.py       # Memory 内存缓存实现
├── redis.py        # Redis 缓存实现
├── cache.py        # 缓存初始化和管理
└── __init__.py     # 导出接口
```

### AdapterCache 接口

所有缓存适配器都实现以下统一接口：

```python
class AdapterCache(ABC):
    async def get(key: str) -> Optional[str]
    async def set(key: str, val: Any, expire: int = 0) -> None
    async def delete(key: str) -> None
    async def hash_get(hk: str, key: str) -> Optional[str]
    async def hash_set(hk: str, key: str, val: Any) -> None
    async def hash_delete(hk: str, key: str) -> None
    async def increase(key: str) -> int
    async def decrease(key: str) -> int
    async def expire(key: str, duration: timedelta) -> None
    async def exists(key: str) -> bool
    async def close() -> None
```

## 配置

### settings.yaml / settings.dev.yaml

```yaml
cache:
  driver: "redis"      # redis 或 memory
  host: "localhost"    # Redis主机
  port: 6379          # Redis端口
  password: ""        # Redis密码（可选）
  db: 0               # Redis数据库编号
```

## 使用方式

### 1. 依赖注入方式（推荐）

```python
from fastapi import APIRouter, Depends
from core import get_cache
from core.cache import AdapterCache

router = APIRouter()

@router.get("/example")
async def example(cache: AdapterCache = Depends(get_cache)):
    # 基本操作
    await cache.set("user:1001", "John Doe", expire=3600)
    value = await cache.get("user:1001")
    
    # 检查存在
    if await cache.exists("user:1001"):
        await cache.delete("user:1001")
    
    return {"value": value}
```

### 2. 服务层使用

```python
from core.cache import AdapterCache

class UserService:
    def __init__(self, cache: AdapterCache):
        self.cache = cache
    
    async def get_user(self, user_id: int):
        # 先查缓存
        cache_key = f"user:{user_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # 查数据库
        user = await self.db_query(user_id)
        
        # 写入缓存（1小时过期）
        await self.cache.set(cache_key, json.dumps(user), expire=3600)
        return user
```

### 3. Runtime 直接获取

```python
from core.runtime import runtime

async def some_function():
    cache = runtime.get_cache_client("default")
    if cache:
        await cache.set("key", "value", expire=60)
```

## 常用操作示例

### 字符串操作

```python
# 设置值（永不过期）
await cache.set("config:theme", "dark")

# 设置值（60秒后过期）
await cache.set("session:token123", "user_data", expire=60)

# 获取值
theme = await cache.get("config:theme")

# 删除值
await cache.delete("config:theme")

# 检查存在
exists = await cache.exists("config:theme")

# 更新过期时间
from datetime import timedelta
await cache.expire("session:token123", timedelta(minutes=30))
```

### 计数器操作

```python
# 初始化计数器
await cache.set("counter:views", "0")

# 递增
count = await cache.increase("counter:views")  # 返回 1
count = await cache.increase("counter:views")  # 返回 2

# 递减
count = await cache.decrease("counter:views")  # 返回 1
```

### 哈希表操作

```python
# 设置哈希字段
await cache.hash_set("user:1001", "name", "John Doe")
await cache.hash_set("user:1001", "email", "john@example.com")
await cache.hash_set("user:1001", "age", "30")

# 获取哈希字段
name = await cache.hash_get("user:1001", "name")
email = await cache.hash_get("user:1001", "email")

# 删除哈希字段
await cache.hash_delete("user:1001", "age")
```

### 会话缓存

```python
import json
from datetime import timedelta

class SessionCache:
    def __init__(self, cache: AdapterCache):
        self.cache = cache
    
    async def save_session(self, session_id: str, data: dict):
        """保存会话（30分钟有效）"""
        key = f"session:{session_id}"
        await self.cache.set(key, json.dumps(data), expire=1800)
    
    async def get_session(self, session_id: str) -> dict:
        """获取会话"""
        key = f"session:{session_id}"
        data = await self.cache.get(key)
        return json.loads(data) if data else {}
    
    async def delete_session(self, session_id: str):
        """删除会话"""
        key = f"session:{session_id}"
        await self.cache.delete(key)
    
    async def extend_session(self, session_id: str):
        """延长会话（再30分钟）"""
        key = f"session:{session_id}"
        if await self.cache.exists(key):
            await self.cache.expire(key, timedelta(minutes=30))
```

### 限流器示例

```python
from datetime import datetime

class RateLimiter:
    def __init__(self, cache: AdapterCache):
        self.cache = cache
    
    async def check_rate_limit(self, user_id: int, limit: int = 100, window: int = 60):
        """
        检查用户是否超过限流
        
        Args:
            user_id: 用户ID
            limit: 时间窗口内最大请求数
            window: 时间窗口（秒）
        
        Returns:
            bool: True 表示允许请求，False 表示超限
        """
        key = f"rate_limit:{user_id}"
        
        # 检查是否存在
        if not await self.cache.exists(key):
            await self.cache.set(key, "1", expire=window)
            return True
        
        # 递增计数
        count = await self.cache.increase(key)
        
        # 检查是否超限
        return count <= limit
```

## Memory vs Redis

### Memory 适配器

**优点：**
- 无需外部依赖
- 性能极高
- 适合单机部署
- 开发测试便捷

**缺点：**
- 数据不持久化
- 不支持分布式
- 重启后数据丢失

**适用场景：**
- 开发环境
- 单机部署
- 临时缓存
- 测试环境

### Redis 适配器

**优点：**
- 支持分布式
- 数据可持久化
- 支持集群
- 功能丰富

**缺点：**
- 需要运行 Redis 服务
- 网络开销

**适用场景：**
- 生产环境
- 分布式部署
- 需要持久化
- 多实例共享缓存

## 切换适配器

只需修改配置文件，无需修改代码：

```yaml
# 开发环境使用 Memory
cache:
  driver: "memory"

# 生产环境使用 Redis
cache:
  driver: "redis"
  host: "redis.prod.com"
  port: 6379
  password: "your-password"
  db: 0
```

## 最佳实践

### 1. 设置合理的过期时间

```python
# 短期数据：验证码（5分钟）
await cache.set("verify_code:email123", "123456", expire=300)

# 中期数据：会话（30分钟）
await cache.set("session:token", data, expire=1800)

# 长期数据：配置（1天）
await cache.set("config:system", data, expire=86400)
```

### 2. 使用命名空间

```python
# 用冒号分隔命名空间
await cache.set("user:1001:profile", data)
await cache.set("order:2002:detail", data)
await cache.set("product:3003:info", data)
```

### 3. 错误处理

```python
try:
    await cache.set("key", "value")
except Exception as e:
    logger.error(f"Cache error: {e}")
    # 降级处理：直接查数据库
    return await db.query(...)
```

### 4. 批量操作优化

```python
# 不推荐：多次调用
for user_id in user_ids:
    data = await cache.get(f"user:{user_id}")

# 推荐：使用哈希表
await cache.hash_set("users", "1001", user_data_1)
await cache.hash_set("users", "1002", user_data_2)
```

## 高级功能

### 获取原生 Redis 客户端（仅 Redis 适配器）

```python
from core.cache import Redis

cache = runtime.get_cache_client("default")
if isinstance(cache, Redis):
    # 获取原生客户端进行高级操作
    redis_client = cache.get_client()
    
    # 使用 Redis 特有功能
    await redis_client.zadd("leaderboard", {"user1": 100, "user2": 95})
    result = await redis_client.zrange("leaderboard", 0, -1, withscores=True)
```

## 测试

```python
import pytest
from core.cache import Memory, Redis

@pytest.mark.asyncio
async def test_memory_cache():
    cache = Memory()
    
    await cache.set("test_key", "test_value", expire=10)
    value = await cache.get("test_key")
    assert value == "test_value"
    
    await cache.delete("test_key")
    value = await cache.get("test_key")
    assert value is None

@pytest.mark.asyncio
async def test_redis_cache():
    cache = await Redis.create(host="localhost", port=6379)
    
    await cache.set("test_key", "test_value", expire=10)
    value = await cache.get("test_key")
    assert value == "test_value"
    
    await cache.close()
```
