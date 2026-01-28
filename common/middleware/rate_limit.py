"""
Rate limit middleware - 限流中间件
基于滑动窗口算法实现，支持 Redis 和内存存储
"""
import time
from typing import Dict, Optional
from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from core.runtime import runtime
from core.logger import get_request_logger


class RateLimiter:
    """限流器"""
    
    def __init__(
        self,
        requests: int = 100,
        window: int = 60,
        use_redis: bool = False
    ):
        """
        初始化限流器
        
        Args:
            requests: 时间窗口内允许的最大请求数
            window: 时间窗口大小（秒）
            use_redis: 是否使用 Redis 存储（适合分布式环境）
        """
        self.requests = requests
        self.window = window
        self.use_redis = use_redis
        
        # 内存存储：{key: [(timestamp1, timestamp2, ...)]}
        self.memory_store: Dict[str, list] = {}
    
    async def is_allowed(self, key: str) -> tuple[bool, Optional[int]]:
        """
        检查是否允许请求
        
        Args:
            key: 限流标识（如 IP 地址或用户 ID）
            
        Returns:
            (是否允许, 剩余秒数)
        """
        current_time = int(time.time())
        window_start = current_time - self.window
        
        if self.use_redis:
            return await self._check_redis(key, current_time, window_start)
        else:
            return await self._check_memory(key, current_time, window_start)
    
    async def _check_redis(self, key: str, current_time: int, window_start: int) -> tuple[bool, Optional[int]]:
        """Redis 存储的限流检查"""
        cache_client = runtime.get_cache_client()
        if not cache_client:
            # Redis 未配置，回退到内存模式
            return await self._check_memory(key, current_time, window_start)
        
        try:
            # 使用 Redis sorted set 实现滑动窗口
            cache_key = f"rate_limit:{key}"
            
            # 移除窗口外的记录
            await cache_client.zremrangebyscore(cache_key, 0, window_start)
            
            # 获取当前窗口内的请求数
            count = await cache_client.zcard(cache_key)
            
            if count >= self.requests:
                # 获取最早的请求时间
                oldest = await cache_client.zrange(cache_key, 0, 0, withscores=True)
                if oldest:
                    retry_after = int(oldest[0][1]) + self.window - current_time
                    return False, max(retry_after, 1)
                return False, self.window
            
            # 添加当前请求
            await cache_client.zadd(cache_key, {str(current_time): current_time})
            
            # 设置过期时间（窗口大小 + 缓冲）
            await cache_client.expire(cache_key, self.window + 10)
            
            return True, None
            
        except Exception as e:
            # Redis 错误时回退到内存模式
            logger = get_request_logger()
            logger.warning(f"Redis rate limit failed, fallback to memory: {e}")
            return await self._check_memory(key, current_time, window_start)
    
    async def _check_memory(self, key: str, current_time: int, window_start: int) -> tuple[bool, Optional[int]]:
        """内存存储的限流检查"""
        # 获取或初始化记录
        if key not in self.memory_store:
            self.memory_store[key] = []
        
        requests = self.memory_store[key]
        
        # 移除窗口外的记录
        requests[:] = [ts for ts in requests if ts > window_start]
        
        if len(requests) >= self.requests:
            # 计算需要等待的时间
            retry_after = requests[0] + self.window - current_time
            return False, max(retry_after, 1)
        
        # 添加当前请求
        requests.append(current_time)
        
        return True, None


# 全局限流器实例
_rate_limiter: Optional[RateLimiter] = None


def init_rate_limiter(
    requests: int = 100,
    window: int = 60,
    use_redis: bool = False
) -> None:
    """初始化全局限流器"""
    global _rate_limiter
    _rate_limiter = RateLimiter(requests=requests, window=window, use_redis=use_redis)


def get_rate_limiter() -> Optional[RateLimiter]:
    """获取限流器实例"""
    return _rate_limiter


async def rate_limit_middleware(request: Request, call_next):
    """限流中间件"""
    limiter = get_rate_limiter()
    
    # 如果未初始化限流器，直接放行
    if not limiter:
        return await call_next(request)
    
    # 获取客户端标识（优先使用用户 ID，否则使用 IP）
    client_id = None
    if hasattr(request.state, "user_id"):
        client_id = f"user:{request.state.user_id}"
    else:
        # 从 X-Forwarded-For 或 X-Real-IP 获取真实 IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_id = f"ip:{forwarded.split(',')[0].strip()}"
        else:
            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                client_id = f"ip:{real_ip}"
            else:
                client_id = f"ip:{request.client.host}" if request.client else "ip:unknown"
    
    # 检查限流
    allowed, retry_after = await limiter.is_allowed(client_id)
    
    if not allowed:
        logger = get_request_logger(getattr(request.state, "request_id", ""))
        logger.warning(f"Rate limit exceeded: {client_id} {request.method} {request.url.path}")
        
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": HTTP_429_TOO_MANY_REQUESTS,
                "message": "请求过于频繁，请稍后再试",
                "retry_after": retry_after
            },
            headers={"Retry-After": str(retry_after)} if retry_after else {}
        )
    
    response = await call_next(request)
    
    # 添加限流信息到响应头
    response.headers["X-RateLimit-Limit"] = str(limiter.requests)
    response.headers["X-RateLimit-Window"] = str(limiter.window)
    
    return response
