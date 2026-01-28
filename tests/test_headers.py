"""
测试HTTP头中间件
"""
import requests


def test_http_headers():
    """测试HTTP响应头"""
    print("🧪 测试HTTP头中间件...\n")
    
    url = "http://localhost:8001/health"
    
    try:
        response = requests.get(url)
        
        print(f"📊 状态码: {response.status_code}\n")
        
        # 检查安全头
        print("🔒 安全头 (Secure Middleware):")
        security_headers = [
            "Access-Control-Allow-Origin",
            "X-Content-Type-Options",
            "X-XSS-Protection",
        ]
        for header in security_headers:
            value = response.headers.get(header, "❌ 未设置")
            print(f"   {header}: {value}")
        
        # 检查缓存控制头
        print("\n🚫 缓存控制头 (NoCache Middleware):")
        cache_headers = [
            "Cache-Control",
            "Expires",
            "Last-Modified",
        ]
        for header in cache_headers:
            value = response.headers.get(header, "❌ 未设置")
            print(f"   {header}: {value}")
        
        # 检查限流头
        print("\n⏱️ 限流头 (RateLimit Middleware):")
        rate_limit_headers = [
            "X-RateLimit-Limit",
            "X-RateLimit-Window",
        ]
        for header in rate_limit_headers:
            value = response.headers.get(header, "❌ 未设置")
            print(f"   {header}: {value}")
        
        # 检查其他重要头
        print("\n📋 其他响应头:")
        other_headers = [
            "Content-Type",
            "Content-Length",
        ]
        for header in other_headers:
            value = response.headers.get(header, "❌ 未设置")
            print(f"   {header}: {value}")
        
        print("\n✅ HTTP头测试完成!")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请先启动应用:")
        print("   .\.venv\Scripts\python.exe main.py -c config/settings.dev.yaml")
    except Exception as e:
        print(f"❌ 测试失败: {e}")


def test_options_request():
    """测试OPTIONS预检请求"""
    print("\n" + "="*60)
    print("🧪 测试OPTIONS预检请求...\n")
    
    url = "http://localhost:8001/health"
    
    try:
        response = requests.options(url)
        
        print(f"📊 状态码: {response.status_code}\n")
        
        print("🌐 CORS头 (Options Middleware):")
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers",
            "Allow",
        ]
        for header in cors_headers:
            value = response.headers.get(header, "❌ 未设置")
            print(f"   {header}: {value}")
        
        print("\n✅ OPTIONS请求测试完成!")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    test_http_headers()
    test_options_request()
    print("\n" + "="*60)
    print("🎉 所有HTTP头测试完成!")
    print("="*60)
