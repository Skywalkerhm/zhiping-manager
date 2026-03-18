# 商家模型
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, DECIMAL
from sqlalchemy.sql import func
from app.database import Base
import enum

class SubscriptionPlan(str, enum.Enum):
    """订阅计划"""
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class Merchant(Base):
    """商家模型"""
    __tablename__ = "merchants"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    shop_name = Column(String(100), nullable=False)
    shop_type = Column(String(50))
    shop_category = Column(String(100))
    address = Column(String(255))
    city = Column(String(50))
    district = Column(String(50))
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    phone = Column(String(20))
    dianping_shop_id = Column(String(50), index=True)
    meituan_shop_id = Column(String(50), index=True)
    eleme_shop_id = Column(String(50))
    authorization_token = Column(String(1024))
    authorization_expire = Column(DateTime)
    subscription_plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.FREE)
    subscription_start = Column(DateTime)
    subscription_expire = Column(DateTime)
    total_reviews = Column(Integer, default=0)
    avg_rating = Column(DECIMAL(3, 2), default=0.00)
    status = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
