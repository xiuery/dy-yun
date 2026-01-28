"""
Base model - 基础模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from core.database import Base


class BaseModel(Base):
    """基础模型类 - 包含通用审计字段"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    create_by = Column(Integer, nullable=True, index=True, comment="创建者")
    update_by = Column(Integer, nullable=True, index=True, comment="更新者")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="最后更新时间")
    deleted_at = Column(DateTime, nullable=True, index=True, comment="删除时间")
