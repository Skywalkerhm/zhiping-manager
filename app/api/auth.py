# 认证 API 路由
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Any
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, TokenRefresh
from app.services.auth_service import AuthService
from app.api.deps import get_current_user, get_client_ip
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=UserResponse, summary="用户注册")
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    注册新用户
    
    - **username**: 用户名（3-50 字符）
    - **email**: 邮箱（可选）
    - **phone**: 手机号（可选）
    - **password**: 密码（6-50 字符）
    - **role**: 角色（merchant/admin/staff）
    """
    try:
        user = AuthService.register(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=TokenResponse, summary="用户登录")
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    用户登录
    
    - **username**: 用户名/邮箱/手机号
    - **password**: 密码
    
    返回访问令牌和刷新令牌
    """
    try:
        ip_address = get_client_ip(request) if request else None
        user, access_token, refresh_token = AuthService.login(
            db, 
            login_data.username, 
            login_data.password,
            ip_address
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800  # 30 分钟
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/refresh", response_model=TokenResponse, summary="刷新令牌")
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    使用刷新令牌获取新的访问令牌
    """
    try:
        new_access, new_refresh = AuthService.refresh_token(db, token_data.refresh_token)
        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
            "expires_in": 1800
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前登录用户的信息
    """
    return current_user

@router.post("/logout", summary="用户登出")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    用户登出（客户端删除 Token 即可）
    """
    return {"message": "登出成功"}
