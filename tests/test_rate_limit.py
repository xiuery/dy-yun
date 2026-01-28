"""
测试限流中间件
"""
import asyncio
import time
import httpx


async def test_rate_limit():
    """测试限流功能"""
    base_url = "http://localhost:8000"
    
    print("🧪 开始测试限流功能...")
    print(f"📌 目标: {base_url}/health")
    print(f"⏱️  配置: 60秒内最多100次请求\n")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        success_count = 0
        blocked_count = 0
        start_time = time.time()
        
        # 发送 150 次请求（超过限制）
        for i in range(1, 151):
            try:
                response = await client.get(f"{base_url}/health")
                
                if response.status_code == 200:
                    success_count += 1
                    if i % 50 == 0:
                        print(f"✅ 第 {i} 次请求成功 (状态码: {response.status_code})")
                elif response.status_code == 429:
                    blocked_count += 1
                    if blocked_count == 1:
                        print(f"\n🚫 第 {i} 次请求被限流!")
                        print(f"   响应: {response.json()}")
                        print(f"   Retry-After: {response.headers.get('Retry-After')} 秒")
                    
                    # 收到限流后停止测试
                    print(f"\n📊 限流测试完成!")
                    break
                    
            except Exception as e:
                print(f"❌ 请求失败: {e}")
                break
            
            # 控制请求速度
            await asyncio.sleep(0.01)
        
        elapsed = time.time() - start_time
        
        print(f"\n" + "="*50)
        print(f"📈 测试结果:")
        print(f"   ✅ 成功请求: {success_count}")
        print(f"   🚫 被限流: {blocked_count}")
        print(f"   ⏱️  总耗时: {elapsed:.2f}秒")
        print(f"   📊 QPS: {success_count/elapsed:.2f} req/s")
        print("="*50)


if __name__ == "__main__":
    asyncio.run(test_rate_limit())
