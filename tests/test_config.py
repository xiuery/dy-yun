"""
配置单元测试
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import set_config_path, get_settings


def test_default_config():
    """测试默认配置加载"""
    print("🧪 测试默认配置...")
    set_config_path("config/settings.yaml")
    settings = get_settings()
    
    assert settings.application.port == 8000, "默认端口应为8000"
    assert settings.cache.driver == "memory", "默认缓存应为memory"
    assert settings.log.level == "INFO", "默认日志级别应为INFO"
    assert settings.rate_limit.enabled == True, "默认应启用限流"
    assert settings.rate_limit.requests == 100, "默认限流为100次/分钟"
    
    print("✅ 默认配置测试通过")


def test_dev_config():
    """测试开发环境配置加载"""
    print("\n🧪 测试开发环境配置...")
    set_config_path("config/settings.dev.yaml")
    settings = get_settings()
    
    assert settings.application.port == 8001, "开发端口应为8001"
    assert settings.cache.driver == "redis", "开发缓存应为redis"
    assert settings.log.level == "DEBUG", "开发日志级别应为DEBUG"
    assert settings.rate_limit.enabled == True, "开发环境应启用限流"
    assert settings.rate_limit.requests == 200, "开发限流为200次/分钟"
    assert settings.rate_limit.use_redis == True, "开发环境限流应使用Redis"
    
    print("✅ 开发配置测试通过")


def test_config_values():
    """测试配置值详情"""
    print("\n🧪 配置详情检查...")
    set_config_path("config/settings.yaml")
    settings = get_settings()
    
    print(f"\n📋 应用配置:")
    print(f"   名称: {settings.application.name}")
    print(f"   版本: {settings.application.version}")
    print(f"   端口: {settings.application.port}")
    print(f"   模式: {settings.application.mode}")
    
    print(f"\n📋 数据库配置:")
    print(f"   驱动: {settings.database.driver}")
    print(f"   源: {settings.database.source}")
    
    print(f"\n📋 缓存配置:")
    print(f"   驱动: {settings.cache.driver}")
    print(f"   主机: {settings.cache.host}")
    print(f"   端口: {settings.cache.port}")
    
    print(f"\n📋 限流配置:")
    print(f"   启用: {settings.rate_limit.enabled}")
    print(f"   限制: {settings.rate_limit.requests}次/{settings.rate_limit.window}秒")
    print(f"   Redis: {settings.rate_limit.use_redis}")
    
    print(f"\n📋 日志配置:")
    print(f"   级别: {settings.log.level}")
    print(f"   文件: {settings.log.file}")
    
    print("\n✅ 配置检查完成")


if __name__ == "__main__":
    try:
        test_default_config()
        test_dev_config()
        test_config_values()
        print("\n" + "="*50)
        print("🎉 所有配置测试通过!")
        print("="*50)
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)
