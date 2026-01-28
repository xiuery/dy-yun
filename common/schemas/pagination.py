"""
Pagination DTO - 分页数据传输对象
"""
from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationRequest(BaseModel):
    """分页请求"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")


class PaginationResponse(BaseModel, Generic[T]):
    """分页响应"""
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
    total: int = Field(description="总记录数")
    list: List[T] = Field(default_factory=list, description="数据列表")
