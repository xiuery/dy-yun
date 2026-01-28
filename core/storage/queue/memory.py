"""
Memory Queue Adapter - 内存队列适配器
"""
import asyncio
from typing import Dict
from loguru import logger
from uuid import uuid4

from .adapter import AdapterQueue, ConsumerFunc
from .message import Message


class Memory(AdapterQueue):
    """内存队列适配器 - 适用于单机开发环境"""
    
    def __init__(self, pool_num: int = 0):
        """
        初始化内存队列
        
        Args:
            pool_num: 队列缓冲区大小，0 表示无限制
        """
        self.pool_num = pool_num
        self._queues: Dict[str, asyncio.Queue] = {}
        self._tasks: Dict[str, asyncio.Task] = {}
        self._running = False
        self._shutdown_event = asyncio.Event()
        logger.debug(f"Memory queue adapter initialized with pool_num={pool_num}")
    
    def string(self) -> str:
        """返回适配器类型"""
        return "memory"
    
    def _make_queue(self) -> asyncio.Queue:
        """创建队列实例"""
        if self.pool_num <= 0:
            return asyncio.Queue()
        return asyncio.Queue(maxsize=self.pool_num)
    
    async def append(self, message: Message) -> None:
        """
        追加消息到队列
        
        Args:
            message: 队列消息
        """
        stream = await message.get_stream()
        
        # 如果队列不存在，创建新队列
        if stream not in self._queues:
            self._queues[stream] = self._make_queue()
            logger.debug(f"Created new queue: {stream}")
        
        # 生成消息 ID
        if not message.get_id():
            message.set_id(str(uuid4()))
        
        # 将消息放入队列
        await self._queues[stream].put(message)
        logger.debug(f"Message {message.get_id()} appended to queue {stream}")
    
    def register(self, name: str, consumer_func: ConsumerFunc) -> None:
        """
        注册消费者
        
        Args:
            name: 队列名称
            consumer_func: 消费者处理函数
        """
        # 确保队列存在
        if name not in self._queues:
            self._queues[name] = self._make_queue()
            logger.debug(f"Created queue for consumer: {name}")
        
        # 创建消费者任务
        task = asyncio.create_task(self._consume_messages(name, consumer_func))
        self._tasks[name] = task
        logger.info(f"Consumer registered for queue: {name}")
    
    async def _consume_messages(self, name: str, consumer_func: ConsumerFunc) -> None:
        """
        消费消息的内部方法
        
        Args:
            name: 队列名称
            consumer_func: 消费者函数
        """
        queue = self._queues[name]
        logger.debug(f"Started consuming messages from queue: {name}")
        
        while self._running or not queue.empty():
            try:
                # 等待消息，超时检查 shutdown
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=0.1)
                except asyncio.TimeoutError:
                    if not self._running:
                        break
                    continue
                
                # 处理消息
                try:
                    await consumer_func(message)
                    logger.debug(f"Message {message.get_id()} processed successfully")
                except Exception as e:
                    logger.error(f"Error processing message {message.get_id()}: {e}")
                    
                    # 错误重试机制（最多3次）
                    if message.get_error_count() < 3:
                        message.set_error_count(message.get_error_count() + 1)
                        # 延迟重试，每次延迟时间递增
                        delay = message.get_error_count()
                        logger.warning(f"Retrying message {message.get_id()} after {delay}s (attempt {message.get_error_count()})")
                        await asyncio.sleep(delay)
                        await queue.put(message)
                    else:
                        logger.error(f"Message {message.get_id()} failed after 3 attempts, discarding")
                
                queue.task_done()
            
            except asyncio.CancelledError:
                logger.debug(f"Consumer task for queue {name} cancelled")
                break
            except Exception as e:
                logger.error(f"Unexpected error in consumer {name}: {e}")
        
        logger.debug(f"Stopped consuming messages from queue: {name}")
    
    async def run(self) -> None:
        """启动队列消费者"""
        self._running = True
        logger.info(f"Memory queue adapter started with {len(self._tasks)} consumers")
        
        # 等待 shutdown 信号
        await self._shutdown_event.wait()
        
        logger.info("Memory queue adapter stopped")
    
    async def shutdown(self) -> None:
        """关闭队列"""
        logger.info("Shutting down memory queue adapter...")
        self._running = False
        
        # 等待所有队列处理完成
        for name, queue in self._queues.items():
            try:
                await asyncio.wait_for(queue.join(), timeout=5.0)
                logger.debug(f"Queue {name} drained successfully")
            except asyncio.TimeoutError:
                logger.warning(f"Queue {name} drain timeout, forcing shutdown")
        
        # 取消所有消费者任务
        for name, task in self._tasks.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                logger.debug(f"Consumer task {name} cancelled")
        
        # 发送 shutdown 信号
        self._shutdown_event.set()
        logger.info("Memory queue adapter shutdown complete")
    
    async def close(self) -> None:
        """关闭资源"""
        if self._running:
            await self.shutdown()
