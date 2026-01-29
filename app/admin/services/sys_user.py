"""
SysUser service - 用户服务
"""
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import defer
from passlib.context import CryptContext
from common.services import BaseService
from common.schemas.pagination import PaginationRequest, PaginationResponse
from app.admin.models.sys_user import SysUser
from app.admin.schemas.sys_user import SysUserCreate, SysUserUpdate, SysUserQuery, SysUserResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SysUserService(BaseService):
    """系统用户服务"""
    
    async def get_page(
        self,
        pagination: PaginationRequest,
        query: Optional[SysUserQuery] = None,
    ) -> PaginationResponse[SysUserResponse]:
        """分页查询用户"""
        offset = (pagination.page - 1) * pagination.page_size
        stmt = select(SysUser).options(defer(SysUser.password))
        if query:
            if query.username:
                stmt = stmt.where(SysUser.username.like(f"%{query.username}%"))
            if query.phone:
                stmt = stmt.where(SysUser.phone == query.phone)
            if query.status is not None:
                stmt = stmt.where(SysUser.status == query.status)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0
        stmt = stmt.offset(offset).limit(pagination.page_size)
        result = await self.db.execute(stmt)
        users = result.scalars().all()
        return PaginationResponse(
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
            list=[SysUserResponse.model_validate(u) for u in users],
        )
    
    async def get_by_id(self, user_id: int) -> Optional[SysUser]:
        """根据 ID 获取用户"""
        result = await self.db.execute(
            select(SysUser).options(defer(SysUser.password)).where(SysUser.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[SysUser]:
        """根据用户名获取用户"""
        result = await self.db.execute(select(SysUser).where(SysUser.username == username))
        return result.scalar_one_or_none()
    
    async def create(self, user_create: SysUserCreate) -> SysUser:
        """创建用户"""
        existing = await self.get_by_username(user_create.username)
        if existing:
            self.add_error("用户名已存在")
            raise ValueError("用户名已存在")
        hashed_password = pwd_context.hash(user_create.password)
        user = SysUser(
            username=user_create.username,
            password=hashed_password,
            nick_name=user_create.nick_name,
            phone=user_create.phone,
            email=user_create.email,
            sex=user_create.sex,
            dept_id=user_create.dept_id,
            role_id=user_create.role_id,
            status=user_create.status,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update(self, user_id: int, user_update: SysUserUpdate) -> Optional[SysUser]:
        """更新用户"""
        user = await self.get_by_id(user_id)
        if not user:
            self.add_error("用户不存在")
            return None
        for key, value in user_update.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def delete(self, user_id: int) -> bool:
        """删除用户"""
        user = await self.get_by_id(user_id)
        if not user:
            self.add_error("用户不存在")
            return False
        await self.db.delete(user)
        await self.db.commit()
        return True
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
