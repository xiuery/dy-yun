# Makefile for dy-yun
# 企业级中后台应用框架 v0.1

.PHONY: help install run dev test lint format clean

help:  ## 显示帮助信息
	@echo "dy-yun - 企业级中后台应用框架 v0.1"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## 安装依赖
	pip install -r requirements.txt

install-dev:  ## 安装开发依赖
	poetry install

run:  ## 启动服务（生产模式）
	python main.py

dev:  ## 启动服务（开发模式）
	python cmd/cli.py server --reload

init-db:  ## 初始化数据库表
	python cmd/cli.py init-db

migrate:  ## 运行数据库迁移
	python cmd/cli.py migrate up

test:  ## 运行测试
	pytest tests/ -v

lint:  ## 代码检查
	ruff check .
	mypy .

format:  ## 代码格式化
	black .
	isort .

clean:  ## 清理临时文件
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf *.egg-info dist build

docker-build:  ## 构建 Docker 镜像
	docker build -t dy-yun:0.1 .

docker-run:  ## 运行 Docker 容器
	docker-compose up -d

docker-stop:  ## 停止 Docker 容器
	docker-compose down
