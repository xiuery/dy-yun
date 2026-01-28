"""
Base service - 基础服务类
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    """基础服务类"""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.errors: List[str] = []
        
    def add_error(self, error: str) -> "BaseService":
        """添加错误"""
        self.errors.append(error)
        return self
        
    def get_errors(self) -> List[str]:
        """获取所有错误"""
        return self.errors
