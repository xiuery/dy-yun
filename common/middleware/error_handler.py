"""
Error handler middleware - 错误处理中间件
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from core.errors import APIException
from core.logger import get_request_logger


async def error_handler_middleware(request: Request, call_next):
    """错误处理中间件"""
    try:
        response = await call_next(request)
        
        # 捕获404等HTTP错误
        if response.status_code == 404:
            request_id = getattr(request.state, "request_id", "")
            logger = get_request_logger(request_id)
            logger.warning(f"404 Not Found: {request.method} {request.url.path}")
            return JSONResponse(
                status_code=404,
                content={
                    "code": 404,
                    "msg": f"路由 {request.method} {request.url.path} 不存在",
                    "data": None,
                    "requestId": request_id,
                },
            )
        
        return response
    except StarletteHTTPException as e:
        request_id = getattr(request.state, "request_id", "")
        logger = get_request_logger(request_id)
        logger.warning(f"HTTP {e.status_code}: {e.detail}")
        return JSONResponse(
            status_code=e.status_code,
            content={
                "code": e.status_code,
                "msg": e.detail if isinstance(e.detail, str) else str(e.detail),
                "data": None,
                "requestId": request_id,
            },
        )
    except APIException as e:
        request_id = getattr(request.state, "request_id", "")
        logger = get_request_logger(request_id)
        logger.error(f"API Error: {e.message}, detail: {e.detail}")
        return JSONResponse(
            status_code=e.status_code,
            content={
                "code": e.status_code,
                "msg": e.message,
                "data": e.detail,
                "requestId": request_id,
            },
        )
    except Exception as e:
        request_id = getattr(request.state, "request_id", "")
        logger = get_request_logger(request_id)
        logger.exception(f"Unhandled exception: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "msg": "Internal Server Error",
                "data": str(e),
                "requestId": request_id,
            },
        )
