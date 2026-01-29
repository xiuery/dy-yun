"""
Auth Schemas - 认证相关数据模型
"""
from pydantic import BaseModel, Field, field_validator


class Login(BaseModel):
    """
    登录请求数据结构
    """
    username: str = Field(..., description="用户名", min_length=1, max_length=64)
    password: str = Field(..., description="密码", min_length=1, max_length=128)
    code: str = Field(..., description="验证码", min_length=4, max_length=6)
    uuid: str = Field(..., description="验证码UUID", min_length=1)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """验证用户名"""
        v = v.strip()
        if not v:
            raise ValueError('用户名不能为空')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码"""
        if not v:
            raise ValueError('密码不能为空')
        return v
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        """验证验证码"""
        v = v.strip()
        if not v:
            raise ValueError('验证码不能为空')
        return v
