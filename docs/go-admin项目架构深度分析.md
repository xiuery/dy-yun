# go-admin 项目架构深度分析

> 基于 go-admin-core 框架构建的企业级权限管理系统  
> 详细解析每个目录、组件职责、初始化顺序及框架耦合点

## 目录

1. [项目概览](#项目概览)
2. [项目目录结构](#项目目录结构)
3. [核心包职责详解](#核心包职责详解)
4. [应用层架构](#应用层架构)
5. [初始化流程详解](#初始化流程详解)
6. [框架耦合点分析](#框架耦合点分析)
7. [中间件体系](#中间件体系)
8. [数据权限系统](#数据权限系统)
9. [后台任务系统](#后台任务系统)
10. [设计模式分析](#设计模式分析)
11. [优缺点评估](#优缺点评估)

---

## 项目概览

### 技术栈

| 组件 | 技术选型 | 版本 | 用途 |
|------|---------|------|------|
| **Web 框架** | Gin | v1.7.7 | HTTP 路由和中间件 |
| **ORM 框架** | GORM | v1.24.2 | 数据库访问层 |
| **配置管理** | go-admin-core/config | 自研 | 配置加载和热更新 |
| **日志框架** | Zap | v1.21+ | 结构化日志 |
| **权限管理** | Casbin | v2.x | RBAC 权限控制 |
| **任务调度** | Cron | v3.x | 定时任务 |
| **缓存** | Redis | - | 缓存和分布式锁 |
| **消息队列** | Redis Stream/NSQ | - | 异步任务队列 |
| **JWT** | jwt-go | v4.x | 身份认证 |
| **API 文档** | Swagger | v1.x | 接口文档生成 |

### 项目特点

1. **分层架构**: API → Service → Model 三层结构
2. **权限体系**: 基于 Casbin 的 RBAC + 数据权限
3. **代码生成**: 内置代码生成器，快速生成 CRUD 代码
4. **插件化**: 模块化设计，易于扩展
5. **前后分离**: RESTful API，配合 Vue 前端

---

## 项目目录结构

```
go-admin/
├── main.go                      # 程序入口
├── go.mod                       # Go 模块依赖
├── Dockerfile                   # Docker 镜像构建
├── docker-compose.yml           # Docker 编排配置
├── Makefile                     # 编译脚本
├── README.md                    # 项目说明
│
├── app/                         # 应用层 - 业务模块
│   ├── admin/                   # 系统管理模块
│   │   ├── apis/                # API 控制器层
│   │   │   ├── sys_user.go      # 用户管理 API
│   │   │   ├── sys_role.go      # 角色管理 API
│   │   │   ├── sys_menu.go      # 菜单管理 API
│   │   │   ├── sys_dept.go      # 部门管理 API
│   │   │   ├── sys_post.go      # 岗位管理 API
│   │   │   ├── sys_dict_type.go # 字典类型 API
│   │   │   ├── sys_dict_data.go # 字典数据 API
│   │   │   ├── sys_config.go    # 参数配置 API
│   │   │   ├── sys_api.go       # API 管理 API
│   │   │   ├── sys_login_log.go # 登录日志 API
│   │   │   ├── sys_opera_log.go # 操作日志 API
│   │   │   ├── captcha.go       # 验证码 API
│   │   │   └── go_admin.go      # 登录/登出 API
│   │   │
│   │   ├── models/              # 数据模型层
│   │   │   ├── sys_user.go      # 用户模型
│   │   │   ├── sys_role.go      # 角色模型
│   │   │   ├── sys_menu.go      # 菜单模型
│   │   │   ├── sys_dept.go      # 部门模型
│   │   │   ├── sys_post.go      # 岗位模型
│   │   │   ├── sys_dict_type.go # 字典类型模型
│   │   │   ├── sys_dict_data.go # 字典数据模型
│   │   │   ├── sys_config.go    # 参数配置模型
│   │   │   ├── sys_api.go       # API 模型
│   │   │   ├── sys_login_log.go # 登录日志模型
│   │   │   ├── sys_opera_log.go # 操作日志模型
│   │   │   ├── casbin_rule.go   # Casbin 规则模型
│   │   │   ├── datascope.go     # 数据权限 Scope
│   │   │   └── initdb.go        # 数据库初始化
│   │   │
│   │   ├── service/             # 业务逻辑层
│   │   │   ├── dto/             # 数据传输对象
│   │   │   │   ├── sys_user.go  # 用户 DTO
│   │   │   │   ├── sys_role.go  # 角色 DTO
│   │   │   │   └── ...
│   │   │   ├── sys_user.go      # 用户业务逻辑
│   │   │   ├── sys_role.go      # 角色业务逻辑
│   │   │   ├── sys_menu.go      # 菜单业务逻辑
│   │   │   └── ...
│   │   │
│   │   └── router/              # 路由配置
│   │       ├── init_router.go   # 路由初始化入口
│   │       ├── router.go        # 公共路由注册
│   │       ├── sys_user.go      # 用户路由
│   │       ├── sys_role.go      # 角色路由
│   │       └── ...
│   │
│   ├── jobs/                    # 定时任务模块
│   │   ├── apis/                # 任务管理 API
│   │   │   └── sys_job.go
│   │   ├── models/              # 任务模型
│   │   │   └── sys_job.go
│   │   ├── service/             # 任务业务逻辑
│   │   │   ├── dto/
│   │   │   └── sys_job.go
│   │   ├── router/              # 任务路由
│   │   │   ├── int_router.go
│   │   │   └── sys_job.go
│   │   ├── jobbase.go           # 任务基类（HTTP/Exec）
│   │   ├── type.go              # 任务类型定义
│   │   └── examples.go          # 任务示例
│   │
│   └── other/                   # 其他功能模块
│       ├── apis/                # 其他 API
│       │   ├── file.go          # 文件上传
│       │   ├── sys_server_monitor.go # 服务器监控
│       │   └── tools/           # 代码生成工具
│       │       ├── gen.go       # 代码生成器
│       │       ├── sys_tables.go # 表管理
│       │       ├── db_tables.go # 数据库表查询
│       │       └── db_columns.go # 数据库列查询
│       ├── models/              # 其他模型
│       │   └── tools/           # 代码生成模型
│       ├── service/             # 其他服务
│       └── router/              # 其他路由
│           ├── init_router.go
│           ├── file.go
│           ├── monitor.go
│           └── gen_router.go
│
├── cmd/                         # 命令行接口
│   ├── cobra.go                 # Cobra 根命令
│   ├── api/                     # API 服务器命令
│   │   ├── server.go            # 启动 API 服务
│   │   ├── jobs.go              # 任务相关命令
│   │   └── other.go             # 其他命令
│   ├── app/                     # 应用命令
│   │   └── server.go
│   ├── migrate/                 # 数据库迁移命令
│   │   ├── server.go
│   │   └── migration/           # 迁移脚本
│   ├── config/                  # 配置命令
│   │   └── server.go
│   └── version/                 # 版本命令
│       └── server.go
│
├── common/                      # 公共组件层
│   ├── actions/                 # 通用 Action（CRUD）
│   │   ├── create.go            # 创建操作
│   │   ├── delete.go            # 删除操作
│   │   ├── update.go            # 更新操作
│   │   ├── view.go              # 查看操作
│   │   ├── index.go             # 列表操作
│   │   ├── permission.go        # 权限检查 Action
│   │   └── type.go              # 类型定义
│   │
│   ├── apis/                    # 公共 API 基类
│   │   └── api.go               # API 基础结构（继承 sdk.Api）
│   │
│   ├── database/                # 数据库配置
│   │   └── initialize.go        # 数据库初始化（多数据库支持）
│   │
│   ├── dto/                     # 公共 DTO
│   │   ├── pagination.go        # 分页 DTO
│   │   └── search.go            # 搜索 DTO
│   │
│   ├── file_store/              # 文件存储
│   │   └── ...
│   │
│   ├── global/                  # 全局常量
│   │   ├── adm.go               # 版本号、驱动名
│   │   └── ...
│   │
│   ├── middleware/              # 中间件
│   │   ├── init.go              # 中间件初始化
│   │   ├── auth.go              # JWT 认证中间件
│   │   ├── permission.go        # 权限校验中间件
│   │   ├── db.go                # DB 注入中间件
│   │   ├── logger.go            # 日志中间件
│   │   ├── customerror.go       # 错误处理中间件
│   │   ├── sentinel.go          # 流量控制中间件
│   │   ├── request_id.go        # 请求 ID 中间件
│   │   ├── header.go            # 安全头中间件
│   │   ├── demo.go              # 演示环境限制
│   │   ├── trace.go             # 链路追踪
│   │   └── handler/             # 处理器
│   │       └── ...
│   │
│   ├── models/                  # 公共模型
│   │   ├── by.go                # 排序字段
│   │   ├── user.go              # 用户模型扩展
│   │   ├── menu.go              # 菜单模型扩展
│   │   ├── type.go              # 类型定义
│   │   ├── migrate.go           # 迁移接口
│   │   └── response.go          # 响应结构
│   │
│   ├── response/                # 响应封装
│   │   └── ...
│   │
│   ├── service/                 # 公共 Service 基类
│   │   └── service.go           # Service 基础结构
│   │
│   ├── storage/                 # 存储初始化
│   │   └── initialize.go        # 缓存/队列/锁初始化
│   │
│   └── ip.go                    # IP 工具
│
├── config/                      # 配置扩展
│   ├── extend.go                # 扩展配置结构
│   └── settings.yml             # 主配置文件（示例）
│
├── docs/                        # API 文档
│   └── admin/                   # Swagger 文档
│
├── scripts/                     # 脚本文件
│   └── k8s/                     # Kubernetes 部署脚本
│
├── static/                      # 静态文件
│   └── ...
│
├── temp/                        # 临时文件
│
├── template/                    # 代码模板
│   └── ...                      # 代码生成模板
│
└── test/                        # 测试文件
    └── ...
```

---

## 核心包职责详解

### 1. main.go - 程序入口

**职责**: 应用启动的唯一入口，委托给 Cobra 命令行框架。

```go
package main

import (
    "go-admin/cmd"
)

//go:generate swag init --parseDependency --parseDepth=6 --instanceName admin -o ./docs/admin

func main() {
    cmd.Execute()  // 执行 Cobra 命令
}
```

**设计要点**:
- 极简入口，逻辑全部在 cmd 包
- Swagger 文档通过 `go generate` 生成
- 所有初始化逻辑延迟到命令执行阶段

---

### 2. cmd 包 - 命令行接口层

#### 2.1 cmd/cobra.go - 命令注册中心

**职责**: 定义 Cobra 根命令，注册子命令。

```go
var rootCmd = &cobra.Command{
    Use:   "go-admin",
    Short: "go-admin",
    Long:  `go-admin`,
}

func init() {
    rootCmd.AddCommand(api.StartCmd)      // API 服务器
    rootCmd.AddCommand(migrate.StartCmd)  // 数据库迁移
    rootCmd.AddCommand(version.StartCmd)  // 版本信息
    rootCmd.AddCommand(config.StartCmd)   // 配置管理
    rootCmd.AddCommand(app.StartCmd)      // 应用管理
}

func Execute() {
    if err := rootCmd.Execute(); err != nil {
        os.Exit(-1)
    }
}
```

**子命令**:
| 命令 | 说明 | 实现包 |
|------|------|--------|
| `server` | 启动 API 服务器 | cmd/api |
| `migrate` | 数据库迁移 | cmd/migrate |
| `version` | 显示版本信息 | cmd/version |
| `config` | 配置管理 | cmd/config |
| `app` | 应用管理 | cmd/app |

#### 2.2 cmd/api/server.go - API 服务器命令

**职责**: API 服务器启动的核心逻辑，包含配置加载、组件初始化、HTTP 服务启动。

**关键函数**:

##### 2.2.1 setup() - 初始化函数

```go
func setup() {
    // 1. 注入扩展配置
    config.ExtendConfig = &ext.ExtConfig
    
    // 2. 初始化配置（核心）
    config.Setup(
        file.NewSource(file.WithPath(configYml)),  // 配置源
        database.Setup,                             // 数据库初始化回调
        storage.Setup,                              // 存储初始化回调
    )
    
    // 3. 注册队列消费者
    queue := sdk.Runtime.GetMemoryQueue("")
    queue.Register(global.LoginLog, models.SaveLoginLog)   // 登录日志
    queue.Register(global.OperateLog, models.SaveOperaLog) // 操作日志
    queue.Register(global.ApiCheck, models.SaveSysApi)     // API 检查
    go queue.Run()  // 启动队列消费
    
    log.Info("starting api server...")
}
```

**初始化顺序**:
```
config.ExtendConfig 注入
   ↓
config.Setup() 【核心配置加载】
   ├─ 加载配置文件 (settings.yml)
   ├─ 初始化日志 (Logger.Setup)
   ├─ 执行 database.Setup() 【数据库初始化】
   │   ├─ gorm.Open() 创建数据库连接
   │   ├─ casbin.Setup() 权限引擎
   │   └─ sdk.Runtime.SetDb/SetCasbin
   └─ 执行 storage.Setup() 【存储初始化】
       ├─ setupCache() 缓存适配器
       ├─ setupCaptcha() 验证码存储
       └─ setupQueue() 队列适配器
   ↓
注册队列消费者
   ↓
启动队列消费（异步）
```

##### 2.2.2 run() - 运行函数

```go
func run() error {
    // 1. 设置 Gin 模式
    if config.ApplicationConfig.Mode == pkg.ModeProd.String() {
        gin.SetMode(gin.ReleaseMode)
    }
    
    // 2. 初始化路由
    initRouter()  // 创建 Gin 引擎，注册全局中间件
    
    // 3. 调用应用路由注册器
    for _, f := range AppRouters {
        f()  // 执行 router.InitRouter()
    }
    
    // 4. 创建 HTTP 服务器
    srv := &http.Server{
        Addr:         fmt.Sprintf("%s:%d", config.ApplicationConfig.Host, config.ApplicationConfig.Port),
        Handler:      sdk.Runtime.GetEngine(),  // 获取 Gin 引擎
        ReadTimeout:  time.Duration(config.ApplicationConfig.ReadTimeout) * time.Second,
        WriteTimeout: time.Duration(config.ApplicationConfig.WriterTimeout) * time.Second,
    }
    
    // 5. 启动后台任务
    go func() {
        jobs.InitJob()              // 初始化任务
        jobs.Setup(sdk.Runtime.GetDb())  // 加载数据库任务配置
    }()
    
    // 6. API 接口检查（可选）
    if apiCheck {
        // 将所有路由信息写入队列，用于 API 管理
        var routers = sdk.Runtime.GetRouter()
        q := sdk.Runtime.GetMemoryQueue("")
        mp := make(map[string]interface{})
        mp["List"] = routers
        message, _ := sdk.Runtime.GetStreamMessage("", global.ApiCheck, mp)
        q.Append(message)
    }
    
    // 7. 启动 HTTP 服务
    go func() {
        if config.SslConfig.Enable {
            srv.ListenAndServeTLS(config.SslConfig.Pem, config.SslConfig.KeyStr)
        } else {
            srv.ListenAndServe()
        }
    }()
    
    // 8. 打印启动信息
    fmt.Println("Server run at: http://localhost:8000/")
    fmt.Println("Swagger run at: http://localhost:8000/swagger/admin/index.html")
    
    // 9. 优雅关闭
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, os.Interrupt)
    <-quit
    
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    log.Info("Shutdown Server ... ")
    
    if err := srv.Shutdown(ctx); err != nil {
        log.Fatal("Server Shutdown:", err)
    }
    log.Info("Server exiting")
    
    return nil
}
```

##### 2.2.3 initRouter() - 路由初始化

```go
func initRouter() {
    var r *gin.Engine
    h := sdk.Runtime.GetEngine()
    if h == nil {
        h = gin.New()                // 创建 Gin 引擎
        sdk.Runtime.SetEngine(h)     // 保存到 Runtime
    }
    
    r = h.(*gin.Engine)
    
    // SSL 中间件
    if config.SslConfig.Enable {
        r.Use(handler.TlsHandler())
    }
    
    // 全局中间件
    r.Use(common.Sentinel()).               // 流量控制（Sentinel）
      Use(common.RequestId(pkg.TrafficKey)). // 请求 ID
      Use(api.SetRequestLogger)               // 设置请求日志
    
    // 初始化业务中间件
    common.InitMiddleware(r)
}
```

**中间件注册顺序**:
```
1. TlsHandler (可选)         - HTTPS 重定向
2. Sentinel                   - 流量控制
3. RequestId                  - 生成请求 ID
4. SetRequestLogger           - 设置请求日志
5. InitMiddleware() 【业务中间件】
   ├─ DemoEvn                 - 演示环境限制
   ├─ WithContextDb           - DB 注入上下文
   ├─ LoggerToFile            - 日志记录
   ├─ CustomError             - 自定义错误处理
   ├─ NoCache                 - 禁用缓存
   ├─ Options                 - CORS 跨域
   └─ Secure                  - 安全头
```

#### SetRequestLogger 中间件机制解析

**注入顺序与理由**
- 置于 `RequestId` 之后：先生成/写入请求 ID，再用该 ID 构造请求级日志器，确保链路日志一致性。

**实现位置**
- 源码：go-admin-core/sdk/api/request_logger.go
    - `SetRequestLogger(c *gin.Context)`: 创建带字段的 `logger.Helper` 并注入到上下文键 `pkg.LoggerKey`。
    - 字段：`strings.ToLower(pkg.TrafficKey)` → `requestid`，值为 `pkg.GenerateMsgIDFromContext(c)`。
    - `GetRequestLogger(c)`: 从上下文取出日志器；若不存在，则用同样规则临时创建一个（回退）。

**执行效果**
- 中下游（中间件/控制器）使用 `api.GetRequestLogger(c)` 输出结构化日志，自动携带 `requestid`，便于链路追踪。
- 与权限中间件协作：例如 `common/middleware/permission.go` 的 `AuthCheckRole` 使用 `api.GetRequestLogger(c)` 记录授权过程日志。

**使用示例**
```go
func Handler(c *gin.Context) {
        log := api.GetRequestLogger(c)
        log.Infof("request start: %s %s", c.Request.Method, c.Request.URL.Path)
        // ... 业务处理
        log.Infof("request end: %s %s", c.Request.Method, c.Request.URL.Path)
}
```

**注意事项**
- 中间件顺序：务必确保 `RequestId` 在前、`SetRequestLogger` 紧随其后，否则可能出现不同阶段生成不同请求 ID 导致日志不一致。
- 获取方式：统一通过 `api.GetRequestLogger(c)` 获取，避免绕过上下文造成字段缺失。

### 3. common 包 - 公共组件层

#### 3.1 common/database/initialize.go - 数据库初始化

**职责**: 配置和初始化多个数据库实例，集成 GORM 和 Casbin。

```go
func Setup() {
    for k := range toolsConfig.DatabasesConfig {
        setupSimpleDatabase(k, toolsConfig.DatabasesConfig[k])
    }
}

func setupSimpleDatabase(host string, c *toolsConfig.Database) {
    log.Infof("%s => %s", host, pkg.Green(c.Source))
    
    // 1. 配置连接池和读写分离
    registers := make([]toolsDB.ResolverConfigure, len(c.Registers))
    for i := range c.Registers {
        registers[i] = toolsDB.NewResolverConfigure(
            c.Registers[i].Sources,   // 读库
            c.Registers[i].Replicas,  // 写库
            c.Registers[i].Policy,    // 负载均衡策略
            c.Registers[i].Tables)    // 表映射
    }
    
    resolverConfig := toolsDB.NewConfigure(
        c.Source,           // 数据源
        c.MaxIdleConns,     // 最大空闲连接
        c.MaxOpenConns,     // 最大打开连接
        c.ConnMaxIdleTime,  // 连接最大空闲时间
        c.ConnMaxLifeTime,  // 连接最大生存时间
        registers)
    
    // 2. 初始化 GORM 【GORM 耦合点】
    db, err := resolverConfig.Init(&gorm.Config{
        NamingStrategy: schema.NamingStrategy{
            SingularTable: true,  // 单数表名
        },
        Logger: New(logger.Config{
            SlowThreshold: time.Second,
            Colorful:      true,
            LogLevel:      logger.LogLevel(log.DefaultLogger.Options().Level.LevelForGorm()),
        }),
    }, opens[c.Driver])  // 驱动选择器（MySQL/PostgreSQL/SQLite）
    
    if err != nil {
        log.Fatal(pkg.Red(c.Driver+" connect error :"), err)
    }
    
    log.Info(pkg.Green(c.Driver + " connect success !"))
    
    // 3. 初始化 Casbin 权限引擎
    e := mycasbin.Setup(db, "")
    
    // 4. 保存到 Runtime
    sdk.Runtime.SetDb(host, db)
    sdk.Runtime.SetCasbin(host, e)
}
```

**支持的数据库**:
- MySQL
- PostgreSQL
- SQLite
- SQL Server

**关键特性**:
- **多数据库**: 支持同时连接多个数据库实例
- **读写分离**: 通过 GORM Resolver 实现
- **连接池**: 可配置的连接池参数
- **日志集成**: 桥接 GORM 日志到 go-admin-core/logger

#### 3.2 common/storage/initialize.go - 存储初始化

**职责**: 初始化缓存、验证码存储、消息队列。

```go
func Setup() {
    setupCache()     // 缓存适配器
    setupCaptcha()   // 验证码存储
    setupQueue()     // 队列适配器
}

func setupCache() {
    cacheAdapter, err := config.CacheConfig.Setup()
    if err != nil {
        log.Fatalf("cache setup error, %s\n", err.Error())
    }
    sdk.Runtime.SetCacheAdapter(cacheAdapter)  // 保存到 Runtime
}

func setupCaptcha() {
    // 使用缓存存储验证码（TTL 600 秒）
    captcha.SetStore(captcha.NewCacheStore(sdk.Runtime.GetCacheAdapter(), 600))
}

func setupQueue() {
    if config.QueueConfig.Empty() {
        return
    }
    if q := sdk.Runtime.GetQueueAdapter(); q != nil {
        q.Shutdown()  // 关闭旧队列
    }
    queueAdapter, err := config.QueueConfig.Setup()
    if err != nil {
        log.Fatalf("queue setup error, %s\n", err.Error())
    }
    sdk.Runtime.SetQueueAdapter(queueAdapter)
    go queueAdapter.Run()  // 启动队列消费
}
```

**存储类型**:
| 类型 | 实现 | 用途 |
|------|------|------|
| 缓存 | Redis/Memory | 数据缓存、分布式锁 |
| 队列 | Redis Stream/NSQ | 异步任务、日志队列 |
| 验证码 | 基于缓存 | 图片验证码存储 |

#### 3.3 common/middleware/init.go - 中间件初始化

**职责**: 注册全局中间件和业务中间件。

```go
const (
    JwtTokenCheck   string = "JwtToken"           // JWT 认证中间件名称
    RoleCheck       string = "AuthCheckRole"      // 角色校验中间件名称
    PermissionCheck string = "PermissionAction"   // 权限校验中间件名称
)

func InitMiddleware(r *gin.Engine) {
    // 1. 全局中间件（按顺序执行）
    r.Use(DemoEvn())           // 演示环境限制（禁止修改数据）
    r.Use(WithContextDb)       // 数据库注入上下文 【GORM 耦合点】
    r.Use(LoggerToFile())      // 日志记录到文件
    r.Use(CustomError)         // 自定义错误处理
    r.Use(NoCache)             // 禁用浏览器缓存
    r.Use(Options)             // CORS 跨域处理
    r.Use(Secure)              // 安全头（XSS、MIME）
    
    // 2. 注册业务中间件到 Runtime（按需使用）
    sdk.Runtime.SetMiddleware(JwtTokenCheck, (*jwt.GinJWTMiddleware).MiddlewareFunc)
    sdk.Runtime.SetMiddleware(RoleCheck, AuthCheckRole())
    sdk.Runtime.SetMiddleware(PermissionCheck, actions.PermissionAction())
}
```

**中间件分类**:

**全局中间件** (所有请求):
- `DemoEvn` - 演示环境保护
- `WithContextDb` - DB 注入
- `LoggerToFile` - 日志记录
- `CustomError` - 错误处理
- `NoCache` - 缓存控制
- `Options` - CORS
- `Secure` - 安全头

**业务中间件** (路由级别):
- `JwtTokenCheck` - JWT 认证
- `RoleCheck` - 角色校验
- `PermissionCheck` - 权限校验

#### 3.4 common/apis/api.go - API 基类

**职责**: 封装 API 控制器的公共逻辑，继承自 `go-admin-core/sdk/api.Api`。

```go
type Api struct {
    Context *gin.Context      // Gin 上下文 【Gin 耦合点】
    Logger  *logger.Helper    // 请求日志
    Orm     *gorm.DB          // GORM 实例 【GORM 耦合点】
    Errors  error             // 错误累积
}

// MakeContext 设置 HTTP 上下文
func (e *Api) MakeContext(c *gin.Context) *Api {
    e.Context = c
    e.Logger = api.GetRequestLogger(c)
    return e
}

// MakeOrm 从上下文获取数据库连接
func (e *Api) MakeOrm() *Api {
    var err error
    e.Orm, err = pkg.GetOrm(e.Context)  // 从 gin.Context 获取 GORM 实例
    if err != nil {
        e.Logger.AddError(err)
    }
    return e
}

// Bind 绑定请求参数
func (e *Api) Bind(d interface{}, bindings ...binding.Binding) *Api {
    var err error
    if len(bindings) == 0 {
        bindings = append(bindings, binding.JSON, nil)
    }
    for i := range bindings {
        if bindings[i] == nil {
            // 兼容 URI 参数绑定
            err = e.Context.ShouldBindUri(d)
        } else {
            // 绑定 JSON/Form 参数
            err = e.Context.ShouldBindWith(d, bindings[i])
        }
        if err != nil {
            e.AddError(err)
            break
        }
    }
    return e
}

// MakeService 初始化 Service 层
func (e *Api) MakeService(s *service.Service) *Api {
    s.Orm = e.Orm
    s.Log = e.Logger
    return e
}
```

**链式调用示例**:
```go
func (e SysUser) GetPage(c *gin.Context) {
    s := service.SysUser{}
    req := dto.SysUserGetPageReq{}
    
    // 链式调用
    err := e.MakeContext(c).      // 设置上下文
        MakeOrm().                // 获取数据库连接
        Bind(&req).               // 绑定请求参数
        MakeService(&s.Service).  // 初始化 Service
        Errors                    // 获取错误
    
    if err != nil {
        e.Error(500, err, err.Error())
        return
    }
    
    // 调用 Service 层
    list := make([]models.SysUser, 0)
    var count int64
    err = s.GetPage(&req, p, &list, &count)
    if err != nil {
        e.Error(500, err, "查询失败")
        return
    }
    
    e.PageOK(list, int(count), req.GetPageIndex(), req.GetPageSize(), "查询成功")
}
```

#### 3.5 common/service/service.go - Service 基类

**职责**: 封装 Service 层的公共逻辑。

```go
type Service struct {
    Orm   *gorm.DB          // GORM 实例 【GORM 耦合点】
    Msg   string            // 消息
    MsgID string            // 消息 ID
    Log   *logger.Helper    // 日志
    Error error             // 错误
}

// AddError 累积错误
func (db *Service) AddError(err error) error {
    if db.Error == nil {
        db.Error = err
    } else if err != nil {
        db.Error = fmt.Errorf("%v; %w", db.Error, err)
    }
    return db.Error
}
```

**使用示例**:
```go
type SysUser struct {
    service.Service  // 继承 Service 基类
}

func (e *SysUser) GetPage(c *dto.SysUserGetPageReq, p *actions.DataPermission, list *[]models.SysUser, count *int64) error {
    var data models.SysUser
    
    // 使用 e.Orm 执行数据库操作
    err := e.Orm.Preload("Dept").
        Scopes(
            cDto.MakeCondition(c.GetNeedSearch()),  // 动态条件
            cDto.Paginate(c.GetPageSize(), c.GetPageIndex()),  // 分页
            actions.Permission(data.TableName(), p),  // 数据权限
        ).
        Find(list).Limit(-1).Offset(-1).
        Count(count).Error
    
    if err != nil {
        e.Log.Errorf("db error: %s", err)
        return err
    }
    return nil
}
```

#### 3.6 common/actions - 通用 CRUD Action

**职责**: 提供可复用的 CRUD 操作，减少重复代码。

##### 3.6.1 actions/permission.go - 数据权限中间件

```go
type DataPermission struct {
    DataScope string  // 数据范围（1=全部 2=自定义 3=本部门 4=本部门及以下 5=仅本人）
    UserId    int     // 用户 ID
    DeptId    int     // 部门 ID
    RoleId    int     // 角色 ID
}

// PermissionAction 权限检查中间件
func PermissionAction() gin.HandlerFunc {
    return func(c *gin.Context) {
        db, err := pkg.GetOrm(c)
        if err != nil {
            log.Error(err)
            return
        }
        
        var p = new(DataPermission)
        if userId := user.GetUserIdStr(c); userId != "" {
            // 从数据库查询用户的数据权限配置
            p, err = newDataPermission(db, userId)
            if err != nil {
                response.Error(c, 500, err, "权限范围鉴定错误")
                c.Abort()
                return
            }
        }
        c.Set(PermissionKey, p)  // 保存到上下文
        c.Next()
    }
}

// Permission 数据权限 Scope（GORM 作用域）
func Permission(tableName string, p *DataPermission) func(db *gorm.DB) *gorm.DB {
    return func(db *gorm.DB) *gorm.DB {
        if p == nil {
            return db
        }
        
        switch p.DataScope {
        case "1": // 全部数据权限
            return db
        case "2": // 自定义数据权限
            return db.Where(tableName+".create_by in (select sys_user.user_id from sys_user where sys_user.dept_id in (select dept_id from sys_role_dept where role_id = ?))", p.RoleId)
        case "3": // 本部门数据权限
            return db.Where(tableName+".create_by in (select user_id from sys_user where dept_id = ?)", p.DeptId)
        case "4": // 本部门及以下数据权限
            return db.Where(tableName+".create_by in (select user_id from sys_user where dept_id in (select dept_id from sys_dept where dept_path like ? ))", "%/"+strconv.Itoa(p.DeptId)+"/%")
        case "5": // 仅本人数据权限
            return db.Where(tableName+".create_by = ?", p.UserId)
        default:
            return db
        }
    }
}
```

##### 3.6.2 actions/create.go - 通用创建操作

```go
type CreateAction struct {
    Control    *gin.Context
    Service    CreateResp
    Business   CreateBus
    Model      interface{}
    ActionType string
}

type CreateResp interface {
    Insert(c *dto.GeneralUpdateReq, model interface{}) error
}

type CreateBus interface {
    BeforeInsert(c *gin.Context, e interface{}) error
    AfterInsert(c *gin.Context, e interface{}) error
}

func (e CreateAction) Action() {
    // 1. 参数绑定
    req := dto.GeneralUpdateReq{}
    if err := e.Control.ShouldBind(&req); err != nil {
        response.Error(e.Control, http.StatusUnprocessableEntity, err, "参数验证失败")
        return
    }
    
    // 2. 业务前置处理
    if e.Business != nil {
        if err := e.Business.BeforeInsert(e.Control, e.Model); err != nil {
            response.Error(e.Control, http.StatusInternalServerError, err, "")
            return
        }
    }
    
    // 3. 执行插入
    if err := e.Service.Insert(&req, e.Model); err != nil {
        response.Error(e.Control, http.StatusInternalServerError, err, "创建失败")
        return
    }
    
    // 4. 业务后置处理
    if e.Business != nil {
        if err := e.Business.AfterInsert(e.Control, e.Model); err != nil {
            response.Error(e.Control, http.StatusInternalServerError, err, "")
            return
        }
    }
    
    response.OK(e.Control, e.Model, "创建成功")
}
```

**其他 Action**:
- `DeleteAction` - 通用删除
- `UpdateAction` - 通用更新
- `ViewAction` - 通用查看
- `IndexAction` - 通用列表查询

---

## 应用层架构

### 1. app/admin - 系统管理模块

**职责**: 实现后台管理系统的核心功能，包括用户、角色、权限、菜单、部门、岗位、字典、日志等。

#### 1.1 模块组织结构

每个功能模块遵循统一的四层结构：

```
sys_user/
├── apis/sys_user.go         # API 控制器层（接收请求，返回响应）
├── models/sys_user.go       # 数据模型层（数据库表映射）
├── service/sys_user.go      # 业务逻辑层（业务处理）
│   └── dto/sys_user.go      # 数据传输对象（请求/响应结构）
└── router/sys_user.go       # 路由配置层（URL 映射）
```

#### 1.2 用户管理示例

##### 1.2.1 Model 层 (models/sys_user.go)

```go
type SysUser struct {
    UserId   int       `gorm:"primaryKey;autoIncrement" json:"userId"`
    Username string    `gorm:"size:64" json:"username"`
    Password string    `gorm:"size:128" json:"-"`
    NickName string    `gorm:"size:128" json:"nickName"`
    Phone    string    `gorm:"size:11" json:"phone"`
    RoleId   int       `gorm:"" json:"roleId"`
    Salt     string    `gorm:"size:255" json:"-"`
    Avatar   string    `gorm:"size:255" json:"avatar"`
    Sex      string    `gorm:"size:255" json:"sex"`
    Email    string    `gorm:"size:128" json:"email"`
    DeptId   int       `gorm:"" json:"deptId"`
    PostId   int       `gorm:"" json:"postId"`
    Remark   string    `gorm:"size:255" json:"remark"`
    Status   string    `gorm:"size:4" json:"status"`
    
    CreateBy   int       `gorm:"" json:"createBy"`
    UpdateBy   int       `gorm:"" json:"updateBy"`
    CreateTime time.Time `gorm:"autoCreateTime" json:"createTime"`
    UpdateTime time.Time `gorm:"autoUpdateTime" json:"updateTime"`
    
    // 关联查询
    Dept *SysDept `gorm:"foreignKey:DeptId;references:DeptId" json:"dept"`
    Role *SysRole `gorm:"foreignKey:RoleId;references:RoleId" json:"role"`
}

func (SysUser) TableName() string {
    return "sys_user"
}
```

##### 1.2.2 DTO 层 (service/dto/sys_user.go)

```go
// SysUserGetPageReq 分页查询请求
type SysUserGetPageReq struct {
    dto.Pagination  `search:"-"`              // 分页参数
    Username        string `form:"username" search:"type:contains;column:username;table:sys_user" comment:"用户名"`
    NickName        string `form:"nickName" search:"type:contains;column:nick_name;table:sys_user" comment:"昵称"`
    Phone           string `form:"phone" search:"type:contains;column:phone;table:sys_user" comment:"手机号"`
    DeptId          int    `form:"deptId" search:"type:exact;column:dept_id;table:sys_user" comment:"部门ID"`
    Status          string `form:"status" search:"type:exact;column:status;table:sys_user" comment:"状态"`
    SysUserOrder
}

// SysUserInsertReq 创建请求
type SysUserInsertReq struct {
    Username string `json:"username" comment:"用户名" binding:"required"`
    Password string `json:"password" comment:"密码" binding:"required"`
    NickName string `json:"nickName" comment:"昵称" binding:"required"`
    Phone    string `json:"phone" comment:"手机号"`
    RoleId   int    `json:"roleId" comment:"角色ID"`
    Avatar   string `json:"avatar" comment:"头像"`
    Sex      string `json:"sex" comment:"性别"`
    Email    string `json:"email" comment:"邮箱"`
    DeptId   int    `json:"deptId" comment:"部门ID" binding:"required"`
    PostId   int    `json:"postId" comment:"岗位ID"`
    Remark   string `json:"remark" comment:"备注"`
    Status   string `json:"status" comment:"状态" default:"2"`
}

// SysUserUpdateReq 更新请求
type SysUserUpdateReq struct {
    UserId   int    `json:"userId" comment:"用户ID" binding:"required"`
    Username string `json:"username" comment:"用户名"`
    NickName string `json:"nickName" comment:"昵称"`
    Phone    string `json:"phone" comment:"手机号"`
    RoleId   int    `json:"roleId" comment:"角色ID"`
    Avatar   string `json:"avatar" comment:"头像"`
    Sex      string `json:"sex" comment:"性别"`
    Email    string `json:"email" comment:"邮箱"`
    DeptId   int    `json:"deptId" comment:"部门ID"`
    PostId   int    `json:"postId" comment:"岗位ID"`
    Remark   string `json:"remark" comment:"备注"`
    Status   string `json:"status" comment:"状态"`
}

// Generate 从 DTO 生成 Model
func (s *SysUserInsertReq) Generate(model *models.SysUser) {
    model.Username = s.Username
    model.Password = s.Password
    model.NickName = s.NickName
    // ... 其他字段映射
}
```

**DTO 设计特点**:
- **标签驱动**: 通过 `search` 标签自动生成 GORM 查询条件
- **参数验证**: 使用 `binding` 标签集成 validator
- **类型转换**: 提供 Generate 方法将 DTO 转换为 Model

##### 1.2.3 Service 层 (service/sys_user.go)

```go
type SysUser struct {
    service.Service  // 继承公共 Service
}

// GetPage 获取用户列表
func (e *SysUser) GetPage(c *dto.SysUserGetPageReq, p *actions.DataPermission, list *[]models.SysUser, count *int64) error {
    var data models.SysUser
    
    err := e.Orm.Preload("Dept").  // 预加载部门信息
        Scopes(
            cDto.MakeCondition(c.GetNeedSearch()),  // 动态查询条件
            cDto.Paginate(c.GetPageSize(), c.GetPageIndex()),  // 分页
            actions.Permission(data.TableName(), p),  // 数据权限
        ).
        Find(list).Limit(-1).Offset(-1).
        Count(count).Error
    
    if err != nil {
        e.Log.Errorf("db error: %s", err)
        return err
    }
    return nil
}

// Get 获取单个用户
func (e *SysUser) Get(d *dto.SysUserById, p *actions.DataPermission, model *models.SysUser) error {
    var data models.SysUser
    
    err := e.Orm.Model(&data).
        Scopes(actions.Permission(data.TableName(), p)).
        First(model, d.GetId()).Error
    
    if err != nil && errors.Is(err, gorm.ErrRecordNotFound) {
        return errors.New("查看对象不存在或无权限")
    }
    if err != nil {
        e.Log.Errorf("db error: %s", err)
        return err
    }
    return nil
}

// Insert 创建用户
func (e *SysUser) Insert(c *dto.SysUserInsertReq) error {
    var err error
    var data models.SysUser
    
    // 1. DTO 转 Model
    c.Generate(&data)
    
    // 2. 密码加密
    data.Password = pkg.Md5(data.Password + data.Salt)
    
    // 3. 检查用户名是否重复
    var count int64
    e.Orm.Model(&models.SysUser{}).Where("username = ?", c.Username).Count(&count)
    if count > 0 {
        return errors.New("用户名已存在")
    }
    
    // 4. 执行插入
    err = e.Orm.Create(&data).Error
    if err != nil {
        e.Log.Errorf("db error: %s", err)
        return err
    }
    return nil
}

// Update 更新用户
func (e *SysUser) Update(c *dto.SysUserUpdateReq, p *actions.DataPermission) error {
    var err error
    var model models.SysUser
    
    // 1. 查询原记录
    db := e.Orm.Scopes(actions.Permission(model.TableName(), p)).
        First(&model, c.GetId())
    if err = db.Error; err != nil {
        return err
    }
    
    // 2. 更新字段
    c.Generate(&model)
    
    // 3. 执行更新
    db = db.Session(&gorm.Session{FullSaveAssociations: true}).
        Updates(&model)
    if err = db.Error; err != nil {
        return err
    }
    
    return nil
}

// Remove 删除用户
func (e *SysUser) Remove(c *dto.SysUserById, p *actions.DataPermission) error {
    var err error
    var data models.SysUser
    
    db := e.Orm.Scopes(actions.Permission(data.TableName(), p)).
        Delete(&data, c.GetId())
    if err = db.Error; err != nil {
        return err
    }
    if db.RowsAffected == 0 {
        return errors.New("删除失败或无权限")
    }
    return nil
}

// ResetPwd 重置密码
func (e *SysUser) ResetPwd(userId int, password string) error {
    user := models.SysUser{}
    user.UserId = userId
    user.Salt = pkg.GenerateSalt()
    user.Password = pkg.Md5(password + user.Salt)
    
    err := e.Orm.Model(&user).
        Select("password", "salt").
        Updates(&user).Error
    if err != nil {
        return err
    }
    return nil
}
```

**Service 层职责**:
- 实现业务逻辑
- 数据验证
- 数据库操作（CRUD）
- 数据权限控制
- 事务管理

##### 1.2.4 API 层 (apis/sys_user.go)

```go
type SysUser struct {
    api.Api  // 继承公共 API
}

// GetPage 获取用户列表
// @Summary 列表用户信息数据
// @Tags 用户
// @Param username query string false "username"
// @Success 200 {object} response.Response
// @Router /api/v1/sys-user [get]
// @Security Bearer
func (e SysUser) GetPage(c *gin.Context) {
    s := service.SysUser{}
    req := dto.SysUserGetPageReq{}
    
    // 链式调用初始化
    err := e.MakeContext(c).
        MakeOrm().
        Bind(&req).
        MakeService(&s.Service).
        Errors
    
    if err != nil {
        e.Logger.Error(err)
        e.Error(500, err, err.Error())
        return
    }
    
    // 获取数据权限
    p := actions.GetPermissionFromContext(c)
    
    // 调用 Service
    list := make([]models.SysUser, 0)
    var count int64
    err = s.GetPage(&req, p, &list, &count)
    if err != nil {
        e.Error(500, err, "查询失败")
        return
    }
    
    // 返回响应
    e.PageOK(list, int(count), req.GetPageIndex(), req.GetPageSize(), "查询成功")
}

// Get 获取单个用户
// @Summary 获取用户
// @Tags 用户
// @Param userId path int true "userId"
// @Success 200 {object} response.Response{data=models.SysUser}
// @Router /api/v1/sys-user/{userId} [get]
// @Security Bearer
func (e SysUser) Get(c *gin.Context) {
    s := service.SysUser{}
    req := dto.SysUserById{}
    err := e.MakeContext(c).
        MakeOrm().
        Bind(&req, binding.JSON, nil).
        MakeService(&s.Service).
        Errors
    
    if err != nil {
        e.Error(500, err, err.Error())
        return
    }
    
    p := actions.GetPermissionFromContext(c)
    var object models.SysUser
    err = s.Get(&req, p, &object)
    if err != nil {
        e.Error(500, err, "查询失败")
        return
    }
    
    e.OK(object, "查询成功")
}

// Insert 创建用户
// @Summary 创建用户
// @Tags 用户
// @Param data body dto.SysUserInsertReq true "body"
// @Success 200 {object} response.Response{data=models.SysUser}
// @Router /api/v1/sys-user [post]
// @Security Bearer
func (e SysUser) Insert(c *gin.Context) {
    s := service.SysUser{}
    req := dto.SysUserInsertReq{}
    err := e.MakeContext(c).
        MakeOrm().
        Bind(&req, binding.JSON).
        MakeService(&s.Service).
        Errors
    
    if err != nil {
        e.Error(500, err, err.Error())
        return
    }
    
    // 设置创建人
    req.SetCreateBy(user.GetUserId(c))
    
    err = s.Insert(&req)
    if err != nil {
        e.Error(500, err, "创建失败")
        return
    }
    
    e.OK(req, "创建成功")
}

// Update 更新用户
// @Summary 更新用户
// @Tags 用户
// @Param userId path int true "userId"
// @Param data body dto.SysUserUpdateReq true "body"
// @Success 200 {object} response.Response{data=models.SysUser}
// @Router /api/v1/sys-user/{userId} [put]
// @Security Bearer
func (e SysUser) Update(c *gin.Context) {
    s := service.SysUser{}
    req := dto.SysUserUpdateReq{}
    err := e.MakeContext(c).
        MakeOrm().
        Bind(&req, binding.JSON, nil).
        MakeService(&s.Service).
        Errors
    
    if err != nil {
        e.Error(500, err, err.Error())
        return
    }
    
    p := actions.GetPermissionFromContext(c)
    req.SetUpdateBy(user.GetUserId(c))
    
    err = s.Update(&req, p)
    if err != nil {
        e.Error(500, err, "更新失败")
        return
    }
    
    e.OK(req, "更新成功")
}

// Delete 删除用户
// @Summary 删除用户
// @Tags 用户
// @Param userId path int true "userId"
// @Success 200 {object} response.Response
// @Router /api/v1/sys-user/{userId} [delete]
// @Security Bearer
func (e SysUser) Delete(c *gin.Context) {
    s := service.SysUser{}
    req := dto.SysUserById{}
    err := e.MakeContext(c).
        MakeOrm().
        Bind(&req, binding.JSON, nil).
        MakeService(&s.Service).
        Errors
    
    if err != nil {
        e.Error(500, err, err.Error())
        return
    }
    
    p := actions.GetPermissionFromContext(c)
    err = s.Remove(&req, p)
    if err != nil {
        e.Error(500, err, "删除失败")
        return
    }
    
    e.OK(req, "删除成功")
}

// ResetPwd 重置密码
// @Summary 重置密码
// @Tags 用户
// @Param data body dto.ResetPwdReq true "body"
// @Success 200 {object} response.Response
// @Router /api/v1/sys-user/pwd/reset [put]
// @Security Bearer
func (e SysUser) ResetPwd(c *gin.Context) {
    s := service.SysUser{}
    req := dto.ResetPwdReq{}
    err := e.MakeContext(c).
        MakeOrm().
        Bind(&req, binding.JSON).
        MakeService(&s.Service).
        Errors
    
    if err != nil {
        e.Error(500, err, err.Error())
        return
    }
    
    err = s.ResetPwd(req.UserId, req.Password)
    if err != nil {
        e.Error(500, err, "重置失败")
        return
    }
    
    e.OK(nil, "重置成功")
}
```

**API 层职责**:
- 接收 HTTP 请求
- 参数绑定和验证
- 调用 Service 层
- 返回 HTTP 响应
- Swagger 文档注释

##### 1.2.5 Router 层 (router/sys_user.go)

```go
func init() {
    routerCheckRole = append(routerCheckRole, registerSysUserRouter)
}

// registerSysUserRouter 注册用户路由
func registerSysUserRouter(v1 *gin.RouterGroup, authMiddleware *jwt.GinJWTMiddleware) {
    api := apis.SysUser{}
    r := v1.Group("/sys-user").Use(authMiddleware.MiddlewareFunc()).Use(middleware.AuthCheckRole())
    {
        r.GET("", api.GetPage)           // 列表
        r.GET("/:userId", api.Get)       // 详情
        r.POST("", api.Insert)           // 创建
        r.PUT("/:userId", api.Update)    // 更新
        r.DELETE("/:userId", api.Delete) // 删除
    }
    
    // 重置密码路由（需要额外权限）
    r.PUT("/pwd/reset", api.ResetPwd)
    
    // 个人中心路由（无需权限检查）
    v1.Group("/user").Use(authMiddleware.MiddlewareFunc()).
        GET("/profile", api.GetProfile).
        PUT("/pwd", api.UpdatePwd).
        PUT("/avatar", api.UpdateAvatar)
}
```

**路由设计**:
- RESTful 风格
- 统一前缀 `/api/v1`
- 中间件链：`JWT认证 → 角色校验 → 权限校验`

#### 1.3 admin 模块功能清单

| 模块 | 功能 | 文件 |
|------|------|------|
| 用户管理 | 用户 CRUD、密码重置、个人中心 | sys_user.go |
| 角色管理 | 角色 CRUD、权限分配、数据权限配置 | sys_role.go |
| 菜单管理 | 菜单树、按钮权限、图标管理 | sys_menu.go |
| 部门管理 | 部门树、层级管理 | sys_dept.go |
| 岗位管理 | 岗位 CRUD | sys_post.go |
| 字典管理 | 字典类型、字典数据 | sys_dict_type.go, sys_dict_data.go |
| 参数配置 | 系统参数 CRUD | sys_config.go |
| API 管理 | API 列表、API 权限 | sys_api.go |
| 登录日志 | 登录日志查询 | sys_login_log.go |
| 操作日志 | 操作日志查询 | sys_opera_log.go |
| 登录/登出 | JWT 登录、登出、刷新令牌 | go_admin.go |
| 验证码 | 图形验证码生成 | captcha.go |

### 2. app/jobs - 定时任务模块

**职责**: 管理和执行定时任务，支持 HTTP 调用和本地函数执行。

#### 2.1 任务类型 (type.go)

```go
type JobExec interface {
    Exec(arg interface{}) error  // 任务执行接口
}

// HTTP 任务
type HttpJob struct {
    JobCore
}

// 本地函数任务
type ExecJob struct {
    JobCore
}

type JobCore struct {
    InvokeTarget   string  // 调用目标（URL 或函数名）
    Name           string  // 任务名称
    JobId          int     // 任务 ID
    EntryId        int     // Cron Entry ID
    CronExpression string  // Cron 表达式
    Args           string  // 参数（JSON 字符串）
}
```

#### 2.2 任务基类 (jobbase.go)

```go
// ExecJob.Run 执行本地函数任务
func (e *ExecJob) Run() {
    startTime := time.Now()
    var obj = jobList[e.InvokeTarget]  // 从注册表获取任务
    if obj == nil {
        log.Warn("[Job] ExecJob Run job nil")
        return
    }
    
    // 执行任务
    err := CallExec(obj.(JobExec), e.Args)
    if err != nil {
        log.Errorf("ExecJob Run error: %s", err)
        recordJobLog(e.JobId, e.Name, startTime, err, "failed")
        return
    }
    
    recordJobLog(e.JobId, e.Name, startTime, nil, "success")
}

// HttpJob.Run 执行 HTTP 任务
func (h *HttpJob) Run() {
    startTime := time.Now()
    
    // 发送 HTTP 请求
    resp, err := http.Get(h.InvokeTarget)
    if err != nil {
        log.Errorf("HttpJob Run error: %s", err)
        recordJobLog(h.JobId, h.Name, startTime, err, "failed")
        return
    }
    defer resp.Body.Close()
    
    recordJobLog(h.JobId, h.Name, startTime, nil, "success")
}

// InitJob 初始化任务注册表
func InitJob() {
    jobList = map[string]JobExec{
        "ExampleJob": ExampleJob{},  // 注册示例任务
    }
}

// Setup 从数据库加载任务配置
func Setup(db *gorm.DB) {
    jobList := make([]models2.SysJob, 0)
    db.Where("status = ?", "1").Find(&jobList)  // 查询启用的任务
    
    for _, job := range jobList {
        if job.JobType == "http" {
            AddHttpJob(&HttpJob{
                JobCore: JobCore{
                    InvokeTarget:   job.InvokeTarget,
                    Name:           job.JobName,
                    JobId:          job.JobId,
                    CronExpression: job.CronExpression,
                    Args:           job.Args,
                },
            })
        } else {
            AddExecJob(&ExecJob{
                JobCore: JobCore{
                    InvokeTarget:   job.InvokeTarget,
                    Name:           job.JobName,
                    JobId:          job.JobId,
                    CronExpression: job.CronExpression,
                    Args:           job.Args,
                },
            })
        }
    }
}

// AddExecJob 添加本地函数任务
func AddExecJob(job *ExecJob) {
    c := sdk.Runtime.GetCrontab("")
    entryId, err := c.AddJob(job.CronExpression, job)
    if err != nil {
        log.Errorf("AddExecJob error: %s", err)
        return
    }
    job.EntryId = int(entryId)
    log.Infof("AddExecJob success, JobId: %d, EntryId: %d", job.JobId, job.EntryId)
}

// RemoveJob 移除任务
func RemoveJob(entryId int) {
    c := sdk.Runtime.GetCrontab("")
    c.Remove(cron.EntryID(entryId))
}
```

#### 2.3 任务示例 (examples.go)

```go
type ExampleJob struct{}

func (e ExampleJob) Exec(arg interface{}) error {
    str := time.Now().Format(timeFormat)
    log.Infof("ExampleJob Exec success, at %s", str)
    return nil
}
```

**任务管理功能**:
- 创建/编辑/删除任务
- 启用/停用任务
- 立即执行任务
- 查看任务日志

### 3. app/other - 其他功能模块

#### 3.1 代码生成器 (apis/tools/gen.go)

**职责**: 根据数据库表结构自动生成 CRUD 代码。

**生成内容**:
- Model 文件
- API 文件
- Service 文件
- Router 文件
- DTO 文件
- Vue 页面（配合前端）

**使用流程**:
1. 选择数据库表
2. 配置生成选项（模块名、包名、作者等）
3. 预览生成代码
4. 下载或直接生成到项目

#### 3.2 文件上传 (apis/file.go)

**职责**: 处理文件上传和存储。

**支持的存储方式**:
- 本地文件系统
- 阿里云 OSS
- 腾讯云 COS
- 七牛云

#### 3.3 服务器监控 (apis/sys_server_monitor.go)

**职责**: 监控服务器资源使用情况。

**监控指标**:
- CPU 使用率
- 内存使用率
- 磁盘使用率
- 网络流量

---

## 初始化流程详解

### 完整启动时序图

```
main.go::main()
   ↓
cmd.Execute()
   ↓
StartCmd.PreRun → setup()
   ↓
┌──────────────────────────────────────────────────────────────┐
│ 第一阶段：配置加载                                           │
└──────────────────────────────────────────────────────────────┘
config.ExtendConfig = &ext.ExtConfig  (注入扩展配置)
   ↓
config.Setup(file.NewSource(...), database.Setup, storage.Setup)
   ├─ 1. 创建文件源
   │    file.NewSource(file.WithPath("config/settings.yml"))
   │
   ├─ 2. 创建配置对象
   │    config.NewConfig(config.WithSource(fileSource))
   │
   ├─ 3. 加载配置实体 _cfg
   │    ├─ Logger.Setup() 【日志初始化】
   │    │    └─ zap.NewLogger() 创建 Zap 日志器
   │    │
   │    ├─ multiDatabase() 【合并数据库配置】
   │    │
   │    └─ _cfg.OnChange() 【配置变更回调】
   │
   ├─ 4. 执行回调: database.Setup() 【数据库初始化】
   │    └─ for each DatabasesConfig:
   │         ├─ toolsDB.NewConfigure() 【连接池配置】
   │         ├─ gorm.Open() 【创建 GORM 实例】 ⚡ GORM 耦合点
   │         ├─ mycasbin.Setup() 【Casbin 权限引擎】
   │         ├─ sdk.Runtime.SetDb(host, db)
   │         └─ sdk.Runtime.SetCasbin(host, e)
   │
   └─ 5. 执行回调: storage.Setup() 【存储初始化】
        ├─ setupCache() 【缓存适配器】
        │    └─ sdk.Runtime.SetCacheAdapter()
        ├─ setupCaptcha() 【验证码存储】
        │    └─ captcha.SetStore()
        └─ setupQueue() 【队列适配器】
             ├─ sdk.Runtime.SetQueueAdapter()
             └─ go queueAdapter.Run() 【启动队列消费】
   ↓
┌──────────────────────────────────────────────────────────────┐
│ 第二阶段：队列消费者注册                                     │
└──────────────────────────────────────────────────────────────┘
queue := sdk.Runtime.GetMemoryQueue("")
queue.Register(global.LoginLog, models.SaveLoginLog)
queue.Register(global.OperateLog, models.SaveOperaLog)
queue.Register(global.ApiCheck, models.SaveSysApi)
go queue.Run()  【启动内存队列消费】
   ↓
┌──────────────────────────────────────────────────────────────┐
│ 第三阶段：HTTP 引擎初始化                                    │
└──────────────────────────────────────────────────────────────┘
run() → initRouter()
   ├─ gin.New() 【创建 Gin 引擎】 ⚡ Gin 耦合点
   ├─ sdk.Runtime.SetEngine(h)
   │
   ├─ 全局中间件注册
   │    ├─ common.Sentinel() 【流量控制】
   │    ├─ common.RequestId() 【请求 ID】
   │    └─ api.SetRequestLogger 【请求日志】
   │
   └─ common.InitMiddleware(r) 【业务中间件】
        ├─ r.Use(DemoEvn())
        ├─ r.Use(WithContextDb) 【DB 注入上下文】 ⚡ GORM 耦合点
        ├─ r.Use(LoggerToFile())
        ├─ r.Use(CustomError)
        ├─ r.Use(NoCache)
        ├─ r.Use(Options) 【CORS】
        ├─ r.Use(Secure)
        │
        └─ sdk.Runtime.SetMiddleware() 【注册业务中间件】
             ├─ JwtTokenCheck → jwt.MiddlewareFunc ⚡ Gin 耦合点
             ├─ RoleCheck → AuthCheckRole()
             └─ PermissionCheck → actions.PermissionAction()
   ↓
┌──────────────────────────────────────────────────────────────┐
│ 第四阶段：路由注册                                           │
└──────────────────────────────────────────────────────────────┘
for _, f := range AppRouters {
    f()  // 执行 router.InitRouter()
}
   ↓
router.InitRouter()
   ├─ authMiddleware := common.AuthInit() 【JWT 中间件初始化】
   │    └─ jwt.New(&jwt.GinJWTMiddleware{
   │           Authenticator: ...,  【登录认证】
   │           Authorizator: ...,   【权限校验】
   │           PayloadFunc: ...,    【生成 Payload】
   │           Unauthorized: ...,   【未授权处理】
   │        })
   │
   ├─ InitSysRouter(r, authMiddleware) 【系统路由】
   │    ├─ 公共路由 (无认证)
   │    │    ├─ POST /login 【登录】
   │    │    ├─ GET /captcha 【验证码】
   │    │    └─ GET /swagger/* 【API 文档】
   │    │
   │    └─ 认证路由 (需要 JWT)
   │         ├─ /sys-user 【用户管理】
   │         ├─ /sys-role 【角色管理】
   │         ├─ /sys-menu 【菜单管理】
   │         ├─ /sys-dept 【部门管理】
   │         ├─ /sys-post 【岗位管理】
   │         ├─ /sys-dict 【字典管理】
   │         ├─ /sys-config 【参数配置】
   │         ├─ /sys-api 【API 管理】
   │         ├─ /sys-login-log 【登录日志】
   │         └─ /sys-opera-log 【操作日志】
   │
   └─ InitExamplesRouter(r, authMiddleware) 【业务路由】
        └─ ... 业务模块路由
   ↓
sdk.Runtime.SetRouter() 【记录所有路由信息，用于 API 管理】
   ↓
┌──────────────────────────────────────────────────────────────┐
│ 第五阶段：HTTP 服务器启动                                    │
└──────────────────────────────────────────────────────────────┘
srv := &http.Server{
    Addr:         ":8000",
    Handler:      sdk.Runtime.GetEngine(), 【获取 Gin 引擎】
    ReadTimeout:  60 * time.Second,
    WriteTimeout: 60 * time.Second,
}
   ↓
go srv.ListenAndServe() 【启动 HTTP 服务】
   ↓
┌──────────────────────────────────────────────────────────────┐
│ 第六阶段：后台任务启动                                       │
└──────────────────────────────────────────────────────────────┘
go func() {
    jobs.InitJob() 【初始化任务注册表】
    jobs.Setup(sdk.Runtime.GetDb()) 【从数据库加载任务】
         ├─ 查询启用的任务
         ├─ 创建 Cron 实例
         ├─ 添加任务到 Cron
         └─ c.Start() 【启动调度器】
}()
   ↓
┌──────────────────────────────────────────────────────────────┐
│ 第七阶段：API 接口检查 (可选)                                │
└──────────────────────────────────────────────────────────────┘
if apiCheck {
    routers := sdk.Runtime.GetRouter()
    message := sdk.Runtime.GetStreamMessage("", global.ApiCheck, routers)
    queue.Append(message) 【将路由信息写入队列，异步保存到数据库】
}
   ↓
┌──────────────────────────────────────────────────────────────┐
│ 第八阶段：等待优雅关闭                                       │
└──────────────────────────────────────────────────────────────┘
quit := make(chan os.Signal, 1)
signal.Notify(quit, os.Interrupt)
<-quit 【阻塞等待 Ctrl+C】
   ↓
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
srv.Shutdown(ctx) 【优雅关闭服务器】
   ├─ 停止接收新请求
   ├─ 等待现有请求完成（最多 5 秒）
   └─ 关闭监听端口
```

### 关键初始化顺序

1. **配置 > 日志 > 数据库 > 存储 > 队列**
2. **数据库** 和 **存储** 可并行初始化（实际是串行）
3. **HTTP 引擎** 在所有后端组件就绪后初始化
4. **后台任务** 与 **HTTP 服务** 并行启动

### 依赖关系图

```
                     ┌──────────┐
                     │  config  │ (配置加载)
                     └────┬─────┘
                          │
                ┌─────────┴─────────┐
                │                   │
         ┌──────▼──────┐    ┌──────▼──────┐
         │   logger    │    │   errors    │
         └──────┬──────┘    └─────────────┘
                │
      ┌─────────┼─────────┐
      │         │         │
┌─────▼────┐ ┌─▼────┐ ┌──▼───────┐
│ database │ │ cache│ │  queue   │
└─────┬────┘ └──┬───┘ └──┬───────┘
      │         │        │
      └─────────┼────────┘
                │
         ┌──────▼──────┐
         │ sdk.Runtime │ (全局运行时)
         └──────┬──────┘
                │
      ┌─────────┼─────────┐
      │         │         │
┌─────▼────┐ ┌─▼────┐ ┌──▼──────┐
│   Gin    │ │ Jobs │ │ Casbin  │
│  Engine  │ │ Cron │ │Enforcer │
└──────────┘ └──────┘ └─────────┘
```

---

## 框架耦合点分析

### 1. Gin 框架耦合点

#### 1.1 高度耦合区域

##### 1.1.1 common/apis/api.go

```go
type Api struct {
    Context *gin.Context  // 直接依赖 gin.Context 【强耦合】
    // ...
}

func (e *Api) MakeContext(c *gin.Context) *Api
func (e *Api) Bind(d interface{}, bindings ...binding.Binding) *Api {
    // 使用 gin.Binding 接口
    err := e.Context.ShouldBindWith(d, bindings[i])
}
```

**影响范围**: 所有 API 控制器（app/admin/apis、app/jobs/apis、app/other/apis）

##### 1.1.2 common/middleware/*.go

```go
// 所有中间件都是 gin.HandlerFunc 类型
func LoggerToFile() gin.HandlerFunc {
    return func(c *gin.Context) {
        // ...
    }
}

func WithContextDb(c *gin.Context) {
    // 将 DB 注入 gin.Context
    c.Set("db", db)
    c.Next()
}
```

**影响范围**: 所有中间件（common/middleware）

##### 1.1.3 app/*/router/*.go

```go
func registerSysUserRouter(v1 *gin.RouterGroup, authMiddleware *jwt.GinJWTMiddleware) {
    api := apis.SysUser{}
    r := v1.Group("/sys-user")
    r.GET("", api.GetPage)  // api.GetPage 签名必须是 func(c *gin.Context)
}
```

**影响范围**: 所有路由文件

#### 1.2 替换 Gin 的成本

**极高难度** 🔴🔴🔴🔴🔴

**需要修改的地方**:
1. 所有 API 控制器（100+ 文件）
2. 所有中间件（15+ 文件）
3. 所有路由配置（30+ 文件）
4. common/apis/api.go 基类
5. sdk.Runtime 的 Engine 存储

**预估工作量**: 60-80 人天

### 2. GORM 框架耦合点

#### 2.1 高度耦合区域

##### 2.1.1 common/apis/api.go

```go
type Api struct {
    Orm *gorm.DB  // 直接存储 GORM 实例 【强耦合】
}
```

##### 2.1.2 common/service/service.go

```go
type Service struct {
    Orm *gorm.DB  // 直接存储 GORM 实例 【强耦合】
}
```

##### 2.1.3 所有 Service 层

```go
func (e *SysUser) GetPage(...) error {
    err := e.Orm.Preload("Dept").  // 使用 GORM 链式 API
        Scopes(
            cDto.MakeCondition(...),
            cDto.Paginate(...),
            actions.Permission(...),
        ).
        Find(list).Count(count).Error
}
```

##### 2.1.4 common/actions/permission.go

```go
// Permission 返回 GORM Scope 函数
func Permission(tableName string, p *DataPermission) func(db *gorm.DB) *gorm.DB {
    return func(db *gorm.DB) *gorm.DB {
        // 使用 GORM Where 方法
        return db.Where(...)
    }
}
```

##### 2.1.5 common/database/initialize.go

```go
func setupSimpleDatabase(...) {
    db, err := resolverConfig.Init(&gorm.Config{...}, opens[c.Driver])
    // 深度使用 GORM 配置
}
```

#### 2.2 替换 GORM 的成本

**极高难度** 🔴🔴🔴🔴🔴

**需要修改的地方**:
1. 所有 Service 层（100+ 文件）
2. 所有 Model 层（50+ 文件）
3. common/apis/api.go 基类
4. common/service/service.go 基类
5. common/actions/* 所有 Action
6. common/database/initialize.go
7. common/dto/* 动态查询构建器
8. sdk.Runtime 的 DB 存储

**预估工作量**: 80-120 人天

### 3. Viper 耦合点

**结论**: **go-admin 不使用 Viper** ✅

使用的是 **go-admin-core/config** 自研配置框架。

**优势**:
- 轻量级，依赖少
- 自定义性强
- 配置变更回调机制

**劣势**:
- 社区支持不如 Viper
- 功能相对简单

### 4. 其他框架耦合点

#### 4.1 JWT 认证 (jwt-go)

**耦合度**: 🟡 中等

**位置**: common/middleware/auth.go, sdk/pkg/jwtauth

**替换难度**: 中等（3-5 人天）

#### 4.2 Casbin 权限

**耦合度**: 🟡 中等

**位置**: common/database/initialize.go, sdk/pkg/casbin

**替换难度**: 中等（5-8 人天）

#### 4.3 Cron 定时任务

**耦合度**: 🟢 低

**位置**: app/jobs/jobbase.go

**替换难度**: 低（2-3 人天）

#### 4.4 Redis (缓存/队列)

**耦合度**: 🟢 低（通过适配器模式）

**位置**: storage 包

**替换难度**: 低（2-3 人天）

### 框架耦合度矩阵

| 框架 | 耦合度 | 影响文件数 | 替换难度 | 预估工作量 |
|------|--------|-----------|---------|-----------|
| **Gin** | 🔴 极高 | 150+ | 极难 | 60-80 人天 |
| **GORM** | 🔴 极高 | 200+ | 极难 | 80-120 人天 |
| **Viper** | 🟢 无 | 0 | - | - |
| JWT | 🟡 中 | 10+ | 中 | 3-5 人天 |
| Casbin | 🟡 中 | 15+ | 中 | 5-8 人天 |
| Cron | 🟢 低 | 5+ | 低 | 2-3 人天 |
| Redis | 🟢 低 | 10+ | 低 | 2-3 人天 |

---

## 中间件体系

### 中间件执行顺序

```
请求进入
   ↓
1. TlsHandler (可选)          - HTTPS 重定向
   ↓
2. Sentinel                   - 流量控制（限流、熔断）
   ↓
3. RequestId                  - 生成请求 ID (X-Request-Id)
   ↓
4. SetRequestLogger           - 设置请求日志 (绑定到上下文)
   ↓
5. DemoEvn                    - 演示环境限制（禁止 POST/PUT/DELETE）
   ↓
6. WithContextDb              - 数据库注入上下文 (c.Set("db", db))
   ↓
7. LoggerToFile               - 日志记录到文件
   ↓
8. CustomError                - 自定义错误处理（统一错误响应）
   ↓
9. NoCache                    - 禁用浏览器缓存
   ↓
10. Options                   - CORS 跨域处理
   ↓
11. Secure                    - 安全头 (XSS、MIME、Frame)
   ↓
--- 路由级别中间件 ---
   ↓
12. JwtTokenCheck (可选)      - JWT 认证
   ↓
13. RoleCheck (可选)          - 角色校验
   ↓
14. PermissionCheck (可选)    - 权限校验 (数据权限)
   ↓
--- 业务处理器 ---
   ↓
Controller Handler
   ↓
响应返回
```

### 核心中间件详解

#### 1. WithContextDb - 数据库注入

```go
func WithContextDb(c *gin.Context) {
    // 从 Runtime 获取默认数据库
    db := sdk.Runtime.GetDbByKey("")
    
    // 注入到 gin.Context
    c.Set("db", db)
    c.Next()
}

// 在 API 中使用
func (e *Api) MakeOrm() *Api {
    e.Orm, err = pkg.GetOrm(e.Context)  // 从上下文获取
    return e
}
```

**设计意图**:
- 避免全局变量
- 支持多数据库切换
- 便于单元测试（Mock DB）

#### 2. LoggerToFile - 日志记录

```go
func LoggerToFile() gin.HandlerFunc {
    return func(c *gin.Context) {
        startTime := time.Now()
        
        c.Next()  // 执行后续中间件和处理器
        
        // 记录请求日志
        latency := time.Since(startTime)
        statusCode := c.Writer.Status()
        clientIP := c.ClientIP()
        method := c.Request.Method
        path := c.Request.URL.Path
        
        log.Infof("| %3d | %13v | %15s | %-7s %s",
            statusCode,
            latency,
            clientIP,
            method,
            path,
        )
        
        // 异步写入操作日志到队列
        if statusCode != 200 || method != "GET" {
            queue := sdk.Runtime.GetMemoryQueue("")
            message := sdk.Runtime.GetStreamMessage("", global.OperateLog, map[string]interface{}{
                "method":      method,
                "path":        path,
                "status_code": statusCode,
                "latency":     latency.Milliseconds(),
                "client_ip":   clientIP,
                "user_id":     user.GetUserId(c),
            })
            queue.Append(message)
        }
    }
}
```

#### 3. CustomError - 错误处理

```go
func CustomError(c *gin.Context) {
    defer func() {
        if err := recover(); err != nil {
            // 捕获 panic
            log.Errorf("panic: %v", err)
            
            // 返回统一错误响应
            response.Error(c, 500, fmt.Errorf("%v", err), "服务器内部错误")
            c.Abort()
        }
    }()
    
    c.Next()
    
    // 检查是否有错误
    if len(c.Errors) > 0 {
        err := c.Errors.Last()
        log.Error(err)
        response.Error(c, 500, err, err.Error())
    }
}
```

#### 4. JwtTokenCheck - JWT 认证

```go
authMiddleware, _ := jwt.New(&jwt.GinJWTMiddleware{
    Realm:           "go-admin",
    Key:             []byte(config.ApplicationConfig.JwtSecret),
    Timeout:         time.Hour * 24,
    MaxRefresh:      time.Hour * 24,
    IdentityKey:     "userId",
    
    // 登录认证
    Authenticator: func(c *gin.Context) (interface{}, error) {
        var loginVals dto.LoginReq
        if err := c.ShouldBind(&loginVals); err != nil {
            return "", jwt.ErrMissingLoginValues
        }
        
        // 验证验证码
        if !captcha.Verify(loginVals.UUID, loginVals.Code, true) {
            return nil, errors.New("验证码错误")
        }
        
        // 验证用户名密码
        user, err := service.Login(&loginVals)
        if err != nil {
            return nil, err
        }
        
        return user, nil
    },
    
    // 生成 Payload
    PayloadFunc: func(data interface{}) jwt.MapClaims {
        if v, ok := data.(*models.SysUser); ok {
            return jwt.MapClaims{
                "userId":   v.UserId,
                "username": v.Username,
                "roleId":   v.RoleId,
                "deptId":   v.DeptId,
            }
        }
        return jwt.MapClaims{}
    },
    
    // 权限校验
    Authorizator: func(data interface{}, c *gin.Context) bool {
        // 从 Token 提取用户信息
        if v, ok := data.(jwt.MapClaims); ok {
            userID := int(v["userId"].(float64))
            c.Set("userId", userID)
            return true
        }
        return false
    },
    
    // 未授权处理
    Unauthorized: func(c *gin.Context, code int, message string) {
        response.Error(c, code, nil, message)
    },
    
    TokenLookup:   "header: Authorization, query: token, cookie: jwt",
    TokenHeadName: "Bearer",
    TimeFunc:      time.Now,
})
```

#### 5. AuthCheckRole - 角色校验

```go
func AuthCheckRole() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 获取用户信息
        userId := user.GetUserId(c)
        
        // 超级管理员跳过校验
        if userId == 1 {
            c.Next()
            return
        }
        
        // 获取用户角色
        db, _ := pkg.GetOrm(c)
        var roleIds []int
        db.Table("sys_user").
            Select("role_id").
            Where("user_id = ?", userId).
            Pluck("role_id", &roleIds)
        
        // 检查角色是否有权限访问该路径
        enforcer := sdk.Runtime.GetCasbin("")
        path := c.Request.URL.Path
        method := c.Request.Method
        
        for _, roleId := range roleIds {
            if enforcer.Enforce(fmt.Sprintf("role_%d", roleId), path, method) {
                c.Next()
                return
            }
        }
        
        response.Error(c, 403, nil, "无权限访问")
        c.Abort()
    }
}
```

#### 6. PermissionAction - 数据权限

**见 [数据权限系统](#数据权限系统) 章节**

---

## 数据权限系统

### 数据权限模型

```
用户 (User)
  ├─ 角色 (Role)
  │    ├─ 数据权限范围 (DataScope)
  │    │    ├─ 1 = 全部数据权限
  │    │    ├─ 2 = 自定义数据权限 (指定部门)
  │    │    ├─ 3 = 本部门数据权限
  │    │    ├─ 4 = 本部门及以下数据权限
  │    │    └─ 5 = 仅本人数据权限
  │    └─ 角色部门关联表 (sys_role_dept)
  └─ 部门 (Dept)
       └─ 部门路径 (dept_path) 例: /1/2/3/
```

### 实现原理

#### 1. 权限信息查询

```go
func newDataPermission(tx *gorm.DB, userId interface{}) (*DataPermission, error) {
    p := &DataPermission{}
    
    // 查询用户的数据权限配置
    err := tx.Table("sys_user").
        Select("sys_user.user_id, sys_user.dept_id, sys_role.role_id, sys_role.data_scope").
        Joins("left join sys_role on sys_role.role_id = sys_user.role_id").
        Where("sys_user.user_id = ?", userId).
        First(p).Error
    
    return p, err
}
```

#### 2. GORM Scope 实现

```go
func Permission(tableName string, p *DataPermission) func(db *gorm.DB) *gorm.DB {
    return func(db *gorm.DB) *gorm.DB {
        if p == nil {
            return db
        }
        
        switch p.DataScope {
        case "1": // 全部数据权限
            return db
            
        case "2": // 自定义数据权限
            // 查询角色关联的部门，再查询这些部门的用户创建的数据
            return db.Where(
                tableName+".create_by in (select sys_user.user_id from sys_user where sys_user.dept_id in (select dept_id from sys_role_dept where role_id = ?))",
                p.RoleId,
            )
            
        case "3": // 本部门数据权限
            return db.Where(
                tableName+".create_by in (select user_id from sys_user where dept_id = ?)",
                p.DeptId,
            )
            
        case "4": // 本部门及以下数据权限
            // 使用 dept_path 实现层级查询
            return db.Where(
                tableName+".create_by in (select user_id from sys_user where dept_id in (select dept_id from sys_dept where dept_path like ?))",
                "%/"+strconv.Itoa(p.DeptId)+"/%",
            )
            
        case "5": // 仅本人数据权限
            return db.Where(tableName+".create_by = ?", p.UserId)
            
        default:
            return db
        }
    }
}
```

#### 3. 使用示例

```go
// 在 Service 层使用
func (e *SysUser) GetPage(c *dto.SysUserGetPageReq, p *actions.DataPermission, list *[]models.SysUser, count *int64) error {
    var data models.SysUser
    
    err := e.Orm.Preload("Dept").
        Scopes(
            cDto.MakeCondition(c.GetNeedSearch()),
            cDto.Paginate(c.GetPageSize(), c.GetPageIndex()),
            actions.Permission(data.TableName(), p),  // 应用数据权限
        ).
        Find(list).Limit(-1).Offset(-1).
        Count(count).Error
    
    return err
}
```

### 数据权限配置流程

1. **创建部门**: 配置部门层级结构
2. **创建角色**: 分配数据权限范围
3. **角色关联部门** (可选): 自定义数据权限时配置
4. **用户分配角色**: 用户继承角色的数据权限

### 数据权限场景示例

假设组织结构如下:

```
总公司 (ID: 1, Path: /1/)
  ├─ 研发部 (ID: 2, Path: /1/2/)
  │    ├─ 前端组 (ID: 3, Path: /1/2/3/)
  │    └─ 后端组 (ID: 4, Path: /1/2/4/)
  └─ 销售部 (ID: 5, Path: /1/5/)
       ├─ 华北区 (ID: 6, Path: /1/5/6/)
       └─ 华南区 (ID: 7, Path: /1/5/7/)
```

**用户 A**: 研发部经理，数据权限范围 = "4" (本部门及以下)
- 可查看: 研发部、前端组、后端组的数据

**用户 B**: 前端组长，数据权限范围 = "3" (本部门)
- 可查看: 前端组的数据

**用户 C**: 普通开发，数据权限范围 = "5" (仅本人)
- 可查看: 自己创建的数据

**用户 D**: 总经理，数据权限范围 = "1" (全部)
- 可查看: 所有数据

---

## 后台任务系统

### 任务类型

#### 1. HTTP 任务

**用途**: 定时调用外部 HTTP 接口。

```go
type HttpJob struct {
    JobCore
}

func (h *HttpJob) Run() {
    startTime := time.Now()
    
    // 发送 HTTP 请求
    resp, err := http.Get(h.InvokeTarget)
    if err != nil {
        recordJobLog(h.JobId, h.Name, startTime, err, "failed")
        return
    }
    defer resp.Body.Close()
    
    recordJobLog(h.JobId, h.Name, startTime, nil, "success")
}
```

**配置示例**:
- 任务名称: 数据同步
- 任务类型: http
- 调用目标: https://api.example.com/sync
- Cron 表达式: `0 0 2 * * ?` (每天凌晨2点)

#### 2. 本地函数任务

**用途**: 定时执行本地 Go 函数。

```go
type ExecJob struct {
    JobCore
}

func (e *ExecJob) Run() {
    startTime := time.Now()
    
    // 从注册表获取任务函数
    var obj = jobList[e.InvokeTarget]
    if obj == nil {
        log.Warn("[Job] ExecJob Run job nil")
        return
    }
    
    // 执行任务
    err := CallExec(obj.(JobExec), e.Args)
    if err != nil {
        recordJobLog(e.JobId, e.Name, startTime, err, "failed")
        return
    }
    
    recordJobLog(e.JobId, e.Name, startTime, nil, "success")
}
```

**配置示例**:
- 任务名称: 数据清理
- 任务类型: exec
- 调用目标: CleanOldData (函数名)
- 参数: `{"days": 30}`
- Cron 表达式: `0 0 3 * * ?` (每天凌晨3点)

### 任务注册

```go
// 1. 定义任务结构体
type CleanOldDataJob struct{}

func (e CleanOldDataJob) Exec(arg interface{}) error {
    // 解析参数
    params := arg.(map[string]interface{})
    days := int(params["days"].(float64))
    
    // 执行清理逻辑
    db := sdk.Runtime.GetDb()
    result := db.Where("create_time < ?", time.Now().AddDate(0, 0, -days)).
        Delete(&models.SysOperaLog{})
    
    log.Infof("CleanOldDataJob: deleted %d records", result.RowsAffected)
    return nil
}

// 2. 注册到任务列表
func InitJob() {
    jobList = map[string]JobExec{
        "ExampleJob":      ExampleJob{},
        "CleanOldData":    CleanOldDataJob{},  // 新增任务
    }
}
```

### 任务管理 API

```go
// 创建任务
POST /api/v1/sys-job
{
    "jobName": "数据清理",
    "jobType": "exec",
    "invokeTarget": "CleanOldData",
    "cronExpression": "0 0 3 * * ?",
    "args": "{\"days\": 30}",
    "status": "1"
}

// 启动/停止任务
PUT /api/v1/sys-job/{id}/status

// 立即执行任务
POST /api/v1/sys-job/{id}/run

// 查看任务日志
GET /api/v1/sys-job/{id}/log
```

### Cron 表达式

| 表达式 | 说明 |
|--------|------|
| `0 0 0 * * ?` | 每天午夜 |
| `0 0 2 * * ?` | 每天凌晨2点 |
| `0 0/5 * * * ?` | 每5分钟 |
| `0 0 12 * * MON-FRI` | 工作日中午12点 |
| `0 0 0 1 * ?` | 每月1号午夜 |

---

## 设计模式分析

### 1. 单例模式 (Singleton)

**应用**: `sdk.Runtime` 全局运行时对象

```go
var (
    _runtime *runtime.Application
)

func Runtime() *runtime.Application {
    if _runtime == nil {
        _runtime = &runtime.Application{}
    }
    return _runtime
}
```

**优点**:
- 全局唯一访问点
- 避免重复初始化

**缺点**:
- 全局状态，不利于单元测试
- 并发安全需要额外处理

### 2. 工厂模式 (Factory)

**应用**: 数据库驱动选择

```go
var opens = map[string]func() gorm.Dialector{
    "mysql":    driver.Mysql,
    "postgres": driver.Postgres,
    "sqlite":   driver.Sqlite,
    "sqlserver": driver.SqlServer,
}

func getDialector(driver string) gorm.Dialector {
    return opens[driver]()
}
```

### 3. 适配器模式 (Adapter)

**应用**: 存储适配器（缓存/队列）

```go
type AdapterCache interface {
    String() string
    Get(key string) (string, error)
    Set(key string, val interface{}, expire int) error
    Del(key string) error
}

// Redis 适配器
type Redis struct {
    client *redis.Client
}

func (r *Redis) Get(key string) (string, error) {
    return r.client.Get(context.Background(), key).Result()
}

// 内存适配器
type Memory struct {
    data map[string]interface{}
}

func (m *Memory) Get(key string) (string, error) {
    return m.data[key].(string), nil
}
```

### 4. 模板方法模式 (Template Method)

**应用**: common/actions 通用 CRUD

```go
type CreateAction struct {
    Control  *gin.Context
    Service  CreateResp
    Business CreateBus  // 业务钩子
}

type CreateBus interface {
    BeforeInsert(c *gin.Context, e interface{}) error  // 前置钩子
    AfterInsert(c *gin.Context, e interface{}) error   // 后置钩子
}

func (e CreateAction) Action() {
    // 1. 参数绑定
    // 2. 调用 BeforeInsert
    // 3. 执行插入
    // 4. 调用 AfterInsert
    // 5. 返回响应
}
```

### 5. 观察者模式 (Observer)

**应用**: 配置变更监听

```go
type Config interface {
    Watch(path ...string) (Watcher, error)
}

type Watcher interface {
    Next() (*ChangeSet, error)
    Stop() error
}

// 使用示例
w, _ := config.Watch("database")
go func() {
    for {
        v, err := w.Next()
        if err != nil {
            return
        }
        // 处理配置变更
        onDatabaseConfigChange(v)
    }
}()
```

### 6. 策略模式 (Strategy)

**应用**: 数据权限策略

```go
func Permission(tableName string, p *DataPermission) func(db *gorm.DB) *gorm.DB {
    return func(db *gorm.DB) *gorm.DB {
        switch p.DataScope {
        case "1": return allDataStrategy(db)
        case "2": return customDataStrategy(db, p)
        case "3": return deptDataStrategy(db, p)
        case "4": return deptAndBelowStrategy(db, p)
        case "5": return selfDataStrategy(db, p)
        }
    }
}
```

### 7. 装饰器模式 (Decorator)

**应用**: 中间件链

```go
r.Use(Sentinel()).
  Use(RequestId()).
  Use(SetRequestLogger).
  Use(WithContextDb).
  Use(LoggerToFile()).
  Use(CustomError)
```

### 8. 责任链模式 (Chain of Responsibility)

**应用**: Gin 中间件链

```go
func AuthCheckRole() gin.HandlerFunc {
    return func(c *gin.Context) {
        if !checkRole(c) {
            c.Abort()  // 中断责任链
            return
        }
        c.Next()  // 继续下一个处理器
    }
}
```

---

## 优缺点评估

### 优点

#### 1. 分层清晰 ✅
- **四层架构**: Router → API → Service → Model
- **职责明确**: 每层有清晰的职责边界
- **易于维护**: 修改某一层不影响其他层

#### 2. 代码生成 ✅
- **提高效率**: 自动生成 CRUD 代码
- **标准化**: 生成的代码遵循统一规范
- **降低错误**: 减少手工编码错误

#### 3. 权限体系完善 ✅
- **RBAC**: 基于角色的访问控制
- **数据权限**: 细粒度的数据访问控制
- **Casbin 集成**: 灵活的权限策略

#### 4. 插件化设计 ✅
- **存储适配器**: 支持多种缓存/队列实现
- **日志适配器**: 支持多种日志库
- **易于扩展**: 通过接口扩展新功能

#### 5. 配置管理 ✅
- **热更新**: 配置文件变更自动重载
- **多环境**: 支持开发/测试/生产环境配置
- **扩展性**: 自定义配置扩展

#### 6. 完善的中间件 ✅
- **流量控制**: Sentinel 限流熔断
- **日志追踪**: 请求 ID + 日志记录
- **错误处理**: 统一错误响应格式
- **安全防护**: CORS、XSS、CSRF

#### 7. 后台任务 ✅
- **Cron 调度**: 灵活的定时任务
- **任务管理**: Web 界面管理任务
- **日志记录**: 任务执行日志

### 缺点

#### 1. 框架强耦合 ❌
- **Gin**: API 层直接依赖 gin.Context
- **GORM**: Service 层直接依赖 gorm.DB
- **替换成本**: 框架替换需要大量改动

**改进建议**: 引入抽象层，定义统一接口
```go
type Context interface {
    Bind(interface{}) error
    JSON(int, interface{})
}

type DB interface {
    Query(dest interface{}, query string, args ...interface{}) error
}
```

#### 2. 全局状态 ❌
- **sdk.Runtime**: 全局单例
- **不利于测试**: 并发测试时状态污染
- **隐式依赖**: 难以追踪依赖关系

**改进建议**: 引入依赖注入
```go
type Container struct {
    DB     *gorm.DB
    Cache  storage.AdapterCache
    Logger logger.Logger
}

func NewUserAPI(c *Container) *UserAPI {
    return &UserAPI{
        db:     c.DB,
        cache:  c.Cache,
        logger: c.Logger,
    }
}
```

#### 3. 过度封装 ❌
- **基类强制继承**: Api/Service 必须继承基类
- **链式调用**: MakeContext().MakeOrm().Bind() 可读性差
- **灵活性降低**: 难以定制特殊逻辑

**改进建议**: 使用组合而非继承
```go
type UserAPI struct {
    ctx    *Context
    db     *DB
    logger *Logger
}

func (api *UserAPI) GetPage(c *gin.Context) {
    req := &dto.UserGetPageReq{}
    if err := c.ShouldBind(req); err != nil {
        api.Error(c, err)
        return
    }
    // ...
}
```

#### 4. 错误处理不统一 ❌
- **Api.Errors**: 错误累积但没有强制检查
- **容易遗漏**: 忘记检查 Errors 导致错误被忽略
- **panic 风险**: 空指针等错误可能导致 panic

**改进建议**: 使用 Go 标准错误处理
```go
func (api *UserAPI) GetPage(c *gin.Context) error {
    req := &dto.UserGetPageReq{}
    if err := c.ShouldBind(req); err != nil {
        return err
    }
    
    list, err := api.service.GetPage(req)
    if err != nil {
        return err
    }
    
    return api.OK(c, list)
}
```

#### 5. 缺少单元测试 ❌
- **测试覆盖率低**: 大部分代码没有单元测试
- **依赖真实数据库**: 测试依赖真实环境
- **难以 Mock**: 全局状态难以 Mock

**改进建议**: 
- 使用 testify/mock 或 gomock
- 引入依赖注入便于 Mock
- 使用 SQLite 或内存数据库测试

#### 6. 文档不足 ❌
- **代码注释少**: 复杂逻辑缺少注释
- **架构文档缺失**: 缺少整体架构说明
- **API 文档**: 仅有 Swagger，缺少详细说明

**改进建议**:
- 增加代码注释（特别是公共接口）
- 编写架构设计文档
- 补充 API 使用示例

#### 7. 性能优化不足 ❌
- **N+1 查询**: 关联查询可能存在 N+1 问题
- **缓存策略**: 缓存使用不够充分
- **数据库索引**: 缺少索引优化建议

**改进建议**:
- 使用 GORM Preload 避免 N+1
- 增加查询缓存
- 数据库字段添加索引

### 适用场景

#### 适合

✅ **中小型企业管理系统**
- 用户数 < 10万
- 业务逻辑中等复杂度
- 团队规模 3-10 人

✅ **快速原型开发**
- 代码生成快速搭建 CRUD
- 内置权限系统
- 开箱即用

✅ **学习 Go Web 开发**
- 完整的项目结构
- 常见技术栈集成
- 最佳实践参考

#### 不适合

❌ **大型分布式系统**
- 全局状态不适合分布式
- 框架强耦合难以微服务化

❌ **高性能实时系统**
- ORM 性能开销较大
- 中间件链较长

❌ **多框架混用项目**
- 强依赖 Gin 和 GORM
- 框架替换成本高

---

## 总结

### 技术栈概览

| 层次 | 技术选型 | 耦合度 |
|------|---------|--------|
| Web 框架 | Gin | 🔴 高 |
| ORM 框架 | GORM | 🔴 高 |
| 配置管理 | go-admin-core/config (自研) | 🟢 低 |
| 日志框架 | Zap | 🟢 低 |
| 权限管理 | Casbin | 🟡 中 |
| 任务调度 | Cron | 🟢 低 |
| 缓存/队列 | Redis (适配器模式) | 🟢 低 |
| JWT 认证 | jwt-go | 🟡 中 |

### 核心特点

1. **四层架构**: Router → API → Service → Model
2. **数据权限**: 5 种数据权限范围（全部/自定义/本部门/本部门及以下/仅本人）
3. **代码生成**: 自动生成 CRUD 代码
4. **后台任务**: 支持 HTTP 和本地函数任务
5. **中间件体系**: 完善的中间件链（认证/鉴权/日志/错误处理）

### 最佳实践

1. **遵循四层架构**: 不要跨层调用
2. **使用数据权限**: 通过 actions.Permission 控制数据访问
3. **统一错误处理**: 使用 CustomError 中间件
4. **日志异步写入**: 使用队列异步写入日志
5. **代码生成**: 利用代码生成器提高效率
6. **定时任务**: 使用后台任务执行定期任务

### 改进方向

1. **引入依赖注入**: 降低全局状态依赖
2. **抽象框架接口**: 降低 Gin/GORM 耦合度
3. **增加单元测试**: 提高代码质量
4. **完善文档**: 增加代码注释和架构文档
5. **性能优化**: 缓存策略、数据库索引
6. **微服务化**: 拆分为独立服务

---

**文档生成时间**: 2026年1月23日  
**分析版本**: go-admin v2.2.0  
**作者**: AI Assistant  
**关联文档**: [go-admin-core架构分析.md](go-admin-core架构分析.md)
