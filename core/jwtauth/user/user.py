"""
JWT User Helpers - JWT 用户辅助函数

提供从请求中提取用户信息的辅助函数
"""
from typing import Optional, Dict, Any
from fastapi import Request

# 类型别名
MapClaims = Dict[str, Any]


def extract_claims(request: Request) -> MapClaims:
    """
    从请求中提取 JWT Claims
    
    Args:
        request: FastAPI Request 对象
        
    Returns:
        JWT Claims 字典
    """
    return getattr(request.state, "jwt_payload", {})


def get_user_id(request: Request) -> Optional[int]:
    """从请求中获取用户 ID"""
    return getattr(request.state, "user_id", None)


def get_username(request: Request) -> Optional[str]:
    """从请求中获取用户名"""
    return getattr(request.state, "username", None)


def get_rolekey(request: Request) -> Optional[str]:
    """从请求中获取角色标识"""
    return getattr(request.state, "rolekey", None)


def get_role_id(request: Request) -> Optional[int]:
    """从请求中获取角色 ID"""
    return getattr(request.state, "role_id", None)


def get_dept_id(request: Request) -> Optional[int]:
    """从请求中获取部门 ID"""
    return getattr(request.state, "dept_id", None)
