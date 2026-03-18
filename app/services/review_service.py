# 评论服务
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.review import Review, Platform, Sentiment
from app.models.merchant import Merchant
from app.schemas.review import ReviewCreate, ReviewFilter, ReviewResponse
from app.utils.logger import logger
from datetime import datetime

class ReviewService:
    """评论管理服务"""
    
    @staticmethod
    def create_review(db: Session, review_data: ReviewCreate) -> Review:
        """创建评论"""
        db_review = Review(
            merchant_id=review_data.merchant_id,
            review_id=review_data.review_id,
            platform=review_data.platform,
            user_name=review_data.user_name,
            rating=review_data.rating,
            content=review_data.content,
            images=review_data.images,
            review_time=review_data.review_time,
            sentiment=Sentiment.NEUTRAL,  # 初始为中性，后续 AI 分析
            is_replied=False,
            is_read=False
        )
        
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
        
        # 更新商家统计
        ReviewService.update_merchant_stats(db, review_data.merchant_id)
        
        logger.info(f"创建评论：{db_review.review_id}")
        return db_review
    
    @staticmethod
    def get_reviews(
        db: Session,
        filter_data: ReviewFilter
    ) -> Dict[str, Any]:
        """
        获取评论列表（分页）
        
        Returns:
            {
                "total": int,
                "items": List[Review],
                "page": int,
                "size": int
            }
        """
        query = db.query(Review)
        
        # 应用筛选条件
        if filter_data.merchant_id:
            query = query.filter(Review.merchant_id == filter_data.merchant_id)
        if filter_data.platform:
            query = query.filter(Review.platform == filter_data.platform.value)
        if filter_data.sentiment:
            query = query.filter(Review.sentiment == filter_data.sentiment.value)
        if filter_data.rating:
            query = query.filter(Review.rating == filter_data.rating)
        if filter_data.is_replied is not None:
            query = query.filter(Review.is_replied == filter_data.is_replied)
        if filter_data.is_read is not None:
            query = query.filter(Review.is_read == filter_data.is_read)
        if filter_data.start_time:
            query = query.filter(Review.review_time >= filter_data.start_time)
        if filter_data.end_time:
            query = query.filter(Review.review_time <= filter_data.end_time)
        
        # 总数
        total = query.count()
        
        # 分页
        offset = (filter_data.page - 1) * filter_data.size
        items = query.order_by(Review.review_time.desc()).offset(offset).limit(filter_data.size).all()
        
        return {
            "total": total,
            "items": items,
            "page": filter_data.page,
            "size": filter_data.size
        }
    
    @staticmethod
    def get_review_by_id(db: Session, review_id: int) -> Optional[Review]:
        """根据 ID 获取评论"""
        return db.query(Review).filter(Review.id == review_id).first()
    
    @staticmethod
    def get_review_by_platform_id(
        db: Session,
        platform_id: str,
        platform: Platform = Platform.DIANPING
    ) -> Optional[Review]:
        """根据平台评论 ID 获取"""
        return db.query(Review).filter(
            and_(
                Review.review_id == platform_id,
                Review.platform == platform.value
            )
        ).first()
    
    @staticmethod
    def mark_as_read(db: Session, review_id: int) -> Review:
        """标记为已读"""
        review = ReviewService.get_review_by_id(db, review_id)
        if not review:
            raise ValueError("评论不存在")
        
        review.is_read = True
        db.commit()
        db.refresh(review)
        
        return review
    
    @staticmethod
    def mark_as_replied(
        db: Session,
        review_id: int,
        reply_content: str,
        replied_by: int = None
    ) -> Review:
        """标记为已回复"""
        review = ReviewService.get_review_by_id(db, review_id)
        if not review:
            raise ValueError("评论不存在")
        
        review.is_replied = True
        review.reply_content = reply_content
        review.reply_time = datetime.utcnow()
        review.replied_by = replied_by
        
        db.commit()
        db.refresh(review)
        
        # 更新商家统计
        ReviewService.update_merchant_stats(db, review.merchant_id)
        
        return review
    
    @staticmethod
    def flag_review(
        db: Session,
        review_id: int,
        flag_reason: str
    ) -> Review:
        """标记评论（需重点关注）"""
        review = ReviewService.get_review_by_id(db, review_id)
        if not review:
            raise ValueError("评论不存在")
        
        review.is_flagged = True
        review.flag_reason = flag_reason
        
        db.commit()
        db.refresh(review)
        
        return review
    
    @staticmethod
    def update_merchant_stats(db: Session, merchant_id: int):
        """更新商家统计信息"""
        merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
        if not merchant:
            return
        
        # 统计评论
        total = db.query(Review).filter(Review.merchant_id == merchant_id).count()
        avg_rating = db.query(Review).filter(
            Review.merchant_id == merchant_id
        ).with_entities(
            db.query(Review).filter(Review.merchant_id == merchant_id)
        ).scalar()
        
        # 计算平均评分
        from sqlalchemy import func
        avg_result = db.query(func.avg(Review.rating)).filter(
            Review.merchant_id == merchant_id
        ).scalar()
        
        merchant.total_reviews = total
        merchant.avg_rating = avg_result or 0.0
        
        db.commit()
        
        logger.info(f"更新商家 {merchant_id} 统计：总评论={total}, 平均评分={avg_result}")
    
    @staticmethod
    def get_stats(db: Session, merchant_id: int) -> Dict[str, Any]:
        """获取评论统计"""
        from sqlalchemy import func
        
        # 总数
        total = db.query(Review).filter(Review.merchant_id == merchant_id).count()
        
        # 情感分布
        positive_count = db.query(Review).filter(
            and_(
                Review.merchant_id == merchant_id,
                Review.sentiment == Sentiment.POSITIVE
            )
        ).count()
        
        neutral_count = db.query(Review).filter(
            and_(
                Review.merchant_id == merchant_id,
                Review.sentiment == Sentiment.NEUTRAL
            )
        ).count()
        
        negative_count = db.query(Review).filter(
            and_(
                Review.merchant_id == merchant_id,
                Review.sentiment == Sentiment.NEGATIVE
            )
        ).count()
        
        # 回复情况
        replied_count = db.query(Review).filter(
            and_(
                Review.merchant_id == merchant_id,
                Review.is_replied == True
            )
        ).count()
        
        unreplied_count = total - replied_count
        
        # 平均评分
        avg_rating = db.query(func.avg(Review.rating)).filter(
            Review.merchant_id == merchant_id
        ).scalar() or 0.0
        
        return {
            "total": total,
            "positive_count": positive_count,
            "neutral_count": neutral_count,
            "negative_count": negative_count,
            "replied_count": replied_count,
            "unreplied_count": unreplied_count,
            "avg_rating": float(avg_rating)
        }
    
    @staticmethod
    def batch_sync_reviews(
        db: Session,
        merchant_id: int,
        platform: Platform,
        reviews_data: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        批量同步评论
        
        Returns:
            {
                "created": int,  # 新增数量
                "updated": int,  # 更新数量
                "skipped": int   # 跳过数量
            }
        """
        created = 0
        updated = 0
        skipped = 0
        
        for review_data in reviews_data:
            # 检查是否已存在
            existing = ReviewService.get_review_by_platform_id(
                db,
                review_data['review_id'],
                platform
            )
            
            if existing:
                # 更新现有评论
                if review_data.get('content'):
                    existing.content = review_data['content']
                if review_data.get('rating'):
                    existing.rating = review_data['rating']
                if review_data.get('images'):
                    existing.images = review_data['images']
                if review_data.get('review_time'):
                    existing.review_time = review_data['review_time']
                
                updated += 1
            else:
                # 创建新评论
                try:
                    review_create = ReviewCreate(
                        merchant_id=merchant_id,
                        review_id=review_data['review_id'],
                        platform=platform,
                        user_name=review_data.get('user_name'),
                        rating=review_data['rating'],
                        content=review_data['content'],
                        images=review_data.get('images'),
                        review_time=review_data.get('review_time')
                    )
                    ReviewService.create_review(db, review_create)
                    created += 1
                except Exception as e:
                    logger.error(f"创建评论失败：{str(e)}")
                    skipped += 1
        
        # 更新商家统计
        ReviewService.update_merchant_stats(db, merchant_id)
        
        logger.info(f"批量同步评论：新增={created}, 更新={updated}, 跳过={skipped}")
        
        return {
            "created": created,
            "updated": updated,
            "skipped": skipped
        }
