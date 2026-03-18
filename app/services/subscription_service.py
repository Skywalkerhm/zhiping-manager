# 订阅服务
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
from app.models.subscription import SubscriptionOrder, PlanType, PaymentStatus
from app.models.merchant import Merchant, SubscriptionPlan
from app.utils.logger import logger

class SubscriptionService:
    """订阅管理服务"""
    
    # 订阅价格
    PRICING = {
        PlanType.FREE: 0,
        PlanType.PRO: 299,
        PlanType.PREMIUM: 999,
        PlanType.ENTERPRISE: 2999
    }
    
    # 订阅周期（月）
    CYCLES = {
        PlanType.FREE: 1,
        PlanType.PRO: 1,
        PlanType.PREMIUM: 3,
        PlanType.ENTERPRISE: 12
    }
    
    @staticmethod
    def create_order(db: Session, merchant_id: int, plan_type: PlanType, payment_method: str = "wechat") -> SubscriptionOrder:
        """创建订阅订单"""
        # 生成订单号
        order_no = f"SUB{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8].upper()}"
        
        amount = SubscriptionService.PRICING.get(plan_type, 0)
        
        order = SubscriptionOrder(
            merchant_id=merchant_id,
            order_no=order_no,
            plan_type=plan_type,
            amount=amount,
            payment_method=payment_method,
            payment_status=PaymentStatus.PENDING
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        logger.info(f"创建订阅订单：{order_no}, 金额：{amount}")
        return order
    
    @staticmethod
    def get_order_by_no(db: Session, order_no: str) -> Optional[SubscriptionOrder]:
        """根据订单号获取订单"""
        return db.query(SubscriptionOrder).filter(
            SubscriptionOrder.order_no == order_no
        ).first()
    
    @staticmethod
    def process_payment(
        db: Session,
        order_no: str,
        transaction_id: str,
        payment_time: datetime = None
    ) -> bool:
        """处理支付成功回调"""
        if not payment_time:
            payment_time = datetime.utcnow()
        
        order = SubscriptionService.get_order_by_no(db, order_no)
        if not order:
            logger.error(f"订单不存在：{order_no}")
            return False
        
        # 更新订单状态
        order.payment_status = PaymentStatus.PAID
        order.payment_time = payment_time
        
        # 计算订阅周期
        start_date = payment_time
        months = SubscriptionService.CYCLES.get(order.plan_type, 1)
        end_date = start_date + timedelta(days=30 * months)
        
        order.start_date = start_date
        order.end_date = end_date
        
        # 更新商家订阅状态
        merchant = db.query(Merchant).filter(Merchant.id == order.merchant_id).first()
        if merchant:
            merchant.subscription_plan = SubscriptionPlan(order.plan_type.value)
            merchant.subscription_start = start_date
            merchant.subscription_expire = end_date
        
        db.commit()
        
        logger.info(f"支付成功：{order_no}, 订阅至：{end_date}")
        return True
    
    @staticmethod
    def get_merchant_subscription(db: Session, merchant_id: int) -> Dict[str, Any]:
        """获取商家订阅信息"""
        merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
        if not merchant:
            return {}
        
        # 获取当前订单
        current_order = db.query(SubscriptionOrder).filter(
            SubscriptionOrder.merchant_id == merchant_id,
            SubscriptionOrder.payment_status == PaymentStatus.PAID,
            SubscriptionOrder.end_date >= datetime.utcnow()
        ).order_by(SubscriptionOrder.end_date.desc()).first()
        
        return {
            "plan_type": merchant.subscription_plan.value if merchant.subscription_plan else "free",
            "subscription_start": merchant.subscription_start,
            "subscription_expire": merchant.subscription_expire,
            "is_active": merchant.subscription_expire and merchant.subscription_expire > datetime.utcnow(),
            "days_remaining": (merchant.subscription_expire - datetime.utcnow()).days if merchant.subscription_expire else 0,
            "order_no": current_order.order_no if current_order else None
        }
    
    @staticmethod
    def get_orders(db: Session, merchant_id: int, page: int = 1, size: int = 20) -> Dict[str, Any]:
        """获取商家订单列表"""
        query = db.query(SubscriptionOrder).filter(
            SubscriptionOrder.merchant_id == merchant_id
        ).order_by(SubscriptionOrder.created_at.desc())
        
        total = query.count()
        offset = (page - 1) * size
        orders = query.offset(offset).limit(size).all()
        
        return {
            "total": total,
            "orders": orders,
            "page": page,
            "size": size
        }
