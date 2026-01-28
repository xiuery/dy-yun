"""
Logger middleware - 日志中间件
"""
import time
from fastapi import Request
from core.logger import get_request_logger


async def logger_middleware(request: Request, call_next):
    """日志中间件"""
    request_id = getattr(request.state, "request_id", "")
    logger = get_request_logger(request_id)
    start_time = time.time()
    logger.info(f"→ {request.method} {request.url.path}")
    response = await call_next(request)
    elapsed = time.time() - start_time
    logger.info(f"← {request.method} {request.url.path} {response.status_code} {elapsed:.3f}s")
    return response
