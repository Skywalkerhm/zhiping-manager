# 认证服务
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user import User, UserRole
from app.schemas.user import UserCreate
from app.utils.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.config import settings
from app.utils.logger import logger

class AuthService:
    """认证服务"""
    
    @staticmethod
    def register(db: Session, user_data: UserCreate) -> User:
        """用户注册"""
        # 检查用户名是否存在
        existing_user = db.query(User).filter(
            or_(
                User.username == user_data.username,
                User.email == user_data.email if user_data.email else False,
                User.phone == user_data.phone if user_data.phone else False
            )
        ).first()
        
        if existing_user:
            raise ValueError("用户名、邮箱或手机号已存在")
        
        # 创建用户
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            phone=user_data.phone,
            password_hash=hashed_password,
            role=user_data.role
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"用户注册成功：{db_user.username}")
        return db_user
    
    @staticmethod
    def login(db: Session, username: str, password: str, ip_address: str = None) -> tuple:
        """用户登录"""
        # 查找用户（支持用户名/邮箱/手机号登录）
        user = db.query(User).filter(
            or_(
                User.username == username,
                User.email == username,
                User.phone == username
            )
        ).first()
        
        if not user:
            raise ValueError("用户不存在")
        
        if not user.status:
            raise ValueError("用户已被禁用")
        
        if not verify_password(password, user.password_hash):
            raise ValueError("密码错误")
        
        # 更新登录信息
        user.last_login_at = datetime.utcnow()
        user.last_login_ip = ip_address
        db.commit()
        
        # 生成 Token
        access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        logger.info(f"用户登录成功：{user.username}")
        
        return user, access_token, refresh_token
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """根据 ID 获取用户"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        return user
    
    @staticmethod
    def refresh_token(db: Session, refresh_token: str) -> tuple:
        """刷新 Token"""
        from app.utils.security import decode_token
        
        payload = decode_token(refresh_token)
        if not payload:
            raise ValueError("无效的刷新令牌")
        
        user_id = int(payload.get("sub"))
        user = AuthService.get_user_by_id(db, user_id)
        
        # 生成新 Token
        new_access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return new_access_token, new_refresh_token
