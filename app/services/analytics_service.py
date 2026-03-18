# 数据分析服务
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta
from app.models.review import Review, Sentiment
from app.models.merchant import Merchant
from app.utils.logger import logger
from collections import defaultdict
import jieba
import re

class AnalyticsService:
    """数据分析服务"""
    
    @staticmethod
    def get_rating_trend(
        db: Session,
        merchant_id: int,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        获取评分趋势
        
        Args:
            db: 数据库会话
            merchant_id: 商家 ID
            days: 天数
        
        Returns:
            [
                {"date": "2026-03-01", "avg_rating": 4.5, "count": 10},
                ...
            ]
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 按日期分组统计
        results = db.query(
            func.date(Review.review_time).label('date'),
            func.avg(Review.rating).label('avg_rating'),
            func.count(Review.id).label('count')
        ).filter(
            and_(
                Review.merchant_id == merchant_id,
                Review.review_time >= start_date
            )
        ).group_by(
            func.date(Review.review_time)
        ).order_by(
            func.date(Review.review_time)
        ).all()
        
        return [
            {
                "date": str(r.date),
                "avg_rating": float(r.avg_rating) if r.avg_rating else 0,
                "count": r.count
            }
            for r in results
        ]
    
    @staticmethod
    def get_review_stats(
        db: Session,
        merchant_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取评论统计
        
        Returns:
            {
                "total": 100,
                "positive": 60,
                "neutral": 30,
                "negative": 10,
                "replied": 80,
                "avg_rating": 4.5
            }
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 总数
        total = db.query(Review).filter(
            and_(
                Review.merchant_id == merchant_id,
                Review.review_time >= start_date
            )
        ).count()
        
        # 情感分布
        positive = db.query(Review).filter(
            and_(
                Review.merchant_id == merchant_id,
                Review.sentiment == Sentiment.POSITIVE,
                Review.review_time >= start_date
            )
        ).count()
        
        neutral = db.query(Review).filter(
            and_(
                Review.merchant_id == merchant_id,
                Review.sentiment == Sentiment.NEUTRAL,
                Review.review_time >= start_date
            )
        ).count()
        
        negative = db.query(Review).filter(
            and_(
                Review.merchant_id == merchant_id,
                Review.sentiment == Sentiment.NEGATIVE,
                Review.review_time >= start_date
            )
        ).count()
        
        # 已回复数
        replied = db.query(Review).filter(
            and_(
                Review.merchant_id == merchant_id,
                Review.is_replied == True,
                Review.review_time >= start_date
            )
        ).count()
        
        # 平均评分
        avg_rating = db.query(func.avg(Review.rating)).filter(
            and_(
                Review.merchant_id == merchant_id,
                Review.review_time >= start_date
            )
        ).scalar() or 0.0
        
        return {
            "total": total,
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
            "replied": replied,
            "avg_rating": float(avg_rating)
        }
    
    @staticmethod
    def get_keywords(
        db: Session,
        merchant_id: int,
        sentiment: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        获取关键词分析
        
        Args:
            db: 数据库会话
            merchant_id: 商家 ID
            sentiment: 情感分类（可选）
            limit: 返回数量
        
        Returns:
            [
                {"keyword": "好吃", "count": 50, "sentiment": "positive"},
                ...
            ]
        """
        # 获取评论文本
        query = db.query(Review.content).filter(
            Review.merchant_id == merchant_id
        )
        
        if sentiment:
            query = query.filter(Review.sentiment == Sentiment(sentiment))
        
        reviews = query.all()
        
        # 分词统计
        word_count = defaultdict(int)
        
        # 停用词表（简化版）
        stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
            '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
            '你', '会', '着', '没有', '看', '好', '自己', '这'
        }
        
        for review in reviews:
            if review.content:
                # 使用 jieba 分词
                words = jieba.cut(review.content)
                for word in words:
                    word = word.strip().lower()
                    if word and word not in stop_words and len(word) > 1:
                        word_count[word] += 1
        
        # 排序并返回 top N
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return [
            {"keyword": word, "count": count}
            for word, count in sorted_words
        ]
    
    @staticmethod
    def get_topic_distribution(
        db: Session,
        merchant_id: int,
        days: int = 30
    ) -> Dict[str, int]:
        """
        获取主题分布
        
        Returns:
            {
                "菜品": 50,
                "服务": 30,
                "环境": 20
            }
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        reviews = db.query(Review.topics).filter(
            and_(
                Review.merchant_id == merchant_id,
                Review.review_time >= start_date
            )
        ).all()
        
        topic_count = defaultdict(int)
        
        for review in reviews:
            if review.topics:
                for topic in review.topics:
                    topic_count[topic] += 1
        
        return dict(topic_count)
    
    @staticmethod
    def get_unreplied_reviews(
        db: Session,
        merchant_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取未回复的评论（优先差评）
        
        Returns:
            [
                {
                    "id": 1,
                    "rating": 2,
                    "content": "...",
                    "review_time": "2026-03-17"
                },
                ...
            ]
        """
        reviews = db.query(Review).filter(
            and_(
                Review.merchant_id == merchant_id,
                Review.is_replied == False
            )
        ).order_by(
            Review.rating.asc(),  # 差评优先
            Review.review_time.desc()
        ).limit(limit).all()
        
        return [
            {
                "id": r.id,
                "rating": r.rating,
                "content": r.content[:100] + "..." if len(r.content) > 100 else r.content,
                "review_time": str(r.review_time),
                "sentiment": r.sentiment.value
            }
            for r in reviews
        ]
    
    @staticmethod
    def get_competitor_analysis(
        db: Session,
        merchant_id: int,
        city: str = None,
        district: str = None,
        shop_type: str = None
    ) -> Dict[str, Any]:
        """
        竞品分析（简化版）
        
        Returns:
            {
                "my_rating": 4.5,
                "avg_rating": 4.2,
                "rank": 5,
                "total_competitors": 20
            }
        """
        # 获取当前商家信息
        merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
        if not merchant:
            return {}
        
        # 查询同区域同类型商家
        query = db.query(Merchant).filter(
            Merchant.status == True
        )
        
        if city:
            query = query.filter(Merchant.city == city)
        if district:
            query = query.filter(Merchant.district == district)
        if shop_type:
            query = query.filter(Merchant.shop_type == shop_type)
        
        competitors = query.all()
        
        if not competitors:
            return {}
        
        # 计算平均评分
        ratings = [m.avg_rating for m in competitors if m.avg_rating > 0]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # 排名
        my_rating = float(merchant.avg_rating)
        rank = sum(1 for r in ratings if r > my_rating) + 1
        
        return {
            "my_rating": my_rating,
            "avg_rating": avg_rating,
            "rank": rank,
            "total_competitors": len(competitors),
            "better_than_avg": my_rating > avg_rating
        }
    
    @staticmethod
    def generate_daily_report(
        db: Session,
        merchant_id: int,
        date: datetime = None
    ) -> Dict[str, Any]:
        """
        生成每日报告
        
        Returns:
            {
                "date": "2026-03-17",
                "new_reviews": 5,
                "new_positive": 3,
                "new_negative": 1,
                "replied": 4,
                "avg_rating": 4.6,
                "keywords": [...],
                "action_items": [...]
            }
        """
        if not date:
            date = datetime.utcnow().date()
        
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        
        # 当日评论
        new_reviews = db.query(Review).filter(
            and_(
                Review.merchant_id == merchant_id,
                Review.review_time >= start_of_day,
                Review.review_time <= end_of_day
            )
        ).all()
        
        new_count = len(new_reviews)
        new_positive = sum(1 for r in new_reviews if r.sentiment == Sentiment.POSITIVE)
        new_negative = sum(1 for r in new_reviews if r.sentiment == Sentiment.NEGATIVE)
        replied_count = sum(1 for r in new_reviews if r.is_replied)
        
        # 当日平均评分
        avg_rating = sum(r.rating for r in new_reviews) / new_count if new_count > 0 else 0
        
        # 生成建议
        action_items = []
        if new_negative > 0:
            action_items.append(f"有{new_negative}条差评需要及时处理")
        
        unreplied = db.query(Review).filter(
            and_(
                Review.merchant_id == merchant_id,
                Review.is_replied == False,
                Review.review_time < start_of_day
            )
        ).count()
        
        if unreplied > 0:
            action_items.append(f"还有{unreplied}条历史评论未回复")
        
        if avg_rating < 4.0:
            action_items.append("今日评分较低，需关注服务质量")
        
        return {
            "date": str(date),
            "new_reviews": new_count,
            "new_positive": new_positive,
            "new_negative": new_negative,
            "replied": replied_count,
            "avg_rating": round(avg_rating, 2),
            "action_items": action_items
        }
