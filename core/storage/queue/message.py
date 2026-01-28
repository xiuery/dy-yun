"""
Queue Message - 队列消息封装
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from uuid import uuid4
import asyncio


@dataclass
class Message:
    """队列消息类"""
    
    id: str = field(default_factory=lambda: str(uuid4()))
    stream: str = ""
    values: Dict[str, Any] = field(default_factory=dict)
    error_count: int = 0
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)
    
    def get_id(self) -> str:
        """获取消息ID"""
        return self.id
    
    def set_id(self, id: str) -> None:
        """设置消息ID"""
        self.id = id
    
    async def get_stream(self) -> str:
        """获取队列名称"""
        async with self._lock:
            return self.stream
    
    async def set_stream(self, stream: str) -> None:
        """设置队列名称"""
        async with self._lock:
            self.stream = stream
    
    async def get_values(self) -> Dict[str, Any]:
        """获取消息数据"""
        async with self._lock:
            return self.values.copy()
    
    async def set_values(self, values: Dict[str, Any]) -> None:
        """设置消息数据"""
        async with self._lock:
            self.values = values
    
    async def get_prefix(self) -> Optional[str]:
        """获取前缀"""
        async with self._lock:
            return self.values.get("__host")
    
    async def set_prefix(self, prefix: str) -> None:
        """设置前缀"""
        async with self._lock:
            if self.values is None:
                self.values = {}
            self.values["__host"] = prefix
    
    def get_error_count(self) -> int:
        """获取错误次数"""
        return self.error_count
    
    def set_error_count(self, count: int) -> None:
        """设置错误次数"""
        self.error_count = count
    
    def __repr__(self) -> str:
        return f"Message(id={self.id}, stream={self.stream}, error_count={self.error_count})"
