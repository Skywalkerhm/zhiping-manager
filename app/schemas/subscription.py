# 订阅 Schema
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class SubscriptionOrderCreate(BaseModel):
    merchant_id: int
    plan_type: PlanType
    payment_method: str = "wechat"

class SubscriptionOrderResponse(BaseModel):
    id: int
    merchant_id: int
    order_no: str
    plan_type: PlanType
    amount: float
    currency: str
    payment_status: PaymentStatus
    payment_time: Optional[datetime]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaymentRequest(BaseModel):
    order_no: str
    payment_method: str = "wechat"

class PaymentCallback(BaseModel):
    order_no: str
    transaction_id: str
    status: str
    payment_time: datetime
