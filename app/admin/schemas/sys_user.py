"""
SysUser Schemas - 用户数据传输对象
"""
from typing import Optional
from pydantic import BaseModel, Field


class SysUserQuery(BaseModel):
    """系统用户查询条件"""
    username: Optional[str] = Field(None, description="用户名")
    phone: Optional[str] = Field(None, description="手机号")
    status: Optional[int] = Field(None, description="状态")


class SysUserCreate(BaseModel):
    """创建系统用户"""
    username: str = Field(..., min_length=3, max_length=64, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    nick_name: Optional[str] = Field(None, max_length=128, description="昵称")
    phone: Optional[str] = Field(None, max_length=11, description="手机号")
    email: Optional[str] = Field(None, max_length=128, description="邮箱")
    sex: Optional[int] = Field(0, description="性别 0=未知 1=男 2=女")
    dept_id: Optional[int] = Field(None, description="部门 ID")
    role_id: Optional[int] = Field(None, description="角色 ID")
    status: Optional[int] = Field(1, description="状态 1=正常 2=停用")


class SysUserUpdate(BaseModel):
    """更新系统用户"""
    nick_name: Optional[str] = Field(None, max_length=128, description="昵称")
    phone: Optional[str] = Field(None, max_length=11, description="手机号")
    email: Optional[str] = Field(None, max_length=128, description="邮箱")
    sex: Optional[int] = Field(None, description="性别")
    dept_id: Optional[int] = Field(None, description="部门 ID")
    role_id: Optional[int] = Field(None, description="角色 ID")
    status: Optional[int] = Field(None, description="状态")


class SysUserResponse(BaseModel):
    """系统用户响应"""
    id: int
    username: str
    nick_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    sex: int = 0
    dept_id: Optional[int] = None
    role_id: Optional[int] = None
    status: int = 1
    
    class Config:
        from_attributes = True
