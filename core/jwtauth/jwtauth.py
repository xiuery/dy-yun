"""
JWT Authentication Core - JWT 认证核心

- 支持回调函数模式（Authenticator, PayloadFunc, Authorizator, Unauthorized）
- 提供 LoginHandler, RefreshHandler, LogoutHandler
- 提供 MiddlewareFunc 用于路由保护
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable, Union
from fastapi import Request, HTTPException, status, Response
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from pydantic import BaseModel

from .constants import JWT_PAYLOAD_KEY, IDENTITY_KEY


# ========== 类型定义 ==========

# MapClaims JWT Claims 类型别名
MapClaims = Dict[str, Any]


# ========== 异常定义 ==========

class JWTAuthError(Exception):
    """JWT 认证错误基类"""
    pass


class MissingSecretKeyError(JWTAuthError):
    """缺少密钥错误"""
    pass


class MissingAuthenticatorError(JWTAuthError):
    """缺少认证函数错误"""
    pass


class EmptyAuthHeaderError(JWTAuthError):
    """空的认证头错误"""
    pass


class InvalidSigningAlgorithmError(JWTAuthError):
    """无效的签名算法错误"""
    pass


# ========== JWTAuth 类 ==========

class JWTAuth:
    """
    JWT 认证类
    
    提供完整的 JWT 认证流程
    
    核心特性：
    1. 回调函数模式 - 高度可定制化
    2. 上下文传递 - 在请求链中传递用户信息
    3. 完整的生命周期 - Login, Refresh, Logout, Middleware
    """
    
    def __init__(
        self,
        # ========== 基础配置 ==========
        realm: str = "dy-yun",
        secret_key: str = None,
        algorithm: str = "HS256",
        timeout: int = 1440,  # 分钟
        max_refresh: int = 1440,  # 分钟
        identity_key: str = IDENTITY_KEY,
        
        # ========== Token 配置 ==========
        token_lookup: str = "header: Authorization, query: token, cookie: jwt",
        token_head_name: str = "Bearer",
        
        # ========== 回调函数（核心） ==========
        authenticator: Optional[Callable] = None,
        payload_func: Optional[Callable] = None,
        authorizator: Optional[Callable] = None,
        unauthorized_handler: Optional[Callable] = None,
        identity_handler: Optional[Callable] = None,
        login_response: Optional[Callable] = None,
        refresh_response: Optional[Callable] = None,
        logout_response: Optional[Callable] = None,
    ):
        """
        初始化 JWT 认证
        
        Args:
            realm: JWT 认证领域
            secret_key: 签名密钥（必需）
            algorithm: 加密算法
            timeout: Token 超时时间（分钟）
            max_refresh: Token 最大刷新时间（分钟）
            identity_key: 身份标识键
            token_lookup: Token 查找位置
            token_head_name: Token 前缀
            
            authenticator: 登录认证函数 async (request) -> user_data or None
            payload_func: Payload 生成函数 (user_data) -> dict
            authorizator: 权限校验函数 (claims, request) -> bool
            unauthorized_handler: 未授权处理函数 (request, code, message) -> Response
            identity_handler: 身份提取函数 (request) -> identity
            login_response: 登录成功响应函数 (request, token, expire) -> Response
            refresh_response: 刷新成功响应函数 (request, token, expire) -> Response
            logout_response: 登出成功响应函数 (request) -> Response
        """
        # 基础配置
        self.realm = realm
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.timeout = timedelta(minutes=timeout)
        self.max_refresh = timedelta(minutes=max_refresh)
        self.identity_key = identity_key
        
        # Token 配置
        self.token_lookup = token_lookup
        self.token_head_name = token_head_name
        
        # 回调函数
        self.authenticator = authenticator
        self.payload_func = payload_func
        self.authorizator = authorizator
        self.unauthorized_handler = unauthorized_handler
        self.identity_handler = identity_handler
        self.login_response = login_response
        self.refresh_response = refresh_response
        self.logout_response = logout_response
        
        # 验证必需参数
        if not self.secret_key:
            raise MissingSecretKeyError("secret_key is required")
        if not self.authenticator:
            raise MissingAuthenticatorError("authenticator func is required")

    # ========== 核心方法 ==========
    
    def token_generator(self, user_data: Dict[str, Any]) -> str:
        """
        生成 Token
        

        Args:
            user_data: 用户数据（由 authenticator 返回）
            
        Returns:
            JWT token 字符串
        """
        # 1. 生成 payload
        claims = self.payload_func(user_data)
        
        # 2. 添加过期时间
        now = datetime.utcnow()
        expire = now + self.timeout
        claims.update({
            "exp": int(expire.timestamp()),
            "orig_iat": int(now.timestamp()),  # 原始签发时间
        })
        
        # 3. 编码 JWT
        encoded_jwt = jwt.encode(claims, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def parse_token(self, request: Request) -> MapClaims:
        """
        从请求中解析 Token
        

        Args:
            request: FastAPI Request 对象
            
        Returns:
            JWT Claims 字典
            
        Raises:
            HTTPException: Token 无效或缺失
        """
        token = None
        
        # 从不同位置查找 Token
        parts = self.token_lookup.split(",")
        for part in parts:
            part = part.strip()
            
            if part.startswith("header:"):
                # 从 Header 获取
                header_name = part.split(":", 1)[1].strip()
                token = request.headers.get(header_name)
                if token:
                    # 去除 "Bearer " 前缀
                    if token.startswith(self.token_head_name):
                        token = token[len(self.token_head_name):].strip()
                    break
            
            elif part.startswith("query:"):
                # 从查询参数获取
                query_name = part.split(":", 1)[1].strip()
                token = request.query_params.get(query_name)
                if token:
                    break
            
            elif part.startswith("cookie:"):
                # 从 Cookie 获取
                cookie_name = part.split(":", 1)[1].strip()
                token = request.cookies.get(cookie_name)
                if token:
                    break
        
        if not token:
            raise EmptyAuthHeaderError("auth header is empty")
        
        # 解析 Token
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # ========== 处理器方法（Handler） ==========
    
    async def login_handler(self, request: Request) -> Response:
        """
        登录处理器
        
        处理 POST /login 请求
        """
        # 1. 调用 Authenticator 验证用户
        user_data = await self.authenticator(request)
        
        if not user_data:
            return await self.unauthorized_handler(
                request,
                status.HTTP_401_UNAUTHORIZED,
                "用户名或密码错误"
            )
        
        # 2. 生成 Token
        token = self.token_generator(user_data)
        expire = datetime.utcnow() + self.timeout
        
        # 3. 返回响应
        return await self.login_response(request, token, expire)
    
    async def refresh_handler(self, request: Request) -> Response:
        """
        Token 刷新处理器
        """
        # 1. 从旧 Token 提取 Claims
        claims = self.parse_token(request)
        
        # 2. 检查是否在刷新期内
        orig_iat = claims.get("orig_iat")
        if orig_iat:
            orig_time = datetime.fromtimestamp(orig_iat)
            if datetime.utcnow() - orig_time > self.max_refresh:
                return await self.unauthorized_handler(
                    request,
                    status.HTTP_401_UNAUTHORIZED,
                    "token 已超过最大刷新时间"
                )
        
        # 3. 生成新 Token（保留原有数据）
        token = self.token_generator(claims)
        expire = datetime.utcnow() + self.timeout
        
        # 4. 返回响应
        return await self.refresh_response(request, token, expire)
    
    async def logout_handler(self, request: Request) -> Response:
        """
        登出处理器
        """
        # JWT 是无状态的，登出只需要客户端删除 Token
        # 这里可以添加黑名单逻辑（可选）
        return await self.logout_response(request)
    
    # ========== 中间件方法 ==========
    
    async def middleware_func(self, request: Request) -> MapClaims:
        """
        中间件函数：验证 Token 并返回 Claims
        
        用于保护需要认证的路由
        
        Args:
            request: FastAPI Request 对象
            
        Returns:
            JWT Claims 字典
            
        Raises:
            HTTPException: 认证失败
        """
        try:
            # 1. 从请求中提取并解析 Token
            claims = self.parse_token(request)
            
            # 2. 检查是否过期
            exp = claims.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="token is expired",
                )
            
            # 3. 身份提取（可选）
            identity = None
            if self.identity_handler:
                identity = self.identity_handler(request)
            else:
                identity = claims.get(self.identity_key)
            
            # 4. 权限校验（可选）
            if self.authorizator:
                if not self.authorizator(claims, request):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="you don't have permission to access",
                    )
            
            # 5. 将 Claims 存入请求状态（类似 Gin 的 c.Set）
            # FastAPI 使用 request.state 存储请求级数据
            request.state.jwt_payload = claims
            request.state.identity = identity
            
            # 6. 提取常用字段到 request.state（方便后续使用）
            request.state.user_id = claims.get("user_id")
            request.state.username = claims.get("username")
            request.state.rolekey = claims.get("rolekey", "")
            request.state.role_id = claims.get("role_id")
            request.state.dept_id = claims.get("dept_id")
            
            return claims
            
        except EmptyAuthHeaderError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
