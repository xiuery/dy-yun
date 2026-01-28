"""
Errors package - 错误和异常包
"""
from core.errors.exceptions import (
    APIException,
    AuthenticationError,
    PermissionDenied,
    NotFound,
    ValidationError,
    DatabaseError,
)

__all__ = [
    "APIException",
    "AuthenticationError",
    "PermissionDenied",
    "NotFound",
    "ValidationError",
    "DatabaseError",
]
