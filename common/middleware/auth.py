"""
提供 JWT 认证中间件初始化和认证依赖
"""
from typing import Optional, Callable
from fastapi import Request
from core.config import get_settings
from core.jwtauth import JWTAuth, MapClaims


# 全局 JWT 认证实例
_jwt_auth: Optional[JWTAuth] = None


def AuthInit(
    authenticator: Callable,
    payload_func: Optional[Callable] = None,
    authorizator: Optional[Callable] = None,
    unauthorized_handler: Optional[Callable] = None,
    identity_handler: Optional[Callable] = None,
    login_response: Optional[Callable] = None,
    refresh_response: Optional[Callable] = None,
    logout_response: Optional[Callable] = None,
) -> JWTAuth:
    """
    初始化 JWT 认证中间件
    
    返回配置好的 JWT 中间件实例
    
    Args:
        authenticator: 登录认证函数 async (request) -> user_data or None
            验证用户凭证（用户名/密码），返回用户数据或 None
            
        payload_func: Payload 生成函数 (user_data) -> dict (可选)
            将用户数据转换为 JWT Claims
            
        authorizator: 权限校验函数 (claims, request) -> bool (可选)
            验证用户是否有权限访问当前资源
            
        unauthorized_handler: 未授权处理函数 (request, code, message) -> Response (可选)
            处理认证失败的响应
            
        identity_handler: 身份提取函数 (request) -> identity (可选)
            从 Claims 中提取用户身份信息
            
        login_response: 登录成功响应函数 (request, token, expire) -> Response (可选)
            自定义登录成功的响应格式
            
        refresh_response: 刷新成功响应函数 (request, token, expire) -> Response (可选)
            自定义 Token 刷新成功的响应格式
            
        logout_response: 登出成功响应函数 (request) -> Response (可选)
            自定义登出成功的响应格式
            
    Returns:
        JWTAuth 实例
    """
    global _jwt_auth
    
    settings = get_settings()
    
    # 创建 JWT 认证实例
    _jwt_auth = JWTAuth(
        realm="dy-yun",
        secret_key=settings.jwt.secret_key,
        algorithm=getattr(settings.jwt, 'algorithm', 'HS256'),
        timeout=getattr(settings.jwt, 'timeout', getattr(settings.jwt, 'access_token_expire_minutes', 1440)),
        max_refresh=getattr(settings.jwt, 'timeout', getattr(settings.jwt, 'access_token_expire_minutes', 1440)),
        token_lookup="header: Authorization, query: token, cookie: jwt",
        token_head_name="Bearer",
        authenticator=authenticator,
        payload_func=payload_func,
        authorizator=authorizator,
        unauthorized_handler=unauthorized_handler,
        identity_handler=identity_handler,
        login_response=login_response,
        refresh_response=refresh_response,
        logout_response=logout_response,
    )
    
    return _jwt_auth


def init_auth_middleware() -> JWTAuth:
    """
    初始化 JWT 认证中间件（带默认处理器）
    
    自动导入并配置所有认证处理器函数
    
    Returns:
        JWTAuth 实例
    """
    global _jwt_auth
    
    if _jwt_auth is None:
        from common.middleware.handler import (
            authenticator,
            payload_func,
            authorizator,
            unauthorized_handler,
            login_response,
            refresh_response,
            logout_response,
        )
        
        _jwt_auth = AuthInit(
            authenticator=authenticator,
            payload_func=payload_func,
            authorizator=authorizator,
            unauthorized_handler=unauthorized_handler,
            login_response=login_response,
            refresh_response=refresh_response,
            logout_response=logout_response,
        )
    
    return _jwt_auth


def get_jwt_auth() -> JWTAuth:
    """
    获取 JWT 认证实例
    
    Returns:
        JWTAuth 实例
        
    Raises:
        RuntimeError: 如果未初始化
    """
    if _jwt_auth is None:
        raise RuntimeError("JWT auth not initialized. Call init_auth_middleware() first.")
    return _jwt_auth


async def jwt_required(request: Request) -> MapClaims:
    """
    JWT 认证依赖
    
    用于路由中需要认证的端点
    """
    auth = get_jwt_auth()
    return await auth.middleware_func(request)

