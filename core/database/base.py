"""
Database base model - 数据库基类模型
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有数据库模型的基类"""
    pass
