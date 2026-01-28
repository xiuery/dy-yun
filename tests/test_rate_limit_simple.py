"""
简单的限流测试 - 使用requests同步方式
"""
import time
import requests


def test_rate_limit_simple():
    """简单的限流测试"""
    url = "http://localhost:8000/health"
    
    print("🧪 开始限流测试...")
    print(f"📌 目标: {url}")
    print(f"⏱️  配置: 100次/60秒\n")
    
    success = 0
    blocked = 0
    
    # 快速发送120次请求
    for i in range(1, 121):
        try:
            resp = requests.get(url, timeout=5)
            
            if resp.status_code == 200:
                success += 1
                if i % 20 == 0:
                    print(f"✅ 第{i:3d}次 - 200 OK")
            elif resp.status_code == 429:
                blocked += 1
                if blocked == 1:
                    print(f"\n🚫 第{i:3d}次 - 429 被限流!")
                    print(f"   响应: {resp.json()}")
                    retry_after = resp.headers.get('Retry-After')
                    if retry_after:
                        print(f"   Retry-After: {retry_after}秒")
                elif blocked % 10 == 0:
                    print(f"🚫 第{i:3d}次 - 429 (已被限流{blocked}次)")
                    
        except Exception as e:
            print(f"❌ 第{i:3d}次 - 错误: {e}")
            break
        
        # 控制速度
        time.sleep(0.01)
    
    print(f"\n{'='*50}")
    print(f"📊 测试结果:")
    print(f"   ✅ 成功: {success}")
    print(f"   🚫 限流: {blocked}")
    print(f"   📈 总计: {success + blocked}")
    print(f"{'='*50}")


if __name__ == "__main__":
    test_rate_limit_simple()
