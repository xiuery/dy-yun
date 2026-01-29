"""
Auth Router - 认证路由
"""
from fastapi import APIRouter, Request, Depends

from core.jwtauth import MapClaims
from common.middleware import jwt_required, get_jwt_auth

router = APIRouter(prefix="/api/v1", tags=["认证"])


@router.post("/login")
async def login(request: Request):
    auth = get_jwt_auth()
    return await auth.login_handler(request)


@router.post("/refresh_token")
async def refresh_token(request: Request):
    auth = get_jwt_auth()
    return await auth.refresh_handler(request)


@router.post("/logout")
async def logout(request: Request, claims: MapClaims = Depends(jwt_required)):
    auth = get_jwt_auth()
    return await auth.logout_handler(request)


@router.get("/user/profile")
async def get_user_info(request: Request, claims: MapClaims = Depends(jwt_required)):

    return JSONResponse(
        status_code=200,
        content={
            "code": 200,
            "msg": "success",
            "data": {
                "user_id": user.get_user_id(request),
                "username": user.get_username(request),
                "rolekey": user.get_rolekey(request),
                "role_id": user.get_role_id(request),
                "dept_id": user.get_dept_id(request),
            }
        }
    )
