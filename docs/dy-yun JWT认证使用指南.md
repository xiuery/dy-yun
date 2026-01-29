# dy-yun JWT 认证使用指南

## 概述

dy-yun 的 JWT 认证系统参考 go-admin 的设计模式实现，提供了完整的认证、授权和用户信息管理功能。

## 架构设计

### 三层架构

```
┌─────────────────────────────────────────┐
│  业务层 (Business Layer)                 │
│  - 路由定义                              │
│  - 业务逻辑                              │
│  - 使用 jwt_required 装饰器保护路由       │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  中间件层 (Middleware Layer)             │
│  - AuthInit: 初始化 JWT 中间件            │
│  - jwt_required: 认证依赖                │
│  - 回调函数: authenticator, payload_func  │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  核心层 (Core Layer)                     │
│  - JWTAuth: JWT 核心实现                 │
│  - token_generator: 生成 Token            │
│  - parse_token: 解析 Token                │
│  - middleware_func: 中间件函数            │
└─────────────────────────────────────────┘
```

### 文件组织

```
dy-yun/
├── core/jwtauth/              # JWT 核心实现（类似 go-admin-core）
│   ├── __init__.py            # 导出 JWTAuth, MapClaims 等
│   ├── constants.py           # JWT 常量定义
│   └── jwtauth.py             # JWTAuth 核心类
│
├── common/middleware/         # 认证中间件（类似 go-admin/common/middleware）
│   └── auth.py                # AuthInit 函数、jwt_required 依赖
│
└── common/routers/            # 认证路由
    ├── auth.py                # 登录、刷新、登出路由
    └── loader.py              # 路由加载器
```

## 快速开始

### 1. 配置 JWT 参数

编辑 `config/settings.yaml` 或 `config/settings.dev.yaml`：

```yaml
jwt:
  secret_key: "your-secret-key-here"  # 密钥
  algorithm: "HS256"                   # 加密算法（可选，默认 HS256）
  expire_minutes: 1440                 # 过期时间（分钟，默认 1440 = 24小时）
```

### 2. 自动初始化

JWT 认证中间件已在 `common/routers/loader.py` 中自动初始化：

```python
from common.routers.auth import init_auth_middleware

# 应用启动时自动调用
init_auth_middleware()
```

### 3. 使用认证路由

系统已提供以下认证端点：

#### 登录

```bash
POST /api/v1/login
Content-Type: application/json

{
  "username": "admin",
  "password": "123456"
}
```

响应：

```json
{
  "code": 200,
  "msg": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expire": 86400,
    "user": {
      "user_id": 1,
      "username": "admin",
      "rolekey": "admin"
    }
  }
}
```

#### 刷新 Token

```bash
POST /api/v1/refresh_token
Authorization: Bearer <your-token>
```

响应：

```json
{
  "code": 200,
  "msg": "刷新成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expire": 86400
  }
}
```

#### 登出

```bash
POST /api/v1/logout
Authorization: Bearer <your-token>
```

响应：

```json
{
  "code": 200,
  "msg": "登出成功",
  "data": null
}
```

#### 获取用户信息

```bash
GET /api/v1/user/info
Authorization: Bearer <your-token>
```

响应：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "user_id": 1,
    "username": "admin",
    "rolekey": "admin",
    "role_id": 1,
    "dept_id": 1
  }
}
```

## 保护路由

### 使用 jwt_required 依赖

```python
from fastapi import APIRouter, Request, Depends
from common.middleware.auth import jwt_required
from core.jwtauth import MapClaims, get_user_id, get_username

router = APIRouter(prefix="/api/v1/admin", tags=["管理"])

@router.get("/users")
async def get_users(
    request: Request,
    claims: MapClaims = Depends(jwt_required)
):
    """需要认证的路由"""
    # 获取当前用户信息
    user_id = get_user_id(request)
    username = get_username(request)
    
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "user_id": user_id,
            "username": username,
            "users": []
        }
    }
```

### 获取用户信息

系统提供了多个辅助函数从请求中提取用户信息：

```python
from core.jwtauth import (
    get_user_id,      # 获取用户 ID
    get_username,     # 获取用户名
    get_rolekey,      # 获取角色 Key
    get_role_id,      # 获取角色 ID
    get_dept_id,      # 获取部门 ID
    extract_claims,   # 提取完整的 Claims
)

@router.get("/profile")
async def get_profile(
    request: Request,
    _: MapClaims = Depends(jwt_required)
):
    user_id = get_user_id(request)
    username = get_username(request)
    rolekey = get_rolekey(request)
    role_id = get_role_id(request)
    dept_id = get_dept_id(request)
    
    # 或者获取完整的 Claims
    claims = extract_claims(request)
    
    return {"user_id": user_id, "username": username}
```

## 自定义认证逻辑

### 修改 Authenticator

编辑 `common/routers/auth.py` 中的 `authenticator` 函数：

```python
async def authenticator(request: Request) -> Optional[dict]:
    """自定义登录认证逻辑"""
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    
    # 自定义验证逻辑
    user = await your_custom_verify_logic(username, password)
    
    if user:
        return {
            "user_id": user.id,
            "username": user.username,
            # 添加其他需要的字段
        }
    return None
```

### 修改 Payload 生成

编辑 `common/routers/auth.py` 中的 `payload_func` 函数：

```python
def payload_func(user_data: dict) -> dict:
    """自定义 JWT Payload"""
    return {
        "identity": user_data.get("user_id"),
        "user_id": user_data.get("user_id"),
        "username": user_data.get("username"),
        # 添加自定义字段
        "custom_field": user_data.get("custom_field"),
    }
```

### 添加权限验证

编辑 `common/routers/auth.py` 中的 `authorizator` 函数：

```python
async def authorizator(claims: MapClaims, request: Request) -> bool:
    """自定义权限验证"""
    # 获取当前路由路径
    path = request.url.path
    
    # 获取用户角色
    rolekey = claims.get("rolekey")
    
    # 自定义权限逻辑
    if path.startswith("/api/v1/admin") and rolekey != "admin":
        return False
    
    return True
```

## Token 传递方式

系统支持三种 Token 传递方式（优先级从高到低）：

### 1. HTTP Header（推荐）

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2. Query 参数

```bash
GET /api/v1/users?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3. Cookie

```bash
Cookie: jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 错误处理

### 认证失败

当 Token 无效或过期时，系统返回：

```json
{
  "code": 401,
  "msg": "Token无效或已过期",
  "data": null
}
```

### 权限不足

当 `authorizator` 返回 `False` 时：

```json
{
  "code": 403,
  "msg": "权限不足",
  "data": null
}
```

## 高级用法

### 在中间件中使用

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from core.jwtauth import extract_claims, get_user_id

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 如果已通过 JWT 认证，可以直接获取用户信息
        try:
            user_id = get_user_id(request)
            if user_id:
                print(f"当前用户: {user_id}")
        except:
            pass
        
        response = await call_next(request)
        return response
```

### 多种认证方式共存

```python
from fastapi import Depends
from typing import Optional

async def optional_jwt(request: Request) -> Optional[MapClaims]:
    """可选的 JWT 认证"""
    try:
        from common.middleware.auth import jwt_required
        return await jwt_required(request)
    except:
        return None

@router.get("/public")
async def public_endpoint(
    request: Request,
    claims: Optional[MapClaims] = Depends(optional_jwt)
):
    """既可以匿名访问，也可以认证访问"""
    if claims:
        user_id = get_user_id(request)
        return {"msg": f"欢迎回来，用户 {user_id}"}
    else:
        return {"msg": "欢迎访客"}
```

## 与 go-admin 的对应关系

| go-admin | dy-yun | 说明 |
|----------|--------|------|
| `go-admin-core/sdk/pkg/jwtauth` | `core/jwtauth` | JWT 核心实现 |
| `common/middleware/auth.go:AuthInit()` | `common/middleware/auth.py:AuthInit()` | 初始化函数 |
| `common/middleware/handler` | 辅助函数 | 用户信息提取 |
| `GinJWTMiddleware.MiddlewareFunc()` | `jwt_required` 依赖 | 中间件函数 |
| `c.Set("key", value)` | `request.state.key = value` | 上下文传递 |
| `c.Get("key")` | `request.state.key` | 上下文读取 |

## 测试示例

### 使用 curl

```bash
# 1. 登录获取 Token
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}' \
  | jq -r '.data.token')

# 2. 使用 Token 访问受保护路由
curl -X GET http://localhost:8001/api/v1/user/info \
  -H "Authorization: Bearer $TOKEN"

# 3. 刷新 Token
curl -X POST http://localhost:8001/api/v1/refresh_token \
  -H "Authorization: Bearer $TOKEN"

# 4. 登出
curl -X POST http://localhost:8001/api/v1/logout \
  -H "Authorization: Bearer $TOKEN"
```

### 使用 Python requests

```python
import requests

BASE_URL = "http://localhost:8001/api/v1"

# 1. 登录
response = requests.post(
    f"{BASE_URL}/login",
    json={"username": "admin", "password": "123456"}
)
data = response.json()
token = data["data"]["token"]

# 2. 访问受保护路由
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/user/info", headers=headers)
print(response.json())

# 3. 刷新 Token
response = requests.post(f"{BASE_URL}/refresh_token", headers=headers)
new_token = response.json()["data"]["token"]

# 4. 登出
requests.post(f"{BASE_URL}/logout", headers=headers)
```

## 常见问题

### Q: Token 存储在哪里？

A: 客户端负责存储 Token，推荐存储在：
- Web: localStorage 或 sessionStorage
- 移动端: 安全存储（如 Keychain/Keystore）
- 请求时通过 Authorization Header 传递

### Q: 如何实现单点登录？

A: 在 `authenticator` 中记录登录状态到 Redis，在 `middleware_func` 中检查状态。

### Q: 如何实现记住我功能？

A: 根据请求参数调整 Token 过期时间：

```python
# 在 AuthInit 时根据配置调整 timeout
auth = AuthInit(
    authenticator=authenticator,
    # ... 其他参数
)

# 或在生成 Token 时动态调整
# 修改 jwtauth.py 的 token_generator 支持自定义过期时间
```

### Q: Token 被盗用怎么办？

A: 建议实施：
1. 使用 HTTPS 传输
2. Token 短期有效 + 刷新机制
3. 记录设备指纹，异常设备强制重新登录
4. 实现 Token 黑名单（登出时加入）

## 总结

dy-yun 的 JWT 认证系统：

✅ **完整的认证流程**：登录 → Token 生成 → 验证 → 刷新 → 登出  
✅ **灵活的回调机制**：authenticator, payload_func, authorizator  
✅ **便捷的辅助函数**：get_user_id, get_username 等  
✅ **多种 Token 传递方式**：Header, Query, Cookie  
✅ **与 go-admin 设计一致**：易于理解和迁移

参考文档：
- [go-admin JWT认证加载流程分析](./go-adminJWT认证加载流程分析.md)
- [dy-yun Core模块说明](./dy-yunCore模块说明.md)
