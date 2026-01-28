"""
SysUser Model - 系统用户模型
"""
from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.orm import synonym
from common.models import BaseModel


class SysUser(BaseModel):
    """系统用户模型"""
    __tablename__ = "sys_user"
    __table_args__ = {'comment': '系统用户表'}
    
    # 使用synonym将user_id映射到BaseModel的id字段
    user_id = synonym('id')
    
    # 基本信息
    username = Column(String(64), comment="用户名")
    password = Column(String(128), comment="密码")
    nick_name = Column(String(128), comment="昵称")
    phone = Column(String(11), comment="手机号")
    email = Column(String(128), comment="邮箱")
    
    # 关联信息
    role_id = Column(BigInteger, comment="角色ID")
    dept_id = Column(BigInteger, comment="部门")
    post_id = Column(BigInteger, comment="岗位")
    
    # 安全信息
    salt = Column(String(255), comment="加盐")
    avatar = Column(String(255), comment="头像")
    sex = Column(String(255), comment="性别")
    
    # 其他信息
    remark = Column(String(255), comment="备注")
    status = Column(String(4), comment="状态")
    
    # 审计字段继承自BaseModel:
    # - create_by (Integer, 创建者)
    # - update_by (Integer, 更新者) 
    # - created_at (DateTime, 创建时间)
    # - updated_at (DateTime, 最后更新时间)
    # - deleted_at (DateTime, 删除时间)
    
    def __repr__(self):
        return f"<SysUser(user_id={self.user_id}, username={self.username})>"
