# Pydantic 模式 - 用户
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    """用户角色"""
    ADMIN = "admin"
    MERCHANT = "merchant"
    STAFF = "staff"

# 用户创建
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description="手机号")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    role: UserRole = UserRole.MERCHANT

# 用户登录
class UserLogin(BaseModel):
    username: str = Field(..., description="用户名或手机号或邮箱")
    password: str = Field(..., description="密码")

# 用户响应
class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    phone: Optional[str]
    role: UserRole
    status: bool
    avatar_url: Optional[str]
    last_login_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token 响应
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

# 刷新 Token
class TokenRefresh(BaseModel):
    refresh_token: str
