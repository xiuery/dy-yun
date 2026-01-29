"""
Login - 登录数据结构
"""
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.models.sys_user import SysUser
from app.admin.models.sys_role import SysRole
from app.admin.schemas.auth import Login
from core.utils import verify_password


async def get_user(
    db: AsyncSession,
    login_data: Login
) -> Tuple[Optional[SysUser], Optional[SysRole]]:
    """
    获取用户和角色信息
    
    Args:
        db: 数据库会话
        login_data: 登录数据
        
    Returns:
        (user, role) 元组
        
    Raises:
        Exception: 用户不存在、密码错误或角色不存在时抛出异常
    """
    # 查询用户 (status='2' 表示正常状态)
    stmt = select(SysUser).where(
        SysUser.username == login_data.username,
        SysUser.status == '2'
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise Exception(f"user not found or disabled")
    
    # 验证密码
    if not verify_password(login_data.password, user.password):
        raise Exception(f"invalid password")
    
    # 查询角色
    stmt = select(SysRole).where(SysRole.id == user.role_id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    
    if not role:
        raise Exception(f"role not found")
    
    return user, role
