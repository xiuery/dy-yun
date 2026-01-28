"""
Queue Adapter - 队列适配器抽象基类
"""
from abc import ABC, abstractmethod
from typing import Callable, Awaitable
from .message import Message


# 消费者函数类型：接收 Message 对象，返回 None 或抛出异常
ConsumerFunc = Callable[[Message], Awaitable[None]]


class AdapterQueue(ABC):
    """队列适配器抽象基类"""
    
    @abstractmethod
    def string(self) -> str:
        """
        返回适配器类型名称
        
        Returns:
            str: 适配器类型 (redis/memory)
        """
        pass
    
    @abstractmethod
    async def append(self, message: Message) -> None:
        """
        将消息追加到队列
        
        Args:
            message: 队列消息对象
            
        Raises:
            Exception: 追加失败时抛出异常
        """
        pass
    
    @abstractmethod
    def register(self, name: str, consumer_func: ConsumerFunc) -> None:
        """
        注册消费者函数
        
        Args:
            name: 队列名称
            consumer_func: 消费者处理函数，接收 Message 对象
        """
        pass
    
    @abstractmethod
    async def run(self) -> None:
        """
        启动队列消费者
        阻塞运行，持续处理队列中的消息
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """
        关闭队列，停止所有消费者
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """
        关闭资源连接
        """
        pass
