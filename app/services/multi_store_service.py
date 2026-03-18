# 多店管理服务
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.merchant import Merchant
from app.models.user import User
from app.utils.logger import logger

class MultiStoreService:
    """多店管理服务"""
    
    @staticmethod
    def get_user_stores(db: Session, user_id: int) -> List[Merchant]:
        """获取用户所有店铺"""
        stores = db.query(Merchant).filter(
            Merchant.user_id == user_id,
            Merchant.status == True
        ).all()
        
        return stores
    
    @staticmethod
    def create_store(
        db: Session,
        user_id: int,
        shop_name: str,
        shop_type: str,
        address: str = None,
        city: str = None,
        district: str = None,
        phone: str = None
    ) -> Merchant:
        """创建新店铺"""
        store = Merchant(
            user_id=user_id,
            shop_name=shop_name,
            shop_type=shop_type,
            address=address,
            city=city,
            district=district,
            phone=phone,
            status=True
        )
        
        db.add(store)
        db.commit()
        db.refresh(store)
        
        logger.info(f"创建新店铺：{store.shop_name}")
        return store
    
    @staticmethod
    def update_store(
        db: Session,
        store_id: int,
        user_id: int,
        **kwargs
    ) -> Optional[Merchant]:
        """更新店铺信息"""
        store = db.query(Merchant).filter(
            Merchant.id == store_id,
            Merchant.user_id == user_id
        ).first()
        
        if not store:
            return None
        
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(store, key) and value is not None:
                setattr(store, key, value)
        
        db.commit()
        db.refresh(store)
        
        logger.info(f"更新店铺信息：{store.shop_name}")
        return store
    
    @staticmethod
    def delete_store(db: Session, store_id: int, user_id: int) -> bool:
        """删除店铺（软删除）"""
        store = db.query(Merchant).filter(
            Merchant.id == store_id,
            Merchant.user_id == user_id
        ).first()
        
        if not store:
            return False
        
        store.status = False
        db.commit()
        
        logger.info(f"删除店铺：{store.shop_name}")
        return True
    
    @staticmethod
    def get_store_stats(db: Session, user_id: int) -> Dict[str, Any]:
        """获取店铺统计"""
        stores = MultiStoreService.get_user_stores(db, user_id)
        
        total_stores = len(stores)
        total_reviews = sum(store.total_reviews or 0 for store in stores)
        avg_rating = sum(store.avg_rating or 0 for store in stores) / total_stores if total_stores > 0 else 0
        
        return {
            "total_stores": total_stores,
            "total_reviews": total_reviews,
            "avg_rating": round(avg_rating, 2),
            "stores": [
                {
                    "id": store.id,
                    "shop_name": store.shop_name,
                    "shop_type": store.shop_type,
                    "total_reviews": store.total_reviews,
                    "avg_rating": float(store.avg_rating) if store.avg_rating else 0
                }
                for store in stores
            ]
        }
    
    @staticmethod
    def switch_store(db: Session, store_id: int, user_id: int) -> Optional[Merchant]:
        """切换当前店铺"""
        store = db.query(Merchant).filter(
            Merchant.id == store_id,
            Merchant.user_id == user_id,
            Merchant.status == True
        ).first()
        
        return store
