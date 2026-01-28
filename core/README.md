# Core 公共代码库说明

本目录提供框架级的公共能力与抽象，面向应用层 `app/` 与通用组件层 `common/`。其职责是统一配置、日志、数据库、运行时资源获取与存储适配，确保各业务模块以一致的方式访问底层能力。

## 模块结构

- `config/`: 配置加载与管理，支持从 YAML 文件读取并合并环境差异。
- `database/`: 数据库连接、会话管理与初始化（ORM/迁移相关能力位于此）。
- `errors/`: 统一错误码与异常类型定义，提供标准化响应。
- `logger/`: 日志系统初始化与获取方法，统一日志格式与输出目标。
- `runtime/`: 运行时资源容器与依赖注入入口（获取数据库、缓存、日志等）。
- `storage/`: 存储抽象与不同后端适配（本地/云对象存储等）。

> 以上模块均为横切关注点，禁止直接耦合业务逻辑；业务只通过公开的接口访问。

## 快速使用

### 1. 初始化（在程序入口）

在应用启动时初始化运行时与配置（示例方法名以约定说明，具体以代码实现为准）：

```python
# main.py（示意）
from core.runtime import init_runtime

if __name__ == "__main__":
    # 可指定配置文件路径，如 config/settings.yaml 或 config/settings.dev.yaml
    init_runtime(settings_path="config/settings.yaml")
```

### 2. 在 API 中获取资源（FastAPI 依赖注入）

```python
from fastapi import APIRouter, Depends

# 约定的资源获取入口（以 get_* 命名），具体函数在 runtime/logger/database 中提供
from core.runtime import get_db, get_cache
from core.logger import get_logger

router = APIRouter(prefix="/example", tags=["example"])

@router.get("/items")
async def list_items(
    db = Depends(get_db),
    cache = Depends(get_cache),
    logger = Depends(get_logger),
):
    logger.info("list items")
    # 使用 db / cache 执行业务逻辑
    return {"items": []}
```

### 3. 手动使用（非依赖注入场景）

```python
from core.logger import get_logger
from core.database import get_session  # 若提供会话工厂接口

logger = get_logger(__name__)

with get_session() as session:
    logger.info("do something with session")
    # session.execute(...)
```

## 配置与环境

- 默认配置文件位于 `config/settings.yaml`，开发环境可使用 `config/settings.dev.yaml`。
- 建议通过环境变量或启动参数选择配置文件，以便在不同部署环境间切换。
- 配置项通常包含：数据库、缓存、日志级别、存储后端等。

示例（YAML 摘要）：

```yaml
database:
  driver: sqlite  # 可选 mysql/postgresql/sqlite
  source: "sqlite:///./dy_yun.db"

logging:
  level: INFO

storage:
  backend: local # 可选 oss/s3 等
```

## 数据库（database/）

- 统一管理连接与会话生命周期，避免各模块重复初始化。
- 支持在依赖注入中提供会话对象（例如 `Depends(get_db)`）。
- 若使用异步 ORM，请统一采用 async/await 的调用规范。

## 日志（logger/）

- 提供全局可用的日志获取函数（例如 `get_logger(name)`）。
- 统一日志格式（时间、等级、请求 ID 等）与输出（控制台/文件）。
- 在中间件中注入请求范围的上下文（如请求 ID），提升可观测性。

## 错误（errors/）

- 定义标准错误码与异常类型，供 API 层统一响应。
- 建议通过异常到响应的转换器，将内部错误屏蔽为一致的外部格式。

## 运行时（runtime/）

- 承载应用启动后的全局资源：数据库、缓存、日志器、配置等。
- 通过 `get_*` 系列函数暴露资源获取入口，兼容依赖注入与手动调用。
- 保持无环依赖：运行时只持有资源，不引用业务模块。

## 存储（storage/）

- 面向“缓存与队列”的统一抽象，不用于文件/对象存储。
- 缓存适配：支持本地内存/Redis 等，提供过期策略、命名空间与序列化策略。
- 队列适配：支持内建轻量队列与第三方后端（如 Redis Stream、RabbitMQ、Kafka），统一生产/消费接口。
- 可靠性能力：支持重试、延迟队列、死信队列（DLQ）与背压（按实现而定）。
- 通过配置选择具体后端，实现在开发与生产环境间平滑切换；与 `runtime/` 集成，支持依赖注入方式获取客户端。

## 约定与最佳实践

- 模块边界清晰：业务逻辑不进入 `core/`，仅使用其接口。
- 类型提示完整：对外接口均提供类型标注以提升可读性与 IDE 体验。
- 异步优先：若选用异步栈，确保数据库/缓存/IO 均使用 async API。
- 统一错误：抛出或转换为 `errors/` 定义的异常类型与错误码。
- 配置集中：通过 `config/` 加载合并，避免散落的硬编码。

## 版本与变更

- 建议遵循 SemVer（语义化版本），对破坏性改动在 release 前明确标注。
- 重要改动记录在项目 `docs/` 或本目录的 `CHANGELOG.md`（如添加）。

## 测试与质量

- 单元测试：建议在 `tests/` 目录为核心能力编写用例（数据库、日志、错误处理等）。
- 代码检查：推荐使用 `black`、`isort` 等工具进行格式化与导入整理。

## 贡献指南

1. 讨论：在提交 PR 前先就接口与改动范围进行简要讨论。
2. 一致性：遵守现有模块边界与命名约定，避免引入耦合。
3. 附测试：为新增/修改的能力添加必要的测试与简要文档。

## 常见问题（FAQ）

- 如何在开发与生产间切换配置？
  - 通过启动参数或环境变量指定 `settings.yaml` 路径，并在 `config/` 中合并差异。
- 依赖注入是否强制？
  - 推荐在 API 层使用依赖注入以获得更好的生命周期管理；非 API 场景可手动获取资源。
- 能否直接在业务中初始化数据库或日志？
  - 不建议。统一通过 `core/` 提供的入口，避免重复初始化与配置漂移。
