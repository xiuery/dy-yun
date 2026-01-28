"""
Main entry - 主入口
dy-yun 企业级中后台应用框架 v0.1
"""
import os
import argparse
from fastapi import FastAPI
from contextlib import asynccontextmanager
from core import (
    get_settings,
    set_config_path,
    setup_logger,
    setup_database,
    runtime,
    close_database,
)
from common.storage import setup_storage, close_storage
from common.middleware import init_rate_limiter, register_middlewares
from common.routers import register_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    settings = get_settings()
    
    # 1. 配置日志
    setup_logger(settings.log)
    
    # 2. 初始化数据库
    await setup_database(settings.database)
    
    # 3. 初始化存储组件（缓存、队列等）
    await setup_storage(settings)
    
    # 4. 初始化限流器
    if settings.rate_limit.enabled:
        init_rate_limiter(
            requests=settings.rate_limit.requests,
            window=settings.rate_limit.window,
            use_redis=settings.rate_limit.use_redis
        )
    
    # 保存配置到 Runtime
    runtime.set_config(settings.model_dump())
    
    yield
    
    # 关闭时清理资源
    await close_storage()
    await close_database()


def create_app() -> FastAPI:
    """
    创建 FastAPI 应用
    """
    settings = get_settings()
    
    app = FastAPI(
        title=settings.application.name,
        version=settings.application.version,
        description="企业级中后台应用框架",
        lifespan=lifespan,
    )
    
    # 1. 注册全局中间件
    register_middlewares(app)
    
    # 2. 注册业务路由
    register_routers(app)
    
    # 3. 健康检查
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": settings.application.version}
    
    return app


if __name__ == "__main__":
    import uvicorn
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="dy-yun 企业级中后台应用框架")
    parser.add_argument(
        "-c", "--config",
        type=str,
        default="config/settings.yaml",
        help="配置文件路径 (默认: config/settings.yaml)"
    )
    parser.add_argument(
        "--host",
        type=str,
        help="服务监听地址 (覆盖配置文件)"
    )
    parser.add_argument(
        "--port",
        type=int,
        help="服务监听端口 (覆盖配置文件)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="启用热重载模式"
    )
    
    args = parser.parse_args()
    
    # 设置配置文件路径（通过环境变量传递，以便 reload 模式下也能生效）
    os.environ["DY_YUN_CONFIG_FILE"] = args.config
    set_config_path(args.config)
    
    settings = get_settings()
    
    # 命令行参数优先级高于配置文件
    host = args.host if args.host else settings.application.host
    port = args.port if args.port else settings.application.port
    reload = args.reload if args.reload else (settings.application.mode == "dev")
    
    print(f"🚀 Starting dy-yun v{settings.application.version}")
    print(f"📝 Config file: {args.config}")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    
    uvicorn.run(
        "main:create_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
    )
