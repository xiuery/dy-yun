# dy-yun 测试目录

## 📋 测试文件说明

### test_config.py
**配置加载测试**
- 测试默认配置（settings.yaml）
- 测试开发配置（settings.dev.yaml）
- 验证配置项正确性

**运行方式：**
```bash
python tests/test_config.py
```

### test_api.py
**API接口测试**
- 健康检查接口测试
- 响应头验证
- 404错误测试

**运行方式：**
```bash
# 先启动服务
python main.py -c config/settings.yaml

# 运行测试
python tests/test_api.py
```

### test_rate_limit.py
**限流功能测试（异步）**
- 使用httpx进行异步请求
- 测试限流触发条件
- 验证429响应和Retry-After头

**运行方式：**
```bash
# 先启动服务
python main.py -c config/settings.yaml

# 运行测试
python tests/test_rate_limit.py
```

### test_rate_limit_simple.py
**限流功能测试（同步）**
- 使用requests进行同步请求
- 简单易懂的测试流程
- 详细的结果输出

**运行方式：**
```bash
# 先启动服务
python main.py -c config/settings.yaml

# 运行测试
python tests/test_rate_limit_simple.py
```

## 🚀 快速开始

### 运行所有测试

```bash
# 1. 配置测试（无需启动服务）
python tests/test_config.py

# 2. 启动服务
python main.py -c config/settings.yaml

# 3. 在另一个终端运行API测试
python tests/test_api.py

# 4. 运行限流测试
python tests/test_rate_limit_simple.py
```

## 📊 测试覆盖范围

- ✅ 配置加载机制
- ✅ API健康检查
- ✅ 响应头验证
- ✅ 限流中间件功能
- ✅ 错误处理

## 🔧 测试环境要求

- Python 3.12+
- 安装依赖：`pip install -r requirements.txt`
- 额外测试依赖：
  - `httpx` - 异步HTTP客户端
  - `requests` - 同步HTTP客户端

## 📝 添加新测试

1. 在 `tests/` 目录创建 `test_*.py` 文件
2. 按照现有测试格式编写
3. 更新本README文档
