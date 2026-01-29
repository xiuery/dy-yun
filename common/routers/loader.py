"""
Router loader - 路由加载器
集中管理所有路由注册
"""
from fastapi import FastAPI
from app.admin.routers.sys_user import router as user_router
from app.admin.routers.auth import router as auth_router


def register_routers(app: FastAPI) -> None:
    """注册所有路由"""
    # 注册认证路由
    app.include_router(auth_router)
    
    # Admin 模块
    app.include_router(user_router)
