"""
Custom exceptions - 自定义异常
"""
from typing import Any, Optional


class APIException(Exception):
    """API 异常基类"""
    def __init__(self, status_code: int = 500, message: str = "Internal Server Error", detail: Optional[Any] = None):
        self.status_code = status_code
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class AuthenticationError(APIException):
    """认证错误"""
    def __init__(self, message: str = "Authentication failed", detail: Optional[Any] = None):
        super().__init__(status_code=401, message=message, detail=detail)


class PermissionDenied(APIException):
    """权限拒绝"""
    def __init__(self, message: str = "Permission denied", detail: Optional[Any] = None):
        super().__init__(status_code=403, message=message, detail=detail)


class NotFound(APIException):
    """资源未找到"""
    def __init__(self, message: str = "Resource not found", detail: Optional[Any] = None):
        super().__init__(status_code=404, message=message, detail=detail)


class ValidationError(APIException):
    """验证错误"""
    def __init__(self, message: str = "Validation failed", detail: Optional[Any] = None):
        super().__init__(status_code=422, message=message, detail=detail)


class DatabaseError(APIException):
    """数据库错误"""
    def __init__(self, message: str = "Database error", detail: Optional[Any] = None):
        super().__init__(status_code=500, message=message, detail=detail)
