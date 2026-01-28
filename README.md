# dy-yun - 企业级中后台应用框架

> 基于 FastAPI 框架的企业级 RBAC 权限管理系统

## 架构设计

采用分层设计与模块化理念：

| 层级 | 目录 | 职责 |
|------|------|------|
| 核心框架层 | `core/` | 配置、日志、数据库、缓存、队列、JWT认证 |
| 公共组件层 | `common/` | 中间件、基类、通用操作、数据传输对象 |
| 业务应用层 | `app/` | 业务模块的路由、服务、模型、数据验证 |
| 配置文件 | `config/` | YAML 配置文件 |

## 核心特性

- ✅ **分层架构**: Router → Service → Model 三层清晰分离
- ✅ **中间件体系**: 错误处理、安全头、请求日志、限流、请求追踪
- ✅ **异步优先**: 基于 async/await 的异步数据库和缓存操作
- ✅ **依赖注入**: 通过 FastAPI Depends 实现数据库会话、缓存、日志注入
- ✅ **配置管理**: YAML 配置加载，支持多环境配置切换
- ✅ **JWT认证**: 完整的 Token 认证体系（登录/登出/刷新）
- ✅ **缓存系统**: 支持 Redis 和内存缓存适配器
- ✅ **队列系统**: 支持 Redis Stream 和内存队列适配器
- ✅ **限流控制**: 滑动窗口限流，支持分布式环境
- ✅ **开发友好**: 热重载、API 自动文档、类型提示

## 快速开始

### 环境要求

- Python 3.10+
- PostgreSQL/MySQL (可选 SQLite)
- Redis (可选)

### 安装依赖

```bash
cd dy-yun

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境（Windows）
.\.venv\Scripts\activate

# 激活虚拟环境（Linux/Mac）
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 配置数据库

编辑 `config/settings.yaml`:

```yaml
database:
  driver: sqlite  # mysql, postgresql, sqlite
  host: localhost
  port: 5432
  name: dy_yun
  username: root
  password: ""
  source: "sqlite+aiosqlite:///./dy_yun.db"
```

### 启动服务

```bash
# 默认配置（8000端口）
python main.py

# 使用开发配置（8001端口）
python main.py -c config/settings.dev.yaml

# 指定端口
python main.py --port 9000
```

访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## 项目结构

```
dy-yun/
├── main.py                      # 程序入口
├── pyproject.toml               # 依赖管理
├── requirements.txt             # Pip 依赖列表
├── Dockerfile                   # Docker 镜像
├── docker-compose.yml           # Docker 编排
├── Makefile                     # 快捷命令
│
├── core/                        # 核心框架层
│   ├── __init__.py              # 核心模块导出
│   ├── config/                  # 配置管理
│   │   ├── config.py            # 配置模型定义
│   │   └── loader.py            # 配置加载器
│   ├── database/                # 数据库管理
│   │   ├── base.py              # 模型基类
│   │   └── database.py          # 数据库连接管理
│   ├── logger/                  # 日志系统
│   │   └── logger.py            # Loguru 日志配置
│   ├── runtime/                 # 运行时状态
│   │   └── runtime.py           # 全局状态管理
│   ├── errors/                  # 错误定义
│   │   └── exceptions.py        # 自定义异常
│   ├── jwtauth/                 # JWT 认证模块
│   │   ├── jwt.py               # JWT 核心逻辑
│   │   ├── middleware.py        # JWT 中间件
│   │   └── types.py             # 类型定义
│   └── storage/                 # 存储适配器
│       ├── cache/               # 缓存适配器
│       │   ├── adapter.py       # 缓存接口
│       │   ├── memory.py        # 内存缓存
│       │   └── redis.py         # Redis 缓存
│       └── queue/               # 队列适配器
│           ├── adapter.py       # 队列接口
│           ├── memory.py        # 内存队列
│           └── redis.py         # Redis Stream 队列
│
├── common/                      # 公共组件层
│   ├── __init__.py
│   ├── middleware/              # 中间件
│   │   ├── auth.py              # JWT 认证
│   │   ├── error_handler.py     # 错误处理
│   │   ├── header.py            # 安全头（NoCache, CORS, Secure）
│   │   ├── logger.py            # 请求日志
│   │   ├── rate_limit.py        # 限流控制
│   │   ├── request_id.py        # 请求 ID
│   │   ├── permission.py        # 权限校验
│   │   └── loader.py            # 中间件注册
│   ├── models/                  # 模型基类
│   │   └── model.py             # 审计字段基类
│   ├── services/                # 服务基类
│   │   └── service.py           # Service 基类
│   ├── routers/                 # 路由加载
│   │   └── loader.py            # 路由注册
│   ├── actions/                 # 通用操作
│   │   └── index.py             # 分页查询
│   ├── schemas/                 # 公共 DTO
│   │   ├── pagination.py        # 分页请求/响应
│   │   └── response.py          # 统一响应格式
│   └── storage/                 # 存储初始化
│       └── initialize.py        # 缓存/队列初始化
│
├── app/                         # 业务应用层
│   └── admin/                   # 系统管理模块
│       ├── routers/             # 路由控制器
│       │   ├── sys_user.py      # 用户管理
│       │   ├── cache_test.py    # 缓存测试
│       │   └── queue_test.py    # 队列测试
│       ├── services/            # 业务逻辑
│       │   └── sys_user.py      # 用户服务
│       ├── models/              # 数据模型
│       │   └── sys_user.py      # 用户模型
│       └── schemas/             # 数据传输对象
│           └── sys_user.py      # 用户 DTO
│
├── cmd/                         # 命令行工具
│   └── cli.py                   # CLI 命令
│
├── config/                      # 配置文件
│   ├── settings.yaml            # 默认配置
│   ├── settings.dev.yaml        # 开发环境配置
│   └── extend.py                # 扩展配置
│
├── docs/                        # 文档
│
├── logs/                        # 日志目录
│
└── tests/                       # 测试
    ├── test_api.py              # API 测试
    ├── test_config.py           # 配置测试
    ├── test_headers.py          # 响应头测试
    └── test_rate_limit.py       # 限流测试
```

## 中间件执行顺序

7 层中间件链（从外到内）：

```
Request
  ↓
1. ErrorHandlerMiddleware       # 全局错误捕获和统一响应
  ↓
2. SecureHeadersMiddleware      # 安全响应头（XSS、Frame、CSP）
  ↓
3. OptionsMiddleware            # OPTIONS 请求快速响应
  ↓
4. NoCacheMiddleware            # Cache-Control 头控制
  ↓
5. RequestIdMiddleware          # 生成唯一请求 ID (X-Request-Id)
  ↓
6. LoggerMiddleware             # 请求/响应日志记录
  ↓
7. RateLimitMiddleware          # 滑动窗口限流
  ↓
Router Handler
```

## API 示例

### 登录认证

```bash
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123456"}'
```

### 用户列表（分页）

```bash
curl -X GET "http://localhost:8000/api/sys-users?page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 创建用户

```bash
curl -X POST http://localhost:8000/api/sys-users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"username": "test", "password": "123456", "email": "test@example.com"}'
```

## 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| Web 框架 | FastAPI | 0.128+ |
| 异步 ORM | SQLAlchemy | 2.0+ |
| 数据验证 | Pydantic | 2.12+ |
| 日志 | Loguru | 0.7+ |
| JWT | python-jose | 3.3+ |
| 密码加密 | passlib | 1.7+ |
| 缓存 | Redis（可选） | - |
| 数据库 | SQLite/MySQL/PostgreSQL | - |

## Git Commit 规范

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | feat: 添加用户登录功能 |
| `fix` | 修复 Bug | fix: 修复分页查询越界问题 |
| `docs` | 文档更新 | docs: 更新 README 安装说明 |
| `style` | 代码格式（不影响功能） | style: 格式化代码缩进 |
| `refactor` | 重构（既不是新功能也不是修复） | refactor: 重构用户服务层 |
| `perf` | 性能优化 | perf: 优化数据库查询性能 |
| `test` | 添加或修改测试 | test: 添加用户接口单元测试 |
| `chore` | 构建/工具变动 | chore: 更新依赖版本 |
| `ci` | CI/CD 配置 | ci: 添加 GitHub Actions 工作流 |
| `revert` | 回滚提交 | revert: 回滚 feat: 用户登录功能 |

**提交格式**: `<type>(<scope>): <subject>`

```bash
# 示例
git commit -m "feat(auth): 添加 JWT 刷新 Token 功能"
git commit -m "fix(user): 修复用户列表分页错误"
git commit -m "docs: 更新项目结构说明"
```

## 开发指南

### 添加新模块

1. 在 `app/` 下创建模块目录
2. 定义 Model（`models/`）、Schema（`schemas/`）、Service（`services/`）、Router（`routers/`）
3. 在 `common/routers/loader.py` 中注册路由

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black .
isort .
```

## 许可证

MIT License