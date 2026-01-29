"""
Header middleware - HTTP头中间件
包括缓存控制、CORS选项、安全头等
"""
from datetime import datetime
from fastapi import Request
from starlette.responses import JSONResponse


async def no_cache_middleware(request: Request, call_next):
    """
    NoCache 中间件 - 防止客户端缓存HTTP响应
    添加缓存控制头，确保每次都从服务器获取最新数据
    """
    response = await call_next(request)
    
    # 添加禁用缓存的响应头
    response.headers["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
    response.headers["Expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"
    response.headers["Last-Modified"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    return response


async def options_middleware(request: Request, call_next):
    """
    Options 中间件 - 处理CORS预检请求
    为OPTIONS请求添加CORS头并直接返回200
    """
    if request.method != "OPTIONS":
        return await call_next(request)
    
    # OPTIONS请求直接返回CORS头
    return JSONResponse(
        status_code=200,
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "authorization, origin, content-type, accept",
            "Allow": "HEAD,GET,POST,PUT,PATCH,DELETE,OPTIONS",
            "Content-Type": "application/json",
        }
    )


async def secure_middleware(request: Request, call_next):
    """
    Secure 中间件 - 添加安全和资源访问头
    包括XSS保护、内容类型嗅探保护、HSTS等
    """
    response = await call_next(request)
    
    # CORS - 允许所有来源（生产环境应配置具体域名）
    response.headers["Access-Control-Allow-Origin"] = "*"
    
    # 防止MIME类型嗅探
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # XSS保护
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # 如果是HTTPS连接，添加HSTS头
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
    
    # 可选：内容安全策略（根据需要启用）
    # response.headers["Content-Security-Policy"] = "script-src 'self' https://cdnjs.cloudflare.com"
    
    # 可选：防止点击劫持（如需启用，取消注释）
    # response.headers["X-Frame-Options"] = "DENY"
    
    return response
