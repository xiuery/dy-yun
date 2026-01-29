"""
Request ID middleware - 请求 ID 中间件
"""
import uuid
from fastapi import Request


async def request_id_middleware(request: Request, call_next):
    """请求 ID 中间件函数版本"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response
