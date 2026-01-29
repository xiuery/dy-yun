"""
测试认证响应处理函数
"""
import asyncio
from datetime import datetime, timedelta
from fastapi import Request
from starlette.datastructures import Headers
from common.middleware.handler.auth import (
    unauthorized_handler,
    login_response,
    refresh_response,
    logout_response
)


async def test_unauthorized_handler():
    """测试未授权响应"""
    print("\n" + "="*60)
    print("🧪 测试 unauthorized_handler")
    print("="*60)
    
    # 创建模拟请求
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/login",
        "headers": [],
        "query_string": b"",
    }
    request = Request(scope)
    
    # 调用函数
    response = await unauthorized_handler(request, 401, "用户名或密码错误")
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.body.decode('utf-8')}")
    print("✅ unauthorized_handler 测试完成\n")


async def test_login_response():
    """测试登录成功响应"""
    print("="*60)
    print("🧪 测试 login_response")
    print("="*60)
    
    # 创建模拟请求
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/login",
        "headers": [],
        "query_string": b"",
    }
    request = Request(scope)
    
    # 模拟token和过期时间
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_token"
    expire = datetime.utcnow() + timedelta(hours=24)
    
    # 调用函数
    response = await login_response(request, token, expire)
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.body.decode('utf-8')}")
    print("✅ login_response 测试完成\n")


async def test_refresh_response():
    """测试刷新成功响应"""
    print("="*60)
    print("🧪 测试 refresh_response")
    print("="*60)
    
    # 创建模拟请求
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/refresh_token",
        "headers": [],
        "query_string": b"",
    }
    request = Request(scope)
    
    # 模拟token和过期时间
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refreshed_token"
    expire = datetime.utcnow() + timedelta(hours=24)
    
    # 调用函数
    response = await refresh_response(request, token, expire)
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.body.decode('utf-8')}")
    print("✅ refresh_response 测试完成\n")


async def test_logout_response():
    """测试登出成功响应"""
    print("="*60)
    print("🧪 测试 logout_response")
    print("="*60)
    
    # 创建模拟请求
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/logout",
        "headers": [],
        "query_string": b"",
    }
    request = Request(scope)
    
    # 调用函数
    response = await logout_response(request)
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.body.decode('utf-8')}")
    print("✅ logout_response 测试完成\n")


async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("开始测试认证响应处理函数")
    print("="*60)
    
    await test_unauthorized_handler()
    await test_login_response()
    await test_refresh_response()
    await test_logout_response()
    
    print("="*60)
    print("✅ 所有测试完成")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
