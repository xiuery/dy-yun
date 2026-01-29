"""
Permission middleware - 权限中间件
"""
from typing import Optional
from fastapi import Depends, Request
from pydantic import BaseModel
from common.middleware.auth import jwt_required
from core.jwtauth import MapClaims, user


class DataPermission(BaseModel):
    """数据权限模型"""
    user_id: int
    role_id: Optional[int] = None
    dept_id: Optional[int] = None
    data_scope: int = 5  # 1=全部,2=自定义,3=本部门,4=本部门及以下,5=仅本人


def check_permission(permission: str):
    """检查权限（返回依赖函数）"""
    async def permission_checker(request: Request, claims: MapClaims = Depends(jwt_required)) -> DataPermission:
        # 获取用户信息
        user_id = user.get_user_id(request)
        role_id = user.get_role_id(request)
        dept_id = user.get_dept_id(request)
        
        # 管理员拥有所有权限
        if user_id == 1:
            return DataPermission(
                user_id=user_id,
                role_id=role_id,
                dept_id=dept_id,
                data_scope=1,
            )
        # TODO: 这里可以添加实际的权限验证逻辑
        return DataPermission(
            user_id=user_id,
            role_id=role_id,
            dept_id=dept_id,
            data_scope=5,
        )
    return permission_checker
