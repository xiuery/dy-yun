"""
登录接口测试
"""
import requests


BASE_URL = "http://localhost:8001"


def test_login_success():
    """测试成功登录"""
    print("🧪 测试成功登录...")
    
    url = f"{BASE_URL}/api/v1/login"
    data = {
        "username": "admin",
        "password": "123456",
        "code": "1234",  # 开发模式可跳过验证码校验
        "uuid": "test-uuid"
    }
    
    response = requests.post(url, json=data)
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    assert response.status_code == 200, f"期望状态码200，实际{response.status_code}"
    
    result = response.json()
    assert "code" in result, "响应应包含code字段"
    assert "data" in result, "响应应包含data字段"
    assert result["code"] == 200, f"期望code为200，实际{result['code']}"
    
    # 检查token
    data = result["data"]
    assert "token" in data, "data应包含token字段"
    assert "expire" in data, "data应包含expire字段"
    
    token = data["token"]
    assert len(token) > 0, "token不应为空"
    
    print(f"✅ 登录成功，token: {token[:50]}...")
    return token


def test_login_invalid_username():
    """测试无效用户名"""
    print("\n🧪 测试无效用户名...")
    
    url = f"{BASE_URL}/api/v1/login"
    data = {
        "username": "notexist",
        "password": "admin123",
        "code": "1234",
        "uuid": "test-uuid"
    }
    
    response = requests.post(url, json=data)
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    # 认证失败应返回401
    assert response.status_code == 401, f"期望状态码401，实际{response.status_code}"
    
    result = response.json()
    assert "code" in result, "响应应包含code字段"
    assert result["code"] == 401, f"期望code为401，实际{result['code']}"
    
    print(f"✅ 无效用户名测试通过")


def test_login_invalid_password():
    """测试无效密码"""
    print("\n🧪 测试无效密码...")
    
    url = f"{BASE_URL}/api/v1/login"
    data = {
        "username": "admin",
        "password": "wrongpassword",
        "code": "1234",
        "uuid": "test-uuid"
    }
    
    response = requests.post(url, json=data)
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    # 认证失败应返回401
    assert response.status_code == 401, f"期望状态码401，实际{response.status_code}"
    
    result = response.json()
    assert "code" in result, "响应应包含code字段"
    assert result["code"] == 401, f"期望code为401，实际{result['code']}"
    
    print(f"✅ 无效密码测试通过")


def test_login_missing_fields():
    """测试缺少必填字段"""
    print("\n🧪 测试缺少必填字段...")
    
    url = f"{BASE_URL}/api/v1/login"
    
    # 测试缺少username
    data = {
        "password": "admin123",
        "code": "1234",
        "uuid": "test-uuid"
    }
    
    response = requests.post(url, json=data)
    print(f"缺少username - 响应状态码: {response.status_code}")
    assert response.status_code == 422, f"期望状态码422，实际{response.status_code}"
    
    # 测试缺少password
    data = {
        "username": "admin",
        "code": "1234",
        "uuid": "test-uuid"
    }
    
    response = requests.post(url, json=data)
    print(f"缺少password - 响应状态码: {response.status_code}")
    assert response.status_code == 422, f"期望状态码422，实际{response.status_code}"
    
    print(f"✅ 缺少必填字段测试通过")


def test_login_empty_username():
    """测试空用户名"""
    print("\n🧪 测试空用户名...")
    
    url = f"{BASE_URL}/api/v1/login"
    data = {
        "username": "  ",  # 空格会被trim
        "password": "admin123",
        "code": "1234",
        "uuid": "test-uuid"
    }
    
    response = requests.post(url, json=data)
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    # Pydantic验证应返回422
    assert response.status_code == 422, f"期望状态码422，实际{response.status_code}"
    
    print(f"✅ 空用户名测试通过")


def test_get_user_profile():
    """测试获取用户信息（需要先登录）"""
    print("\n🧪 测试获取用户信息...")
    
    # 先登录获取token
    token = test_login_success()
    
    # 使用token访问用户信息接口
    url = f"{BASE_URL}/api/v1/user/profile"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    assert response.status_code == 200, f"期望状态码200，实际{response.status_code}"
    
    result = response.json()
    assert result["code"] == 200, f"期望code为200，实际{result['code']}"
    
    data = result["data"]
    assert "user_id" in data, "data应包含user_id字段"
    assert "username" in data, "data应包含username字段"
    assert "rolekey" in data, "data应包含rolekey字段"
    
    print(f"✅ 用户信息获取成功: {data}")


if __name__ == "__main__":
    print("=" * 60)
    print("开始登录接口测试")
    print("=" * 60)
    
    try:
        test_login_success()
        test_login_invalid_username()
        test_login_invalid_password()
        test_login_missing_fields()
        test_login_empty_username()
        test_get_user_profile()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
