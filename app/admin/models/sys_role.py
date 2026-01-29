"""
SysRole Model - 系统角色模型
"""
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import synonym, reconstructor
from common.models import BaseModel


class SysRole(BaseModel):
    """系统角色模型"""
    __tablename__ = "sys_role"
    __table_args__ = {'comment': '系统角色表'}
    
    # 主键：数据库列名是role_id，但我们使用id作为属性名
    id = Column('role_id', Integer, primary_key=True, autoincrement=True, comment="角色ID")
    
    # 提供role_id作为id的别名
    role_id = synonym('id')
    
    # 基本信息
    role_name = Column(String(128), comment="角色名称")
    status = Column(String(4), comment="状态 1禁用 2正常")
    role_key = Column(String(128), comment="角色代码")
    role_sort = Column(Integer, comment="角色排序")
    flag = Column(String(128), comment="标志")
    remark = Column(String(255), comment="备注")
    admin = Column(Boolean, default=False, comment="是否管理员")
    data_scope = Column(String(128), comment="数据范围")
    
    def __repr__(self):
        return f"<SysRole(role_id={self.role_id}, role_name={self.role_name})>"
