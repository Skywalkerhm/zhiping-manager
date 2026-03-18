# 订阅 API 路由
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.subscription import SubscriptionOrderCreate, SubscriptionOrderResponse, PaymentRequest
from app.services.subscription_service import SubscriptionService
from app.api.deps import get_current_user
from app.models.user import User
from app.utils.logger import logger

router = APIRouter()

@router.post("/orders", response_model=SubscriptionOrderResponse, summary="创建订阅订单")
async def create_subscription_order(
    order_data: SubscriptionOrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建订阅订单
    
    - **merchant_id**: 商家 ID
    - **plan_type**: 计划类型（free/pro/premium/enterprise）
    - **payment_method**: 支付方式（wechat/alipay）
    """
    try:
        order = SubscriptionService.create_order(
            db,
            order_data.merchant_id,
            order_data.plan_type,
            order_data.payment_method
        )
        
        return order
    except Exception as e:
        logger.error(f"创建订单失败：{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建订单失败"
        )

@router.get("/orders/{order_no}", response_model=SubscriptionOrderResponse, summary="获取订单详情")
async def get_order(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取订单详情
    
    - **order_no**: 订单号
    """
    order = SubscriptionService.get_order_by_no(db, order_no)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    return order

@router.post("/payment", summary="发起支付")
async def initiate_payment(
    payment_data: PaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    发起支付
    
    - **order_no**: 订单号
    - **payment_method**: 支付方式
    """
    order = SubscriptionService.get_order_by_no(db, payment_data.order_no)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    # TODO: 调用微信支付/支付宝 API 生成支付链接
    # 这里返回模拟的支付链接
    payment_url = f"https://pay.example.com/pay?order_no={order.order_no}&amount={order.amount}"
    
    return {
        "code": 200,
        "data": {
            "order_no": order.order_no,
            "amount": float(order.amount),
            "payment_url": payment_url,
            "qr_code": f"https://api.example.com/qr?order_no={order.order_no}"
        },
        "message": "请扫描二维码完成支付"
    }

@router.post("/payment/callback", summary="支付回调")
async def payment_callback(
    order_no: str,
    transaction_id: str,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    支付成功回调
    
    - **order_no**: 订单号
    - **transaction_id**: 交易流水号
    - **status**: 支付状态
    """
    if status != "SUCCESS":
        return {"message": "支付失败"}
    
    success = SubscriptionService.process_payment(db, order_no, transaction_id)
    
    if success:
        return {"message": "支付成功，订阅已激活"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="处理支付失败"
        )

@router.get("/subscription", summary="获取订阅信息")
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的订阅信息
    """
    # TODO: 获取用户关联的商家 ID
    merchant_id = 1  # 简化处理
    
    subscription = SubscriptionService.get_merchant_subscription(db, merchant_id)
    
    return {
        "code": 200,
        "data": subscription,
        "message": "success"
    }

@router.get("/orders", summary="获取订单列表")
async def get_orders(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取订单列表
    
    - **page**: 页码
    - **size**: 每页数量
    """
    # TODO: 获取用户关联的商家 ID
    merchant_id = 1  # 简化处理
    
    result = SubscriptionService.get_orders(db, merchant_id, page, size)
    
    return {
        "code": 200,
        "data": {
            "total": result["total"],
            "orders": result["orders"],
            "page": result["page"],
            "size": result["size"]
        },
        "message": "success"
    }
