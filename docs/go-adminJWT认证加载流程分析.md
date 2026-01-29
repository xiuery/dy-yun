# go-admin JWT 认证中间件加载流程分析

## 目录结构

```
go-admin/
├── common/
│   └── middleware/
│       ├── auth.go              # JWT 认证中间件初始化
│       ├── init.go              # 中间件注册
│       └── handler/             # 处理器目录
│           ├── auth.go          # 认证相关处理器
│           ├── httpshandler.go  # HTTPS 重定向
│           ├── login.go         # 登录处理器
│           ├── ping.go          # 健康检查
│           ├── role.go          # 角色处理器
│           └── user.go          # 用户处理器

go-admin-core/
└── sdk/
    └── pkg/
        └── jwtauth/
            └── jwtauth.go       # JWT 核心实现
```

## 一、go-admin-core/sdk/pkg/jwtauth - JWT 核心模块

### 1.1 GinJWTMiddleware 结构体

这是 JWT 认证的核心结构体，类似第三方库 `github.com/appleboy/gin-jwt/v2`：

```go
// 文件：go-admin-core/sdk/pkg/jwtauth/jwtauth.go
package jwtauth

import (
    "time"
    "github.com/gin-gonic/gin"
    "github.com/golang-jwt/jwt/v4"
)

// GinJWTMiddleware JWT 中间件配置
type GinJWTMiddleware struct {
    // ========== 基础配置 ==========
    Realm           string        // JWT 认证领域（通常是应用名称）
    Key             []byte        // 签名密钥
    Timeout         time.Duration // Token 超时时间
    MaxRefresh      time.Duration // Token 最大刷新时间
    IdentityKey     string        // 身份标识键（在 Payload 中的字段名）
    
    // ========== 回调函数（核心） ==========
    
    // Authenticator 登录认证函数
    // 验证用户凭证（用户名/密码），返回用户数据或错误
    // 在 /login 接口中调用
    Authenticator func(c *gin.Context) (interface{}, error)
    
    // PayloadFunc Payload 生成函数
    // 将用户数据转换为 JWT Claims（载荷）
    // 在生成 Token 时调用
    PayloadFunc func(data interface{}) MapClaims
    
    // Authorizator 权限校验函数（可选）
    // 验证用户是否有权限访问当前资源
    // 在每个受保护的路由中调用
    Authorizator func(data interface{}, c *gin.Context) bool
    
    // Unauthorized 未授权处理函数
    // 处理认证失败的响应
    Unauthorized func(*gin.Context, int, string)
    
    // IdentityHandler 身份提取函数（可选）
    // 从 Claims 中提取用户身份信息
    IdentityHandler func(*gin.Context) interface{}
    
    // LoginResponse 登录成功响应函数（可选）
    // 自定义登录成功的响应格式
    LoginResponse func(*gin.Context, int, string, time.Time)
    
    // RefreshResponse 刷新成功响应函数（可选）
    // 自定义 Token 刷新成功的响应格式
    RefreshResponse func(*gin.Context, int, string, time.Time)
    
    // LogoutResponse 登出成功响应函数（可选）
    // 自定义登出成功的响应格式
    LogoutResponse func(*gin.Context, int)
    
    // ========== Token 配置 ==========
    TokenLookup   string // Token 查找位置："header: Authorization, query: token, cookie: jwt"
    TokenHeadName string // Token 前缀："Bearer"
    TimeFunc      func() time.Time // 时间函数（用于测试）
    
    // ========== 其他配置 ==========
    SendCookie       bool          // 是否通过 Cookie 发送 Token
    SecureCookie     bool          // Cookie 是否仅 HTTPS
    CookieHTTPOnly   bool          // Cookie 是否 HttpOnly
    CookieDomain     string        // Cookie 域名
    SendAuthorization bool         // 是否发送 Authorization header
    DisabledAbort    bool          // 禁用自动 Abort（用于自定义错误处理）
    CookieName       string        // Cookie 名称
    CookieSameSite   http.SameSite // Cookie SameSite 属性
}

// MapClaims JWT Claims 类型别名
type MapClaims = jwt.MapClaims

// ========== 核心方法 ==========

// New 创建 JWT 中间件实例
func New(m *GinJWTMiddleware) (*GinJWTMiddleware, error) {
    // 设置默认值
    if m.Realm == "" {
        m.Realm = "go-admin"
    }
    if m.TimeFunc == nil {
        m.TimeFunc = time.Now
    }
    if m.TokenLookup == "" {
        m.TokenLookup = "header: Authorization"
    }
    if m.TokenHeadName == "" {
        m.TokenHeadName = "Bearer"
    }
    if m.IdentityKey == "" {
        m.IdentityKey = "identity"
    }
    if m.Timeout == 0 {
        m.Timeout = time.Hour
    }
    if m.MaxRefresh == 0 {
        m.MaxRefresh = m.Timeout
    }
    
    // 验证必需的回调函数
    if m.Key == nil {
        return nil, ErrMissingSecretKey
    }
    if m.Authenticator == nil {
        return nil, ErrMissingAuthenticatorFunc
    }
    
    return m, nil
}

// MiddlewareFunc 返回 Gin 中间件函数（核心）
// 用于保护需要认证的路由
func (mw *GinJWTMiddleware) MiddlewareFunc() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 1. 从请求中提取 Token
        token, err := mw.parseToken(c)
        if err != nil {
            mw.unauthorized(c, http.StatusUnauthorized, mw.HTTPStatusMessageFunc(err, c))
            return
        }
        
        // 2. 验证 Token
        if !token.Valid {
            mw.unauthorized(c, http.StatusUnauthorized, "token is invalid")
            return
        }
        
        // 3. 提取 Claims
        claims := token.Claims.(jwt.MapClaims)
        
        // 4. 检查是否过期
        if mw.TimeFunc().Unix() > int64(claims["exp"].(float64)) {
            mw.unauthorized(c, http.StatusUnauthorized, "token is expired")
            return
        }
        
        // 5. 身份提取（可选）
        var identity interface{}
        if mw.IdentityHandler != nil {
            identity = mw.IdentityHandler(c)
        } else {
            identity = claims[mw.IdentityKey]
        }
        
        // 6. 权限校验（可选）
        if mw.Authorizator != nil {
            if !mw.Authorizator(claims, c) {
                mw.unauthorized(c, http.StatusForbidden, "you don't have permission to access")
                return
            }
        }
        
        // 7. 将 Claims 和身份信息存入上下文
        c.Set("JWT_PAYLOAD", claims)
        c.Set(mw.IdentityKey, identity)
        
        // 8. 继续处理请求
        c.Next()
    }
}

// LoginHandler 登录处理器
// 处理 POST /login 请求
func (mw *GinJWTMiddleware) LoginHandler(c *gin.Context) {
    // 1. 调用 Authenticator 验证用户
    data, err := mw.Authenticator(c)
    if err != nil {
        mw.unauthorized(c, http.StatusUnauthorized, err.Error())
        return
    }
    
    // 2. 生成 Token
    token := mw.TokenGenerator(data)
    
    // 3. 返回响应
    if mw.LoginResponse != nil {
        mw.LoginResponse(c, http.StatusOK, token, mw.TimeFunc().Add(mw.Timeout))
    } else {
        c.JSON(http.StatusOK, gin.H{
            "code":   200,
            "token":  token,
            "expire": mw.TimeFunc().Add(mw.Timeout).Format(time.RFC3339),
        })
    }
}

// RefreshHandler Token 刷新处理器
func (mw *GinJWTMiddleware) RefreshHandler(c *gin.Context) {
    // 从旧 Token 提取 Claims 并生成新 Token
    token, _ := mw.parseToken(c)
    claims := token.Claims.(jwt.MapClaims)
    
    newToken := mw.TokenGenerator(claims)
    
    if mw.RefreshResponse != nil {
        mw.RefreshResponse(c, http.StatusOK, newToken, mw.TimeFunc().Add(mw.Timeout))
    } else {
        c.JSON(http.StatusOK, gin.H{
            "code":   200,
            "token":  newToken,
            "expire": mw.TimeFunc().Add(mw.Timeout).Format(time.RFC3339),
        })
    }
}

// LogoutHandler 登出处理器
func (mw *GinJWTMiddleware) LogoutHandler(c *gin.Context) {
    if mw.LogoutResponse != nil {
        mw.LogoutResponse(c, http.StatusOK)
    } else {
        c.JSON(http.StatusOK, gin.H{
            "code": 200,
            "msg":  "success",
        })
    }
}

// ========== 内部方法 ==========

// TokenGenerator 生成 Token
func (mw *GinJWTMiddleware) TokenGenerator(data interface{}) string {
    // 1. 生成 Claims
    var claims MapClaims
    if mw.PayloadFunc != nil {
        claims = mw.PayloadFunc(data)
    } else {
        claims = MapClaims{}
    }
    
    // 2. 添加过期时间
    expire := mw.TimeFunc().Add(mw.Timeout)
    claims["exp"] = expire.Unix()
    claims["orig_iat"] = mw.TimeFunc().Unix()
    
    // 3. 生成 Token
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    tokenString, _ := token.SignedString(mw.Key)
    
    return tokenString
}

// parseToken 从请求中解析 Token
func (mw *GinJWTMiddleware) parseToken(c *gin.Context) (*jwt.Token, error) {
    var token string
    
    // 从不同位置查找 Token
    parts := strings.Split(mw.TokenLookup, ",")
    for _, part := range parts {
        part = strings.TrimSpace(part)
        
        if strings.HasPrefix(part, "header:") {
            // 从 Header 获取
            headerName := strings.TrimSpace(strings.TrimPrefix(part, "header:"))
            token = c.GetHeader(headerName)
            if token != "" {
                // 去除 "Bearer " 前缀
                if len(token) > len(mw.TokenHeadName) {
                    token = strings.TrimSpace(token[len(mw.TokenHeadName):])
                }
                break
            }
        } else if strings.HasPrefix(part, "query:") {
            // 从查询参数获取
            queryName := strings.TrimSpace(strings.TrimPrefix(part, "query:"))
            token = c.Query(queryName)
            if token != "" {
                break
            }
        } else if strings.HasPrefix(part, "cookie:") {
            // 从 Cookie 获取
            cookieName := strings.TrimSpace(strings.TrimPrefix(part, "cookie:"))
            token, _ = c.Cookie(cookieName)
            if token != "" {
                break
            }
        }
    }
    
    if token == "" {
        return nil, ErrEmptyAuthHeader
    }
    
    // 解析 Token
    return jwt.Parse(token, func(token *jwt.Token) (interface{}, error) {
        if jwt.GetSigningMethod(token.Method.Alg()) != jwt.SigningMethodHS256 {
            return nil, ErrInvalidSigningAlgorithm
        }
        return mw.Key, nil
    })
}

// unauthorized 未授权响应
func (mw *GinJWTMiddleware) unauthorized(c *gin.Context, code int, message string) {
    c.Header("WWW-Authenticate", "JWT realm="+mw.Realm)
    
    if !mw.DisabledAbort {
        c.Abort()
    }
    
    if mw.Unauthorized != nil {
        mw.Unauthorized(c, code, message)
    } else {
        c.JSON(code, gin.H{
            "code": code,
            "msg":  message,
        })
    }
}

// ========== 错误定义 ==========

var (
    ErrMissingSecretKey           = errors.New("secret key is required")
    ErrMissingAuthenticatorFunc   = errors.New("authenticator func is required")
    ErrEmptyAuthHeader            = errors.New("auth header is empty")
    ErrInvalidSigningAlgorithm    = errors.New("invalid signing algorithm")
)

// ========== 常量定义 ==========

const (
    // JwtPayloadKey 上下文中存储 JWT Payload 的键
    JwtPayloadKey = "JWT_PAYLOAD"
)
```

### 1.2 关键常量

```go
// JwtPayloadKey 是上下文中存储 JWT Claims 的键
// 其他中间件（如权限校验）可以通过这个键获取用户信息
const JwtPayloadKey = "JWT_PAYLOAD"
```

---

## 二、go-admin/common/middleware/auth.go - JWT 认证中间件初始化

### 2.1 AuthInit 函数

这是 JWT 中间件的初始化入口，在应用启动时调用：

```go
// 文件：go-admin/common/middleware/auth.go
package middleware

import (
    "errors"
    "time"
    "github.com/gin-gonic/gin"
    "go-admin/app/admin/models"
    "go-admin/app/admin/service"
    "go-admin/app/admin/service/dto"
    "go-admin/common/global"
    "go-admin/common/middleware/handler"
    toolsConfig "go-admin-core/config"
    "go-admin-core/sdk"
    "go-admin-core/sdk/pkg/captcha"
    "go-admin-core/sdk/pkg/jwtauth"
    "go-admin-core/sdk/pkg/response"
)

// AuthInit 初始化 JWT 认证中间件
// 返回配置好的 GinJWTMiddleware 实例
func AuthInit() (*jwtauth.GinJWTMiddleware, error) {
    return jwtauth.New(&jwtauth.GinJWTMiddleware{
        // ========== 基础配置 ==========
        Realm:      "go-admin",                                      // JWT 认证领域
        Key:        []byte(toolsConfig.ApplicationConfig.JwtSecret), // 从配置读取密钥
        Timeout:    time.Hour * time.Duration(toolsConfig.ApplicationConfig.JwtTimeout), // Token 超时时间
        MaxRefresh: time.Hour * time.Duration(toolsConfig.ApplicationConfig.JwtTimeout), // 最大刷新时间
        
        // ========== Token 配置 ==========
        IdentityKey:   "identity",  // 身份标识键
        TokenLookup:   "header: Authorization, query: token, cookie: jwt", // Token 查找位置
        TokenHeadName: "Bearer",    // Token 前缀
        TimeFunc:      time.Now,    // 时间函数
        
        // ========== 核心回调函数 ==========
        
        // Authenticator 登录认证函数
        // 在 POST /login 时调用
        Authenticator: func(c *gin.Context) (interface{}, error) {
            var loginVals dto.LoginReq
            
            // 1. 绑定登录请求参数
            if err := c.ShouldBind(&loginVals); err != nil {
                return "", jwtauth.ErrMissingLoginValues
            }
            
            // 2. 验证验证码
            if !captcha.Verify(loginVals.UUID, loginVals.Code, true) {
                return nil, errors.New("验证码错误")
            }
            
            // 3. 验证用户名密码（调用 Service 层）
            s := service.SysUser{}
            s.Orm = sdk.Runtime.GetDbByKey(c.Request.Host)
            s.Log = api.GetRequestLogger(c)
            
            user, role, err := s.GetUser(&loginVals)
            if err != nil {
                return nil, errors.New("用户名或密码错误")
            }
            
            // 4. 检查用户状态
            if user.Status != "2" {
                return nil, errors.New("用户已被禁用")
            }
            
            // 5. 记录登录日志（异步）
            go handler.LoggerLogin(c, user, "登录成功")
            
            // 6. 返回用户数据（会传给 PayloadFunc）
            return user, nil
        },
        
        // PayloadFunc Payload 生成函数
        // 将用户数据转换为 JWT Claims
        PayloadFunc: func(data interface{}) jwtauth.MapClaims {
            if v, ok := data.(*models.SysUser); ok {
                return jwtauth.MapClaims{
                    "userId":   v.UserId,      // 用户 ID
                    "username": v.Username,    // 用户名
                    "roleId":   v.RoleId,      // 角色 ID
                    "roleKey":  v.RoleKey,     // 角色标识（用于 Casbin）
                    "deptId":   v.DeptId,      // 部门 ID
                }
            }
            return jwtauth.MapClaims{}
        },
        
        // IdentityHandler 身份提取函数
        // 从 Claims 中提取用户身份信息
        IdentityHandler: func(c *gin.Context) interface{} {
            claims := jwtauth.ExtractClaims(c)
            return claims[jwtauth.IdentityKey]
        },
        
        // Authorizator 权限校验函数
        // 在每个受保护的路由中调用
        Authorizator: func(data interface{}, c *gin.Context) bool {
            if v, ok := data.(jwtauth.MapClaims); ok {
                // 提取用户信息
                userId := int(v["userId"].(float64))
                roleKey := v["roleKey"].(string)
                
                // 将用户信息存入上下文
                c.Set("userId", userId)
                c.Set("roleKey", roleKey)
                
                return true
            }
            return false
        },
        
        // Unauthorized 未授权处理函数
        // 处理认证失败的响应
        Unauthorized: func(c *gin.Context, code int, message string) {
            response.Error(c, code, errors.New(message), message)
        },
        
        // ========== 登录/登出/刷新响应（可选） ==========
        
        // LoginResponse 登录成功响应
        LoginResponse: func(c *gin.Context, code int, token string, expire time.Time) {
            response.OK(c, gin.H{
                "token":  token,
                "expire": expire.Format(time.RFC3339),
            }, "登录成功")
        },
        
        // RefreshResponse Token 刷新成功响应
        RefreshResponse: func(c *gin.Context, code int, token string, expire time.Time) {
            response.OK(c, gin.H{
                "token":  token,
                "expire": expire.Format(time.RFC3339),
            }, "刷新成功")
        },
        
        // LogoutResponse 登出成功响应
        LogoutResponse: func(c *gin.Context, code int) {
            response.OK(c, nil, "登出成功")
        },
    })
}
```

### 2.2 登录请求 DTO

```go
// 文件：app/admin/service/dto/sys_user.go
package dto

type LoginReq struct {
    Username string `json:"username" binding:"required"` // 用户名
    Password string `json:"password" binding:"required"` // 密码
    Code     string `json:"code" binding:"required"`     // 验证码
    UUID     string `json:"uuid" binding:"required"`     // 验证码 UUID
}
```

---

## 三、go-admin/common/middleware/handler - 处理器目录

### 3.1 handler/login.go - 登录日志处理器

```go
// 文件：common/middleware/handler/login.go
package handler

import (
    "go-admin/app/admin/models"
    "go-admin/common/global"
    "go-admin-core/sdk"
    "github.com/gin-gonic/gin"
)

// LoggerLogin 记录登录日志（异步）
func LoggerLogin(c *gin.Context, user *models.SysUser, message string) {
    // 获取内存队列
    queue := sdk.Runtime.GetMemoryQueue("")
    
    // 构造登录日志数据
    loginLog := map[string]interface{}{
        "username":   user.Username,
        "ipaddr":     c.ClientIP(),
        "login_time": time.Now(),
        "status":     "0", // 成功
        "msg":        message,
    }
    
    // 发送到队列（异步处理）
    message, _ := sdk.Runtime.GetStreamMessage("", global.LoginLog, loginLog)
    queue.Append(message)
}
```

### 3.2 handler/httpshandler.go - HTTPS 重定向

```go
// 文件：common/middleware/handler/httpshandler.go
package handler

import (
    "github.com/gin-gonic/gin"
    "github.com/unrolled/secure"
)

// TlsHandler HTTPS 重定向中间件
func TlsHandler() gin.HandlerFunc {
    return func(c *gin.Context) {
        secureMiddleware := secure.New(secure.Options{
            SSLRedirect: true,                    // 重定向到 HTTPS
            SSLHost:     "localhost:443",         // HTTPS 主机
        })
        
        err := secureMiddleware.Process(c.Writer, c.Request)
        if err != nil {
            return
        }
        
        c.Next()
    }
}
```

### 3.3 handler/user.go - 用户信息提取

```go
// 文件：common/middleware/handler/user.go
package handler

import (
    "github.com/gin-gonic/gin"
    "go-admin-core/sdk/pkg/jwtauth"
)

// GetUserId 从上下文获取用户 ID
func GetUserId(c *gin.Context) int {
    claims := jwtauth.ExtractClaims(c)
    if userId, ok := claims["userId"].(float64); ok {
        return int(userId)
    }
    return 0
}

// GetUsername 从上下文获取用户名
func GetUsername(c *gin.Context) string {
    claims := jwtauth.ExtractClaims(c)
    if username, ok := claims["username"].(string); ok {
        return username
    }
    return ""
}

// GetRoleKey 从上下文获取角色标识
func GetRoleKey(c *gin.Context) string {
    claims := jwtauth.ExtractClaims(c)
    if roleKey, ok := claims["roleKey"].(string); ok {
        return roleKey
    }
    return ""
}
```

---

## 四、加载流程详解

### 4.1 应用启动流程

```
main.go
  ↓
cmd/api/server.go::setup()
  ↓
配置初始化、数据库初始化、存储初始化
  ↓
cmd/api/server.go::run()
  ↓
initRouter() 【路由初始化】
  ↓
common.InitMiddleware(r) 【中间件注册】
  ↓
for _, f := range AppRouters { f() } 【业务路由注册】
  ↓
app/admin/router/init_router.go::InitRouter()
  ↓
【关键步骤】authMiddleware := common.AuthInit()
```

### 4.2 JWT 中间件初始化时序

```
1. 应用启动
   ↓
2. InitRouter() 调用
   ↓
3. common.AuthInit() 【创建 JWT 中间件】
   ├─ 设置基础配置（Realm, Key, Timeout）
   ├─ 设置 Authenticator（登录认证函数）
   ├─ 设置 PayloadFunc（Payload 生成函数）
   ├─ 设置 Authorizator（权限校验函数）
   ├─ 设置 Unauthorized（未授权处理函数）
   └─ 返回 *jwtauth.GinJWTMiddleware
   ↓
4. 注册路由
   ├─ 公共路由（无认证）
   │   ├─ POST /login → authMiddleware.LoginHandler
   │   ├─ POST /refresh → authMiddleware.RefreshHandler
   │   └─ POST /logout → authMiddleware.LogoutHandler
   │
   └─ 受保护路由（需要认证）
       ├─ .Use(authMiddleware.MiddlewareFunc()) 【注册中间件】
       ├─ .Use(middleware.AuthCheckRole())       【角色权限校验】
       └─ 业务路由
```

### 4.3 登录请求流程

```
POST /login
  ↓
authMiddleware.LoginHandler(c)
  ↓
1. 调用 Authenticator(c)
   ├─ 绑定请求参数（username, password, code, uuid）
   ├─ 验证验证码
   ├─ 调用 Service 层验证用户名密码
   ├─ 检查用户状态
   ├─ 记录登录日志（异步）
   └─ 返回 user 对象
  ↓
2. 调用 PayloadFunc(user)
   ├─ 提取用户字段（userId, username, roleId, roleKey, deptId）
   └─ 返回 MapClaims
  ↓
3. 生成 JWT Token
   ├─ 添加过期时间 exp
   ├─ 使用 HS256 算法签名
   └─ 返回 token 字符串
  ↓
4. 调用 LoginResponse(c, 200, token, expire)
   └─ 返回 JSON：{"code": 0, "data": {"token": "xxx", "expire": "..."}}
```

### 4.4 受保护路由请求流程

```
GET /api/v1/sys-user
  ↓
authMiddleware.MiddlewareFunc()(c) 【JWT 认证中间件】
  ↓
1. 从请求中提取 Token
   ├─ 尝试从 Header: Authorization
   ├─ 尝试从 Query: token
   └─ 尝试从 Cookie: jwt
  ↓
2. 解析 Token
   ├─ 验证签名算法（HS256）
   ├─ 使用密钥解密
   └─ 提取 Claims
  ↓
3. 验证 Token 有效性
   ├─ 检查是否过期（exp 字段）
   └─ 检查签名是否正确
  ↓
4. 调用 IdentityHandler(c) 【可选】
   └─ 提取用户身份信息
  ↓
5. 调用 Authorizator(claims, c) 【可选】
   ├─ 提取用户信息（userId, roleKey）
   ├─ 存入上下文：c.Set("userId", userId)
   └─ 返回 true/false
  ↓
6. 将 Claims 存入上下文
   ├─ c.Set("JWT_PAYLOAD", claims)
   └─ c.Set("identity", identity)
  ↓
7. c.Next() 【继续执行后续中间件和处理器】
  ↓
middleware.AuthCheckRole()(c) 【角色权限校验中间件】
  ↓
1. 从上下文获取用户信息
   └─ claims := c.Get("JWT_PAYLOAD")
  ↓
2. 提取 roleKey
  ↓
3. 管理员直通（roleKey == "admin"）
  ↓
4. Casbin 策略校验
   ├─ 获取 Enforcer
   ├─ enforcer.Enforce(roleKey, path, method)
   └─ 返回 true/false
  ↓
5. 权限不足返回 403
  ↓
业务处理器
  ↓
返回响应
```

### 4.5 数据流转

```
                    ┌──────────────────────────────────┐
                    │   1. 用户发起登录请求             │
                    │   POST /login                     │
                    │   {username, password, code}      │
                    └────────────┬─────────────────────┘
                                 │
                    ┌────────────▼─────────────────────┐
                    │   2. LoginHandler                 │
                    │   调用 Authenticator              │
                    └────────────┬─────────────────────┘
                                 │
                    ┌────────────▼─────────────────────┐
                    │   3. Authenticator                │
                    │   - 验证验证码                    │
                    │   - 查询数据库验证用户名密码       │
                    │   - 返回 user 对象                │
                    └────────────┬─────────────────────┘
                                 │
                    ┌────────────▼─────────────────────┐
                    │   4. PayloadFunc                  │
                    │   user → MapClaims                │
                    │   {userId, username, roleKey...}  │
                    └────────────┬─────────────────────┘
                                 │
                    ┌────────────▼─────────────────────┐
                    │   5. TokenGenerator               │
                    │   - 添加 exp 字段                 │
                    │   - HS256 签名                    │
                    │   - 返回 token 字符串             │
                    └────────────┬─────────────────────┘
                                 │
                    ┌────────────▼─────────────────────┐
                    │   6. LoginResponse                │
                    │   返回 JSON：{token, expire}      │
                    └──────────────────────────────────┘
                                 │
                                 │
                    ┌────────────▼─────────────────────┐
                    │   7. 用户后续请求                 │
                    │   GET /api/v1/sys-user            │
                    │   Header: Authorization: Bearer xxx│
                    └────────────┬─────────────────────┘
                                 │
                    ┌────────────▼─────────────────────┐
                    │   8. MiddlewareFunc               │
                    │   - parseToken（提取 token）      │
                    │   - 验证签名和过期时间             │
                    └────────────┬─────────────────────┘
                                 │
                    ┌────────────▼─────────────────────┐
                    │   9. Authorizator                 │
                    │   - 提取 claims                   │
                    │   - 存入上下文                    │
                    │   c.Set("JWT_PAYLOAD", claims)    │
                    └────────────┬─────────────────────┘
                                 │
                    ┌────────────▼─────────────────────┐
                    │   10. AuthCheckRole               │
                    │   - 从上下文读取 claims           │
                    │   - Casbin 权限校验               │
                    └────────────┬─────────────────────┘
                                 │
                    ┌────────────▼─────────────────────┐
                    │   11. 业务处理器                  │
                    │   - handler.GetUserId(c)          │
                    │   - 执行业务逻辑                  │
                    └──────────────────────────────────┘
```

---

## 五、关键设计模式

### 5.1 回调函数模式

JWT 中间件使用回调函数实现高度可定制化：

- **Authenticator**：业务自定义登录逻辑
- **PayloadFunc**：业务自定义 Token 载荷
- **Authorizator**：业务自定义权限校验
- **Unauthorized**：业务自定义错误响应

### 5.2 上下文传递模式

使用 Gin 的 Context 在中间件链中传递用户信息：

```go
// JWT 中间件存入
c.Set("JWT_PAYLOAD", claims)
c.Set("userId", userId)
c.Set("roleKey", roleKey)

// 权限中间件读取
claims := c.Get("JWT_PAYLOAD")
userId := c.GetInt("userId")

// 业务处理器读取
userId := handler.GetUserId(c)
```

### 5.3 中间件链模式

```
请求 → JWT认证 → 角色权限校验 → 数据权限校验 → 业务处理 → 响应
       MiddlewareFunc   AuthCheckRole   PermissionAction   Handler
```

每个中间件负责特定职责，通过 `c.Next()` 传递控制权。

---

## 六、核心要点总结

### 6.1 关键常量

| 常量 | 值 | 用途 |
|------|---|------|
| `JwtPayloadKey` | "JWT_PAYLOAD" | 上下文中存储 JWT Claims 的键 |
| `IdentityKey` | "identity" | Claims 中身份标识的键 |

### 6.2 关键函数

| 函数 | 职责 | 调用时机 |
|------|------|---------|
| `AuthInit()` | 初始化 JWT 中间件 | 应用启动时 |
| `Authenticator` | 验证用户凭证 | 登录时 |
| `PayloadFunc` | 生成 JWT Claims | 生成 Token 时 |
| `MiddlewareFunc` | 验证 JWT Token | 每个受保护的请求 |
| `Authorizator` | 权限校验 | 每个受保护的请求 |

### 6.3 数据流

```
用户数据 → Authenticator → 验证成功
   ↓
user 对象 → PayloadFunc → MapClaims
   ↓
MapClaims → TokenGenerator → JWT Token
   ↓
JWT Token → 返回给客户端
   ↓
客户端请求带 Token → MiddlewareFunc → 解析验证
   ↓
Claims → Authorizator → 权限校验
   ↓
Claims → 存入上下文 → 业务处理器使用
```

### 6.4 与其他中间件的协作

```
1. JWT 认证（AuthInit）
   - 验证 Token
   - 提取用户信息
   - 存入上下文：c.Set("JWT_PAYLOAD", claims)
   
2. 角色权限校验（AuthCheckRole）
   - 读取上下文：c.Get("JWT_PAYLOAD")
   - 提取 roleKey
   - Casbin 策略匹配
   
3. 数据权限（PermissionAction）
   - 读取上下文：c.Get("JWT_PAYLOAD")
   - 提取 userId, deptId
   - 构造数据范围过滤条件
   
4. 业务处理器
   - 读取用户信息：handler.GetUserId(c)
   - 执行业务逻辑
```

这就是 go-admin JWT 认证中间件的完整加载流程和实现细节！
