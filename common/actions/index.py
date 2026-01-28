"""
Generic CRUD actions - 通用 CRUD 操作
"""
from typing import Type, TypeVar, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from common.models import BaseModel
from common.schemas.pagination import PaginationRequest, PaginationResponse

T = TypeVar("T", bound=BaseModel)


async def get_page(
    db: AsyncSession,
    model: Type[T],
    pagination: PaginationRequest,
) -> PaginationResponse[T]:
    """通用分页查询"""
    offset = (pagination.page - 1) * pagination.page_size
    count_query = select(func.count()).select_from(model)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    query = select(model).offset(offset).limit(pagination.page_size)
    result = await db.execute(query)
    items = result.scalars().all()
    return PaginationResponse(
        page=pagination.page,
        page_size=pagination.page_size,
        total=total,
        list=list(items),
    )


async def create(db: AsyncSession, obj: T) -> T:
    """通用创建"""
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update(db: AsyncSession, obj: T) -> T:
    """通用更新"""
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete(db: AsyncSession, obj: T) -> bool:
    """通用删除"""
    await db.delete(obj)
    await db.commit()
    return True
