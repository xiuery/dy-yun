"""
Permission middleware - 权限中间件
"""
from typing import Optional
from fastapi import Depends, HTTPException
from pydantic import BaseModel
from common.middleware.auth import get_current_user, TokenData


class DataPermission(BaseModel):
    """数据权限模型"""
    user_id: int
    role_id: Optional[int] = None
    dept_id: Optional[int] = None
    data_scope: int = 5  # 1=全部,2=自定义,3=本部门,4=本部门及以下,5=仅本人


def check_permission(permission: str):
    """检查权限（返回依赖函数）"""
    def permission_checker(current_user: TokenData = Depends(get_current_user)) -> DataPermission:
        # 管理员拥有所有权限
        if current_user.user_id == 1:
            return DataPermission(
                user_id=current_user.user_id,
                role_id=current_user.role_id,
                dept_id=current_user.dept_id,
                data_scope=1,
            )
        # TODO: 这里可以添加实际的权限验证逻辑
        return DataPermission(
            user_id=current_user.user_id,
            role_id=current_user.role_id,
            dept_id=current_user.dept_id,
            data_scope=5,
        )
    return permission_checker
