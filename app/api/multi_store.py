# 多店管理 API 路由
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.multi_store_service import MultiStoreService
from app.utils.logger import logger

router = APIRouter()

@router.get("/stores", summary="获取我的店铺列表")
async def get_my_stores(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的所有店铺
    """
    stores = MultiStoreService.get_user_stores(db, current_user.id)
    
    return {
        "code": 200,
        "data": stores,
        "message": "success"
    }

@router.post("/stores", summary="创建新店铺")
async def create_store(
    shop_name: str,
    shop_type: str,
    address: str = None,
    city: str = None,
    district: str = None,
    phone: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新店铺
    
    - **shop_name**: 店铺名称
    - **shop_type**: 店铺类型
    - **address**: 地址
    - **city**: 城市
    - **district**: 区域
    - **phone**: 联系电话
    """
    try:
        store = MultiStoreService.create_store(
            db,
            current_user.id,
            shop_name,
            shop_type,
            address,
            city,
            district,
            phone
        )
        
        return {
            "code": 200,
            "data": store,
            "message": "店铺创建成功"
        }
    except Exception as e:
        logger.error(f"创建店铺失败：{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建店铺失败"
        )

@router.put("/stores/{store_id}", summary="更新店铺信息")
async def update_store(
    store_id: int,
    shop_name: str = None,
    shop_type: str = None,
    address: str = None,
    city: str = None,
    district: str = None,
    phone: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新店铺信息
    """
    update_data = {k: v for k, v in {
        "shop_name": shop_name,
        "shop_type": shop_type,
        "address": address,
        "city": city,
        "district": district,
        "phone": phone
    }.items() if v is not None}
    
    store = MultiStoreService.update_store(db, store_id, current_user.id, **update_data)
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="店铺不存在或无权限"
        )
    
    return {
        "code": 200,
        "data": store,
        "message": "店铺更新成功"
    }

@router.delete("/stores/{store_id}", summary="删除店铺")
async def delete_store(
    store_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除店铺（软删除）
    """
    success = MultiStoreService.delete_store(db, store_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="店铺不存在或无权限"
        )
    
    return {
        "code": 200,
        "message": "店铺删除成功"
    }

@router.get("/stores/stats", summary="获取店铺统计")
async def get_stores_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取所有店铺的统计数据
    """
    stats = MultiStoreService.get_store_stats(db, current_user.id)
    
    return {
        "code": 200,
        "data": stats,
        "message": "success"
    }

@router.post("/stores/{store_id}/switch", summary="切换店铺")
async def switch_store(
    store_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    切换当前操作的店铺
    """
    store = MultiStoreService.switch_store(db, store_id, current_user.id)
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="店铺不存在或无权限"
        )
    
    return {
        "code": 200,
        "data": {
            "current_store_id": store.id,
            "shop_name": store.shop_name
        },
        "message": "店铺切换成功"
    }
