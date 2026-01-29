"""
Middleware loader - 中间件加载器
集中管理所有中间件注册
"""
from fastapi import FastAPI
from common.middleware.request_id import request_id_middleware
from common.middleware.logger import logger_middleware
from common.middleware.error_handler import error_handler_middleware
from common.middleware.rate_limit import rate_limit_middleware
from common.middleware.header import no_cache_middleware, options_middleware, secure_middleware


def register_middlewares(app: FastAPI) -> None:
    """
    注册所有中间件
    
    按执行顺序倒序注册：
    执行顺序: request → error_handler → secure → options → no_cache → request_id → logger → rate_limit → 路由
    """
    # 初始化 JWT 认证中间件
    from common.middleware.auth import init_auth_middleware
    init_auth_middleware()
    
    # 最外层：捕获所有异常
    app.middleware("http")(error_handler_middleware)
    
    # 安全头
    app.middleware("http")(secure_middleware)
    
    # CORS预检请求
    app.middleware("http")(options_middleware)
    
    # 禁用缓存
    app.middleware("http")(no_cache_middleware)
    
    # 生成请求ID
    app.middleware("http")(request_id_middleware)
    
    # 记录日志（使用request_id）
    app.middleware("http")(logger_middleware)
    
    # 最内层：限流检查
    app.middleware("http")(rate_limit_middleware)
