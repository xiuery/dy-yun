"""
Schemas package - 数据传输对象
"""
from common.schemas.pagination import PaginationRequest, PaginationResponse
from common.schemas.response import APIResponse, ErrorResponse

__all__ = [
    "PaginationRequest",
    "PaginationResponse",
    "APIResponse",
    "ErrorResponse",
]
