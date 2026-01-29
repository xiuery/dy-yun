"""
Auth Handlers - 认证处理器

提供 JWT 认证相关的回调函数
"""
from typing import Optional
from fastapi import Request
from fastapi.responses import JSONResponse

from core.logger import get_request_logger
from core.runtime import get_db
from app.admin.schemas.auth import Login
from common.middleware.handler.login import get_user


async def authenticator(request: Request) -> Optional[dict]:
    """
    登录认证函数
    
    验证用户凭证，返回用户和角色信息用于生成 JWT Token
    
    Args:
        request: FastAPI Request 对象
        
    Returns:
        {"user": SysUser, "role": SysRole} 或 None（认证失败）
    """
    try:
        # 解析请求体
        data = await request.json()
        
        # 构造登录数据
        login_data = Login(**data)
        
        # TODO: 验证码校验（开发模式可跳过）
        # if not verify_captcha(login_data.uuid, login_data.code):
        #     return None
        
        # 使用get_db()获取数据库会话
        async for db in get_db():
            # 获取用户和角色
            sys_user, sys_role = await get_user(db, login_data)
            
            # 返回用户和角色数据
            return {
                "user": sys_user,
                "role": sys_role,
            }
        
    except Exception as e:
        logger = get_request_logger()
        logger.error(f"Authentication error: {e}", exc_info=True)
        return None


def payload_func(data: dict) -> dict:
    """
    生成 JWT Payload（参考 go-admin PayloadFunc）
    
    从 authenticator 返回的 {"user": SysUser, "role": SysRole} 提取 Claims
    
    Args:
        data: authenticator 返回的数据 {"user": user_obj, "role": sys_role}
        
    Returns:
        JWT Claims 字典，字段名对应 go-admin:
        - identity: 用户ID
        - roleid: 角色ID  
        - rolekey: 角色标识（用于权限校验）
        - nice: 用户名
        - datascope: 数据权限范围
        - rolename: 角色名称
    """
    sys_user = data.get("user")
    sys_role = data.get("role")
    
    return {
        "identity": sys_user.id,
        "roleid": sys_role.role_id,
        "rolekey": sys_role.role_key,
        "nice": sys_user.username,
        "datascope": getattr(sys_role, "data_scope", ""),
        "rolename": sys_role.role_name,
    }


async def authorizator(data: dict, request: Request) -> bool:
    """
    权限验证函数（参考 go-admin Authorizator）
    
    将用户信息设置到请求上下文，供后续中间件使用
    
    Args:
        data: authenticator 返回的数据 {"user": user_obj, "role": sys_role}
        request: FastAPI Request 对象
        
    Returns:
        True: 通过验证，False: 拒绝访问
    """
    try:
        sys_user = data.get("user")
        sys_role = data.get("role")
        
        # 将用户和角色信息存储到请求状态（类似 go-admin 的 c.Set）
        request.state.role = sys_role.role_name
        request.state.role_ids = sys_role.role_id
        request.state.user_id = sys_user.id
        request.state.username = sys_user.username
        request.state.data_scope = getattr(sys_role, "data_scope", "")
        
        return True
    except Exception as e:
        logger = get_request_logger()
        logger.error(f"Authorizator error: {e}", exc_info=True)
        return False


async def unauthorized_handler(request: Request, code: int, message: str) -> JSONResponse:
    """
    未授权处理函数（可选）
    
    自定义认证失败的响应格式
    
    Args:
        request: FastAPI Request 对象
        code: 错误码
        message: 错误信息
        
    Returns:
        JSON 响应
    """
    return JSONResponse(
        status_code=200,
        content={
            "code": code,
            "msg": message,
            "data": None,
        }
    )


async def login_response(request: Request, token: str, expire: int) -> JSONResponse:
    """
    登录成功响应函数（可选）
    
    自定义登录成功的响应格式
    
    Args:
        request: FastAPI Request 对象
        token: JWT Token
        expire: 过期时间（datetime对象）
        
    Returns:
        JSON 响应
    """
    # 登录阶段返回简化的响应，用户信息已在token中
    return JSONResponse(
        status_code=200,
        content={
            "code": 200,
            "token": token,
            "expire": int(expire.timestamp()) if hasattr(expire, 'timestamp') else expire,
        }
    )


async def refresh_response(request: Request, token: str, expire: int) -> JSONResponse:
    """
    刷新成功响应函数（可选）
    
    自定义 Token 刷新成功的响应格式
    
    Args:
        request: FastAPI Request 对象
        token: 新的 JWT Token
        expire: 过期时间（datetime对象或时间戳）
        
    Returns:
        JSON 响应
    """
    return JSONResponse(
        status_code=200,
        content={
            "code": 200,
            "token": token,
            "expire": int(expire.timestamp()) if hasattr(expire, 'timestamp') else expire,
        }
    )


async def logout_response(request: Request) -> JSONResponse:
    """
    登出成功响应函数（可选）
    
    自定义登出成功的响应格式
    
    Args:
        request: FastAPI Request 对象
        
    Returns:
        JSON 响应
    """
    return JSONResponse(
        status_code=200,
        content={
            "code": 200,
            "msg": "登出成功",
            "data": None,
        }
    )
