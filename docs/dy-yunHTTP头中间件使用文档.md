# HTTP头中间件使用文档

## 📋 概述

参考 go-admin 的 `common/middleware/header.go`，为 dy-yun 添加了三个HTTP头中间件：
- **NoCache** - 禁用缓存
- **Options** - 处理CORS预检请求  
- **Secure** - 添加安全响应头

## 🔧 中间件详解

### 1. NoCache Middleware（禁用缓存）

**功能：** 防止客户端缓存HTTP响应，确保每次都从服务器获取最新数据。

**添加的响应头：**
```http
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
Expires: Thu, 01 Jan 1970 00:00:00 GMT
Last-Modified: Sun, 26 Jan 2026 15:45:00 GMT
```

**使用场景：**
- API接口（防止数据过期）
- 实时数据查询
- 需要即时更新的页面

**Go-admin对应代码：**
```go
func NoCache(c *gin.Context) {
    c.Header("Cache-Control", "no-cache, no-store, max-age=0, must-revalidate, value")
    c.Header("Expires", "Thu, 01 Jan 1970 00:00:00 GMT")
    c.Header("Last-Modified", time.Now().UTC().Format(http.TimeFormat))
    c.Next()
}
```

**Python实现：**
```python
async def no_cache_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
    response.headers["Expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"
    response.headers["Last-Modified"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    return response
```

---

### 2. Options Middleware（CORS预检）

**功能：** 处理浏览器的CORS预检请求（OPTIONS），直接返回允许的方法和头信息。

**添加的响应头：**
```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET,POST,PUT,PATCH,DELETE,OPTIONS
Access-Control-Allow-Headers: authorization, origin, content-type, accept
Allow: HEAD,GET,POST,PUT,PATCH,DELETE,OPTIONS
Content-Type: application/json
```

**使用场景：**
- 跨域API请求
- 前后端分离项目
- 需要支持多种HTTP方法

**Go-admin对应代码：**
```go
func Options(c *gin.Context) {
    if c.Request.Method != "OPTIONS" {
        c.Next()
    } else {
        c.Header("Access-Control-Allow-Origin", "*")
        c.Header("Access-Control-Allow-Methods", "GET,POST,PUT,PATCH,DELETE,OPTIONS")
        c.Header("Access-Control-Allow-Headers", "authorization, origin, content-type, accept")
        c.Header("Allow", "HEAD,GET,POST,PUT,PATCH,DELETE,OPTIONS")
        c.Header("Content-Type", "application/json")
        c.AbortWithStatus(200)
    }
}
```

**Python实现：**
```python
async def options_middleware(request: Request, call_next):
    if request.method != "OPTIONS":
        return await call_next(request)
    
    return JSONResponse(
        status_code=200,
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "authorization, origin, content-type, accept",
            "Allow": "HEAD,GET,POST,PUT,PATCH,DELETE,OPTIONS",
            "Content-Type": "application/json",
        }
    )
```

---

### 3. Secure Middleware（安全头）

**功能：** 添加各种安全相关的HTTP响应头，增强应用安全性。

**添加的响应头：**
```http
Access-Control-Allow-Origin: *
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000  # 仅HTTPS
```

**安全特性：**

| 响应头 | 作用 | 防护 |
|--------|------|------|
| `X-Content-Type-Options: nosniff` | 防止MIME类型嗅探 | 防止浏览器错误解析内容类型 |
| `X-XSS-Protection: 1; mode=block` | 启用XSS过滤 | 防止跨站脚本攻击 |
| `Strict-Transport-Security` | 强制HTTPS | 防止中间人攻击 |
| `Access-Control-Allow-Origin` | CORS支持 | 跨域资源共享 |

**可选头（已注释）：**
```python
# 防止点击劫持
# response.headers["X-Frame-Options"] = "DENY"

# 内容安全策略
# response.headers["Content-Security-Policy"] = "script-src 'self' https://cdnjs.cloudflare.com"
```

**Go-admin对应代码：**
```go
func Secure(c *gin.Context) {
    c.Header("Access-Control-Allow-Origin", "*")
    //c.Header("X-Frame-Options", "DENY")
    c.Header("X-Content-Type-Options", "nosniff")
    c.Header("X-XSS-Protection", "1; mode=block")
    if c.Request.TLS != nil {
        c.Header("Strict-Transport-Security", "max-age=31536000")
    }
}
```

**Python实现：**
```python
async def secure_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
    
    return response
```

---

## 📦 集成方式

### 1. 在 main.py 中注册

```python
# 导入中间件
from common.middleware.header import no_cache_middleware, options_middleware, secure_middleware

# 注册中间件（注意顺序）
app.middleware("http")(error_handler_middleware)    # 最外层
app.middleware("http")(secure_middleware)           # 安全头
app.middleware("http")(options_middleware)          # CORS预检
app.middleware("http")(no_cache_middleware)         # 禁用缓存
app.middleware("http")(request_id_middleware)       # 请求ID
app.middleware("http")(logger_middleware)            # 日志
app.middleware("http")(rate_limit_middleware)        # 限流
```

### 2. 中间件执行顺序

```
客户端请求
    ↓
error_handler（异常处理）
    ↓
secure（添加安全头）
    ↓
options（处理OPTIONS请求）
    ↓
no_cache（添加缓存控制头）
    ↓
request_id（生成请求ID）
    ↓
logger（记录日志）
    ↓
rate_limit（限流检查）
    ↓
路由处理
    ↓
（响应按相反顺序返回）
    ↓
客户端收到响应
```

---

## 🧪 测试方法

### 方法1：使用测试脚本
```bash
# 启动服务
.\.venv\Scripts\python.exe main.py -c config/settings.dev.yaml

# 运行测试
.\.venv\Scripts\python.exe tests/test_headers.py
```

### 方法2：使用curl
```bash
# 测试普通请求
curl -i http://localhost:8001/health

# 测试OPTIONS请求
curl -i -X OPTIONS http://localhost:8001/health
```

### 方法3：浏览器开发者工具
1. 打开 http://localhost:8001/docs
2. F12 打开开发者工具
3. Network标签查看响应头

---

## 📊 预期响应头示例

```http
HTTP/1.1 200 OK
content-type: application/json
content-length: 41

# Secure Middleware
access-control-allow-origin: *
x-content-type-options: nosniff
x-xss-protection: 1; mode=block

# NoCache Middleware
cache-control: no-cache, no-store, max-age=0, must-revalidate
expires: Thu, 01 Jan 1970 00:00:00 GMT
last-modified: Sun, 26 Jan 2026 15:45:22 GMT

# RateLimit Middleware
x-ratelimit-limit: 200
x-ratelimit-window: 60

{"status":"healthy","version":"0.1.0"}
```

---

## ⚙️ 生产环境配置建议

### 1. CORS配置
生产环境应指定具体域名：
```python
# 修改 secure_middleware 和 options_middleware
response.headers["Access-Control-Allow-Origin"] = "https://yourdomain.com"
```

### 2. 启用X-Frame-Options
防止点击劫持：
```python
response.headers["X-Frame-Options"] = "DENY"
```

### 3. 配置CSP
内容安全策略：
```python
response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' https://cdn.example.com"
```

### 4. HTTPS强制
确保生产环境使用HTTPS，HSTS头才会生效。

---

## 🔗 相关文件

- **实现文件：** [common/middleware/header.py](d:\tools\dy-yun\common\middleware\header.py)
- **集成文件：** [main.py](d:\tools\dy-yun\main.py)
- **测试文件：** [tests/test_headers.py](d:\tools\dy-yun\tests\test_headers.py)
- **参考文件：** [go-admin/common/middleware/header.go](d:\tools\go-admin\common\middleware\header.go)
