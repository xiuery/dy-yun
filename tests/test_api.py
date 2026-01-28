"""
API接口测试
"""
import requests


def test_health_endpoint():
    """测试健康检查接口"""
    print("🧪 测试健康检查接口...")
    
    url = "http://localhost:8000/health"
    response = requests.get(url)
    
    assert response.status_code == 200, f"期望状态码200，实际{response.status_code}"
    
    data = response.json()
    assert "status" in data, "响应应包含status字段"
    assert "version" in data, "响应应包含version字段"
    assert data["status"] == "healthy", "状态应为healthy"
    
    print(f"✅ 健康检查通过: {data}")


def test_response_headers():
    """测试响应头"""
    print("\n🧪 测试响应头...")
    
    url = "http://localhost:8000/health"
    response = requests.get(url)
    
    # 检查限流相关响应头
    assert "X-RateLimit-Limit" in response.headers, "应包含X-RateLimit-Limit响应头"
    assert "X-RateLimit-Window" in response.headers, "应包含X-RateLimit-Window响应头"
    
    print(f"✅ X-RateLimit-Limit: {response.headers['X-RateLimit-Limit']}")
    print(f"✅ X-RateLimit-Window: {response.headers['X-RateLimit-Window']}")


def test_404_endpoint():
    """测试不存在的路由"""
    print("\n🧪 测试404错误...")
    
    url = "http://localhost:8000/not-exists"
    response = requests.get(url)
    
    assert response.status_code == 404, f"期望状态码404，实际{response.status_code}"
    
    print(f"✅ 404测试通过")


if __name__ == "__main__":
    try:
        test_health_endpoint()
        test_response_headers()
        test_404_endpoint()
        print("\n" + "="*50)
        print("🎉 所有API测试通过!")
        print("="*50)
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器，请先启动应用:")
        print("   python main.py -c config/settings.yaml")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
