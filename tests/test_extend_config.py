#!/usr/bin/env python
"""测试扩展配置功能"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import get_settings, set_config_path

def test_extend_config():
    """测试扩展配置"""
    print("=" * 60)
    print("测试扩展配置功能")
    print("=" * 60)
    
    # 使用 dev 配置
    set_config_path("config/settings.dev.yaml")
    settings = get_settings()
    
    print("\n1. 测试扩展配置对象存在:")
    assert hasattr(settings, 'extend'), "settings 应该有 extend 属性"
    print(f"   ✓ settings.extend 存在: {type(settings.extend)}")
    
    print("\n2. 测试扩展配置内容:")
    extend_dict = settings.extend.model_dump()
    print(f"   扩展配置内容: {extend_dict}")
    
    print("\n3. 测试高德地图配置:")
    if hasattr(settings.extend, 'amap') and settings.extend.amap:
        amap_key = settings.extend.amap.get('key', '')
        print(f"   ✓ AMap Key: {amap_key}")
    else:
        print("   - AMap 配置未设置")
    
    print("\n4. 测试自定义配置:")
    if hasattr(settings.extend, 'custom') and settings.extend.custom:
        custom = settings.extend.custom
        print(f"   ✓ Custom 配置: {custom}")
        if 'debug_mode' in custom:
            print(f"   ✓ Debug Mode: {custom['debug_mode']}")
        if 'feature_flags' in custom:
            print(f"   ✓ Feature Flags: {custom['feature_flags']}")
    else:
        print("   - Custom 配置未设置")
    
    print("\n5. 测试配置完整性:")
    all_configs = {
        'application': settings.application.name,
        'jwt': settings.jwt.algorithm,
        'database': settings.database.driver,
        'cache': settings.cache.driver,
        'log': settings.log.level,
        'extend': 'loaded' if extend_dict else 'empty'
    }
    for key, value in all_configs.items():
        print(f"   ✓ {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✓ 扩展配置测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_extend_config()
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
