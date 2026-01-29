"""
SysUser API - 用户管理 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.runtime import get_db
from common.schemas.pagination import PaginationRequest, PaginationResponse
from common.schemas.response import APIResponse
from common.middleware.auth import jwt_required
from core.jwtauth import MapClaims
from common.middleware.permission import check_permission, DataPermission
from app.admin.services.sys_user import SysUserService
from app.admin.schemas.sys_user import SysUserCreate, SysUserUpdate, SysUserQuery, SysUserResponse

router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])


@router.get("/page", response_model=APIResponse[PaginationResponse[SysUserResponse]])
async def get_user_page(
    page: int = 1,
    page_size: int = 10,
    username: str = None,
    phone: str = None,
    status: int = None,
    db: AsyncSession = Depends(get_db),
    claims: MapClaims = Depends(jwt_required),
    permission: DataPermission = Depends(check_permission("sys:user:list")),
):
    """分页查询用户"""
    pagination = PaginationRequest(page=page, page_size=page_size)
    query = SysUserQuery(username=username, phone=phone, status=status)
    service = SysUserService(db)
    result = await service.get_page(pagination, query)
    return APIResponse(data=result)


@router.get("/{user_id}", response_model=APIResponse[SysUserResponse])
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    claims: MapClaims = Depends(jwt_required),
):
    """获取用户详情"""
    service = SysUserService(db)
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return APIResponse(data=SysUserResponse.model_validate(user))


@router.post("", response_model=APIResponse[SysUserResponse])
async def create_user(
    user_create: SysUserCreate,
    db: AsyncSession = Depends(get_db),
    claims: MapClaims = Depends(jwt_required),
    permission: DataPermission = Depends(check_permission("sys:user:add")),
):
    """创建用户"""
    service = SysUserService(db)
    try:
        user = await service.create(user_create)
        return APIResponse(data=SysUserResponse.model_validate(user))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{user_id}", response_model=APIResponse[SysUserResponse])
async def update_user(
    user_id: int,
    user_update: SysUserUpdate,
    db: AsyncSession = Depends(get_db),
    claims: MapClaims = Depends(jwt_required),
    permission: DataPermission = Depends(check_permission("sys:user:edit")),
):
    """更新用户"""
    service = SysUserService(db)
    user = await service.update(user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return APIResponse(data=SysUserResponse.model_validate(user))


@router.delete("/{user_id}", response_model=APIResponse[bool])
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    claims: MapClaims = Depends(jwt_required),
    permission: DataPermission = Depends(check_permission("sys:user:remove")),
):
    """删除用户"""
    service = SysUserService(db)
    success = await service.delete(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    return APIResponse(data=success)
