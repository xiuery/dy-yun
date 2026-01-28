"""
Middleware package - 中间件
"""
from common.middleware.request_id import request_id_middleware
from common.middleware.logger import logger_middleware
from common.middleware.error_handler import error_handler_middleware
from common.middleware.auth import create_access_token, get_current_user, TokenData
from common.middleware.permission import DataPermission, check_permission
from common.middleware.rate_limit import (
    rate_limit_middleware,
    init_rate_limiter,
    get_rate_limiter,
)
from common.middleware.header import (
    no_cache_middleware,
    options_middleware,
    secure_middleware,
)
from common.middleware.loader import register_middlewares

__all__ = [
    "request_id_middleware",
    "logger_middleware",
    "error_handler_middleware",
    "create_access_token",
    "get_current_user",
    "TokenData",
    "DataPermission",
    "check_permission",
    "rate_limit_middleware",
    "init_rate_limiter",
    "get_rate_limiter",
    "no_cache_middleware",
    "options_middleware",
    "secure_middleware",
    "register_middlewares",
]
