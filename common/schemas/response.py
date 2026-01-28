"""
API Response - API 响应模型
"""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """统一 API 响应"""
    code: int = Field(200, description="状态码")
    msg: str = Field("success", description="消息")
    data: Optional[T] = Field(None, description="数据")
    request_id: Optional[str] = Field(None, description="请求 ID")


class ErrorResponse(BaseModel):
    """错误响应"""
    code: int = Field(description="错误码")
    msg: str = Field(description="错误消息")
    detail: Optional[str] = Field(None, description="详细信息")
    request_id: Optional[str] = Field(None, description="请求 ID")
