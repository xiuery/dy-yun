# request.state 数据结构分析

## 概览

`request.state` 是 FastAPI 提供的请求级存储机制，用于在中间件和路由处理器之间共享数据。类似于 Go Gin 框架的 `c.Set()`。

## 完整数据结构

```python
request.state = {
    # ============ 基础信息 ============
    "request_id": str,           # UUID格式的请求唯一标识
    
    # ============ JWT认证信息 ============
    "jwt_payload": dict,         # 完整的JWT载荷
    "identity": str,             # JWT身份标识（通常是用户ID）
    
    # ============ 用户信息 ============
    "user_id": int,              # 用户ID
    "username": str,             # 用户名
    
    # ============ 角色信息 ============
    "role": str,                 # 角色名称（例如："admin"）
    "role_id": int,              # 角色ID
    "role_ids": int,             # 角色ID（别名，与role_id相同）
    "rolekey": str,              # 角色标识（例如："admin", "common"）
    
    # ============ 权限信息 ============
    "data_scope": str,           # 数据权限范围
    
    # ============ 组织信息 ============
    "dept_id": int,              # 部门ID
}
```

---

## 数据填充流程

### 1. **request_id** - 请求ID中间件

**文件：** [common/middleware/request_id.py](../common/middleware/request_id.py#L11)  
**时机：** 请求处理最早阶段  
**执行顺序：** 第5个中间件

```python
async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id  # 生成并存储UUID
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id  # 添加到响应头
    return response
```

**用途：**
- 请求追踪和日志关联
- 分布式系统中的链路追踪
- 错误排查时定位具体请求

---

### 2. **JWT认证信息** - JWT认证中间件

**文件：** [core/jwtauth/jwtauth.py](../core/jwtauth/jwtauth.py#L330-L338)  
**时机：** JWT Token解析后  
**触发条件：** 请求头包含 `Authorization: Bearer <token>`

```python
# JWT验证成功后填充
request.state.jwt_payload = claims      # 完整JWT载荷
request.state.identity = identity       # JWT identity字段

# 从JWT Claims中提取常用字段
request.state.user_id = claims.get("user_id")
request.state.username = claims.get("username")
request.state.rolekey = claims.get("rolekey", "")
request.state.role_id = claims.get("role_id")
request.state.dept_id = claims.get("dept_id")
```

**JWT Payload 示例：**
```json
{
    "identity": "1",
    "user_id": 1,
    "username": "admin",
    "rolekey": "admin",
    "role_id": 1,
    "dept_id": 103,
    "exp": 1738223849,
    "iat": 1738137449,
    "iss": "dy-yun"
}
```

---

### 3. **用户和角色详细信息** - Authorizator回调

**文件：** [common/middleware/handler/auth.py](../common/middleware/handler/auth.py#L105-L109)  
**时机：** JWT验证通过，从数据库查询用户后  
**触发条件：** 启用了 `authorizator` 回调函数

```python
async def authorizator(request: Request, data: dict) -> bool:
    sys_user = data.get("user")  # SysUser模型实例
    sys_role = data.get("role")  # SysRole模型实例
    
    # 存储数据库查询的完整信息
    request.state.role = sys_role.role_name        # "管理员"
    request.state.role_ids = sys_role.role_id      # 1（与role_id相同）
    request.state.user_id = sys_user.id            # 1
    request.state.username = sys_user.username     # "admin"
    request.state.data_scope = sys_role.data_scope # "1"（数据权限）
    
    return True
```

---

## 数据来源对比

| 字段 | JWT中间件 | Authorizator | 数据源 |
|------|----------|--------------|--------|
| `request_id` | ❌ | ❌ | UUID生成 |
| `jwt_payload` | ✅ | ❌ | JWT Token |
| `identity` | ✅ | ❌ | JWT Claims |
| `user_id` | ✅ | ✅（覆盖） | JWT → DB |
| `username` | ✅ | ✅（覆盖） | JWT → DB |
| `rolekey` | ✅ | ❌ | JWT Claims |
| `role_id` | ✅ | ❌ | JWT Claims |
| `dept_id` | ✅ | ❌ | JWT Claims |
| `role` | ❌ | ✅ | 数据库查询 |
| `role_ids` | ❌ | ✅ | 数据库查询 |
| `data_scope` | ❌ | ✅ | 数据库查询 |

**注意：** `user_id` 和 `username` 会被覆盖两次（先JWT，后DB查询）

---

## 中间件执行顺序

```
请求进入
    ↓
1. error_handler      → 全局异常捕获
    ↓
2. secure             → 安全响应头
    ↓
3. options            → CORS预检
    ↓
4. no_cache           → 禁用缓存
    ↓
5. request_id         → 生成request_id ✅
    ↓
6. logger             → 请求日志
    ↓
7. rate_limit         → 使用request.state.user_id限流 ✅
    ↓
8. JWT middleware     → 验证Token，填充jwt_payload, identity, user_id等 ✅
    ↓
9. authorizator       → 数据库查询，填充role, data_scope等 ✅
    ↓
路由处理器
```

---

## 使用场景

### 1. **日志追踪**

```python
# common/middleware/logger.py
request_id = getattr(request.state, "request_id", "")
logger = get_request_logger(request_id)
logger.info(f"→ {request.method} {request.url.path}")
```

### 2. **限流标识**

```python
# common/middleware/rate_limit.py
if hasattr(request.state, "user_id"):
    client_id = f"user:{request.state.user_id}"  # 基于用户限流
else:
    client_id = f"ip:{request.client.host}"      # 基于IP限流
```

### 3. **权限控制**

```python
# 业务代码中
def check_permission(request: Request):
    role_key = getattr(request.state, "rolekey", "")
    if role_key != "admin":
        raise HTTPException(403, "Forbidden")
```

### 4. **数据权限过滤**

```python
# 服务层查询
data_scope = getattr(request.state, "data_scope", "")
user_id = getattr(request.state, "user_id")

if data_scope == "1":  # 全部数据权限
    query = select(Model)
elif data_scope == "2":  # 自定义数据权限
    query = select(Model).where(Model.dept_id.in_(allowed_depts))
elif data_scope == "5":  # 仅本人数据
    query = select(Model).where(Model.create_by == user_id)
```

### 5. **审计日志**

```python
# 记录操作人信息
username = getattr(request.state, "username", "anonymous")
user_id = getattr(request.state, "user_id", 0)

audit_log = {
    "user_id": user_id,
    "username": username,
    "action": "delete_user",
    "request_id": request.state.request_id,
    "timestamp": datetime.now()
}
```

---

## 字段详解

### request_id (UUID)
- **类型：** `str`
- **格式：** `"550e8400-e29b-41d4-a716-446655440000"`
- **用途：** 唯一标识一次请求，用于日志追踪
- **响应头：** `X-Request-Id`

### jwt_payload (JWT载荷)
- **类型：** `dict`
- **包含字段：**
  ```python
  {
      "identity": "1",       # JWT标识
      "user_id": 1,
      "username": "admin",
      "rolekey": "admin",
      "role_id": 1,
      "dept_id": 103,
      "exp": 1738223849,    # 过期时间戳
      "iat": 1738137449,    # 签发时间戳
      "iss": "dy-yun"       # 签发者
  }
  ```

### identity (身份标识)
- **类型：** `str`
- **值：** 通常是用户ID的字符串形式
- **用途：** JWT的核心标识字段

### user_id (用户ID)
- **类型：** `int`
- **来源：** JWT Claims → 数据库查询（会覆盖）
- **用途：** 用户唯一标识

### username (用户名)
- **类型：** `str`
- **来源：** JWT Claims → 数据库查询（会覆盖）
- **示例：** `"admin"`, `"zhangsan"`

### role / role_name (角色名称)
- **类型：** `str`
- **来源：** 数据库 `sys_role.role_name`
- **示例：** `"管理员"`, `"普通用户"`
- **用途：** 显示角色中文名

### role_id (角色ID)
- **类型：** `int`
- **来源：** JWT Claims
- **示例：** `1` (管理员), `2` (普通用户)

### role_ids (角色ID别名)
- **类型：** `int`
- **来源：** 数据库 `sys_role.role_id`
- **与role_id关系：** 内容相同，只是重复存储

### rolekey (角色标识)
- **类型：** `str`
- **来源：** JWT Claims
- **示例：** `"admin"`, `"common"`
- **用途：** 权限判断（更细粒度）

### data_scope (数据权限)
- **类型：** `str`
- **来源：** 数据库 `sys_role.data_scope`
- **可能值：**
  - `"1"` - 全部数据权限
  - `"2"` - 自定义数据权限
  - `"3"` - 本部门数据权限
  - `"4"` - 本部门及以下数据权限
  - `"5"` - 仅本人数据权限

### dept_id (部门ID)
- **类型：** `int`
- **来源：** JWT Claims
- **示例：** `103`
- **用途：** 部门数据权限过滤

---

## 最佳实践

### 1. **安全地访问字段**

```python
# ✅ 推荐：使用 getattr 提供默认值
user_id = getattr(request.state, "user_id", None)

# ✅ 推荐：使用 hasattr 检查
if hasattr(request.state, "user_id"):
    user_id = request.state.user_id

# ❌ 不推荐：直接访问可能抛出 AttributeError
user_id = request.state.user_id  # 未登录用户会报错
```

### 2. **区分匿名和认证用户**

```python
def get_current_user_id(request: Request) -> Optional[int]:
    """获取当前用户ID，未登录返回None"""
    return getattr(request.state, "user_id", None)

def require_auth(request: Request) -> int:
    """要求必须登录，未登录抛出异常"""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(401, "Unauthorized")
    return user_id
```

### 3. **使用类型提示**

```python
from typing import Optional
from fastapi import Request

def process(request: Request):
    user_id: Optional[int] = getattr(request.state, "user_id", None)
    username: str = getattr(request.state, "username", "anonymous")
    role: Optional[str] = getattr(request.state, "role", None)
```

### 4. **不要在中间件之外修改**

```python
# ❌ 不推荐：在路由处理器中修改
@router.get("/")
async def index(request: Request):
    request.state.custom_field = "value"  # 可能导致混乱

# ✅ 推荐：只在中间件中修改，在路由中读取
@router.get("/")
async def index(request: Request):
    user_id = getattr(request.state, "user_id")
```

---

## 调试技巧

### 1. **打印所有state数据**

```python
@router.get("/debug/state")
async def debug_state(request: Request):
    state_dict = {
        key: getattr(request.state, key)
        for key in dir(request.state)
        if not key.startswith("_")
    }
    return state_dict
```

### 2. **日志记录state变化**

```python
# 在中间件中
logger.debug(f"State after JWT: user_id={getattr(request.state, 'user_id', None)}")
logger.debug(f"State after auth: role={getattr(request.state, 'role', None)}")
```

### 3. **验证数据完整性**

```python
def validate_request_state(request: Request):
    required_fields = ["user_id", "username", "role_id"]
    missing = [f for f in required_fields if not hasattr(request.state, f)]
    if missing:
        logger.warning(f"Missing state fields: {missing}")
```

---

## 与 go-admin 对比

| go-admin (Gin) | dy-yun (FastAPI) | 说明 |
|----------------|------------------|------|
| `c.Set("userId", 1)` | `request.state.user_id = 1` | 设置值 |
| `c.Get("userId")` | `request.state.user_id` | 获取值 |
| `c.GetInt("userId")` | `getattr(request.state, "user_id", 0)` | 带默认值 |
| `c.GetString("username")` | `getattr(request.state, "username", "")` | 字符串类型 |

**主要区别：**
- Gin: 使用 `map[string]interface{}`，需要类型断言
- FastAPI: 直接属性访问，Python动态类型

---

## 常见问题

### Q1: 为什么 user_id 同时在 JWT 和 authorizator 中设置？

**A:** 
- JWT中间件设置：快速从Token中提取，不查数据库
- Authorizator设置：从数据库查询最新数据，确保数据准确性
- 最终使用的是数据库的值（后覆盖）

### Q2: role_id 和 role_ids 有什么区别？

**A:** 
- `role_id`: 来自JWT Claims
- `role_ids`: 来自数据库查询（authorizator）
- 两者值相同，是历史遗留的重复字段

### Q3: 如何在依赖注入中使用 request.state？

**A:**
```python
from fastapi import Depends, Request

def get_current_user_id(request: Request) -> int:
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(401, "Unauthorized")
    return user_id

@router.get("/profile")
async def profile(user_id: int = Depends(get_current_user_id)):
    return {"user_id": user_id}
```

### Q4: request.state 的生命周期是多久？

**A:** 
- 生命周期：单次HTTP请求
- 请求结束后自动销毁
- 不会跨请求共享（线程安全）

---

## 总结

`request.state` 是dy-yun项目中传递请求上下文的核心机制，包含：

1. **请求追踪**：request_id
2. **身份认证**：JWT payload, identity
3. **用户信息**：user_id, username
4. **角色权限**：role, rolekey, data_scope
5. **组织架构**：dept_id

**关键设计原则：**
- 只读不写（路由中）
- 安全访问（getattr）
- 清晰职责（中间件负责填充）
- 请求隔离（不跨请求）
