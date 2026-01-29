"""
SysUser Model - 系统用户模型
"""
from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.orm import synonym, reconstructor
from common.models import BaseModel


class SysUser(BaseModel):
    """系统用户模型"""
    __tablename__ = "sys_user"
    __table_args__ = {'comment': '系统用户表'}
    
    # 主键：数据库列名是user_id，但我们使用id作为属性名
    id = Column('user_id', Integer, primary_key=True, autoincrement=True, comment="用户ID")
    
    # 提供user_id作为id的别名
    user_id = synonym('id')
    
    # 基本信息
    username = Column(String(64), comment="用户名")
    password = Column(String(128), comment="密码", info={"exclude": True})
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
    
    @reconstructor
    def after_load(self):
        """
        数据加载后的钩子函数
        类似 GORM 的 AfterFind，在从数据库加载记录后自动执行
        将单个ID转换为列表格式，便于前端处理
        """
        self.dept_ids = [self.dept_id] if self.dept_id else []
        self.post_ids = [self.post_id] if self.post_id else []
        self.role_ids = [self.role_id] if self.role_id else []
    
    def __repr__(self):
        return f"<SysUser(user_id={self.user_id}, username={self.username})>"
