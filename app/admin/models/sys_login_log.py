"""
SysLoginLog Model - 系统登录日志模型
"""
from sqlalchemy import Column, String, DateTime
from common.models import BaseModel


class SysLoginLog(BaseModel):
    """系统登录日志模型"""
    __tablename__ = "sys_login_log"
    __table_args__ = {'comment': '系统登录日志表'}
    
    # 用户信息
    username = Column(String(128), comment="用户名")
    
    # 登录信息
    status = Column(String(4), comment="状态")
    ipaddr = Column(String(255), comment="IP地址")
    login_location = Column(String(255), comment="归属地")
    browser = Column(String(255), comment="浏览器")
    os = Column(String(255), comment="系统")
    platform = Column(String(255), comment="固件")
    login_time = Column(DateTime, comment="登录时间")
    
    # 其他信息
    remark = Column(String(255), comment="备注")
    msg = Column(String(255), comment="信息")
    
    # 排除软删除字段
    deleted_at = None
    
    def __repr__(self):
        return f"<SysLoginLog(id={self.id}, username={self.username}, ipaddr={self.ipaddr})>"
