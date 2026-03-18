# 订阅订单模型
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey, ENUM
from sqlalchemy.sql import func
from app.database import Base
import enum

class PlanType(str, enum.Enum):
    """订阅计划类型"""
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class PaymentStatus(str, enum.Enum):
    """支付状态"""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class SubscriptionOrder(Base):
    """订阅订单表"""
    __tablename__ = "subscription_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)
    order_no = Column(String(50), unique=True, nullable=False)
    plan_type = Column(ENUM(PlanType), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(10), default="CNY")
    payment_method = Column(String(50))
    payment_status = Column(ENUM(PaymentStatus), default=PaymentStatus.PENDING)
    payment_time = Column(DateTime)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
