"""
Redis Queue Adapter - Redis 队列适配器
"""
import asyncio
import json
from typing import Dict, Optional, Any
from loguru import logger
import redis.asyncio as aioredis

from .adapter import AdapterQueue, ConsumerFunc
from .message import Message


class Redis(AdapterQueue):
    """Redis 队列适配器 - 使用 Redis Stream 实现分布式队列"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        consumer_group: str = "default_group"
    ):
        """
        初始化 Redis 队列
        
        Args:
            host: Redis 主机地址
            port: Redis 端口
            db: Redis 数据库编号
            password: Redis 密码
            consumer_group: 消费者组名称
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.consumer_group = consumer_group
        self._client: Optional[aioredis.Redis] = None
        self._consumers: Dict[str, ConsumerFunc] = {}
        self._tasks: Dict[str, asyncio.Task] = {}
        self._running = False
        self._shutdown_event = asyncio.Event()
    
    def string(self) -> str:
        """返回适配器类型"""
        return "redis"
    
    @classmethod
    async def create(
        cls,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        consumer_group: str = "default_group"
    ) -> "Redis":
        """
        创建并初始化 Redis 队列适配器
        
        Args:
            host: Redis 主机
            port: Redis 端口
            db: 数据库编号
            password: 密码
            consumer_group: 消费者组名称
            
        Returns:
            Redis: 初始化完成的 Redis 队列实例
        """
        instance = cls(host, port, db, password, consumer_group)
        await instance._connect()
        return instance
    
    async def _connect(self) -> None:
        """连接到 Redis"""
        try:
            self._client = await aioredis.from_url(
                f"redis://{self.host}:{self.port}/{self.db}",
                password=self.password,
                encoding="utf-8",
                decode_responses=True
            )
            # 测试连接
            await self._client.ping()
            logger.info(f"Redis queue connected: {self.host}:{self.port}/{self.db}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def get_client(self) -> aioredis.Redis:
        """获取原生 Redis 客户端"""
        if not self._client:
            raise RuntimeError("Redis client not initialized")
        return self._client
    
    async def append(self, message: Message) -> None:
        """
        追加消息到 Redis Stream
        
        Args:
            message: 队列消息
        """
        if not self._client:
            raise RuntimeError("Redis client not initialized")
        
        try:
            stream = await message.get_stream()
            values = await message.get_values()
            
            # 将消息数据序列化为字符串
            message_data = {
                "id": message.get_id(),
                "stream": stream,
                "values": json.dumps(values),
                "error_count": str(message.get_error_count())
            }
            
            # 使用 XADD 添加到 Stream
            message_id = await self._client.xadd(stream, message_data)
            logger.debug(f"Message {message_id} appended to Redis stream {stream}")
        
        except Exception as e:
            logger.error(f"Failed to append message to Redis: {e}")
            raise
    
    def register(self, name: str, consumer_func: ConsumerFunc) -> None:
        """
        注册消费者
        
        Args:
            name: 队列名称（Stream 名称）
            consumer_func: 消费者处理函数
        """
        self._consumers[name] = consumer_func
        logger.info(f"Consumer registered for Redis stream: {name}")
    
    async def _ensure_consumer_group(self, stream: str) -> None:
        """确保消费者组存在"""
        if not self._client:
            return
        
        try:
            # 尝试创建消费者组
            await self._client.xgroup_create(
                stream,
                self.consumer_group,
                id="0",
                mkstream=True
            )
            logger.debug(f"Created consumer group {self.consumer_group} for stream {stream}")
        except aioredis.ResponseError as e:
            # 如果组已存在，忽略错误
            if "BUSYGROUP" not in str(e):
                raise
    
    async def _consume_stream(self, stream: str, consumer_func: ConsumerFunc) -> None:
        """
        从 Redis Stream 消费消息
        
        Args:
            stream: Stream 名称
            consumer_func: 消费者函数
        """
        if not self._client:
            return
        
        consumer_name = f"consumer_{asyncio.current_task().get_name()}"
        logger.debug(f"Started consuming from Redis stream: {stream} as {consumer_name}")
        
        # 确保消费者组存在
        await self._ensure_consumer_group(stream)
        
        while self._running:
            try:
                # 从 Stream 读取消息
                messages = await self._client.xreadgroup(
                    self.consumer_group,
                    consumer_name,
                    {stream: ">"},
                    count=10,
                    block=1000  # 1秒超时
                )
                
                if not messages:
                    continue
                
                # 处理每条消息
                for stream_name, stream_messages in messages:
                    for msg_id, msg_data in stream_messages:
                        try:
                            # 重构消息对象
                            message = Message(
                                id=msg_data.get("id", msg_id),
                                stream=msg_data.get("stream", stream),
                                values=json.loads(msg_data.get("values", "{}")),
                                error_count=int(msg_data.get("error_count", "0"))
                            )
                            
                            # 调用消费者函数
                            await consumer_func(message)
                            
                            # 确认消息处理成功
                            await self._client.xack(stream, self.consumer_group, msg_id)
                            logger.debug(f"Message {msg_id} processed and acked")
                        
                        except Exception as e:
                            logger.error(f"Error processing Redis message {msg_id}: {e}")
                            
                            # 错误重试逻辑
                            error_count = int(msg_data.get("error_count", "0"))
                            if error_count < 3:
                                # 增加错误计数并重新添加消息
                                msg_data["error_count"] = str(error_count + 1)
                                await self._client.xadd(stream, msg_data)
                                logger.warning(f"Message {msg_id} requeued (attempt {error_count + 1})")
                            else:
                                logger.error(f"Message {msg_id} failed after 3 attempts")
                            
                            # 确认原消息
                            await self._client.xack(stream, self.consumer_group, msg_id)
            
            except asyncio.CancelledError:
                logger.debug(f"Consumer for stream {stream} cancelled")
                break
            except Exception as e:
                logger.error(f"Unexpected error in Redis consumer {stream}: {e}")
                await asyncio.sleep(1)  # 避免快速循环错误
        
        logger.debug(f"Stopped consuming from Redis stream: {stream}")
    
    async def run(self) -> None:
        """启动所有注册的消费者"""
        self._running = True
        
        # 为每个注册的消费者创建任务
        for stream, consumer_func in self._consumers.items():
            task = asyncio.create_task(
                self._consume_stream(stream, consumer_func),
                name=f"redis_consumer_{stream}"
            )
            self._tasks[stream] = task
        
        logger.info(f"Redis queue adapter started with {len(self._tasks)} consumers")
        
        # 等待 shutdown 信号
        await self._shutdown_event.wait()
        
        logger.info("Redis queue adapter stopped")
    
    async def shutdown(self) -> None:
        """关闭队列"""
        logger.info("Shutting down Redis queue adapter...")
        self._running = False
        
        # 取消所有消费者任务
        for stream, task in self._tasks.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                logger.debug(f"Consumer task for stream {stream} cancelled")
        
        # 发送 shutdown 信号
        self._shutdown_event.set()
        logger.info("Redis queue adapter shutdown complete")
    
    async def close(self) -> None:
        """关闭 Redis 连接"""
        if self._running:
            await self.shutdown()
        
        if self._client:
            await self._client.close()
            logger.info("Redis queue connection closed")
