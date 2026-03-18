# 评论模型
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey, DECIMAL, JSON
from sqlalchemy.sql import func
from app.database import Base
import enum

class Platform(str, enum.Enum):
    """平台类型"""
    DIANPING = "dianping"
    MEITUAN = "meituan"
    ELEME = "eleme"

class Sentiment(str, enum.Enum):
    """情感分类"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class Review(Base):
    """评论模型"""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)
    review_id = Column(String(50), unique=True, nullable=False, index=True)
    platform = Column(Enum(Platform), default=Platform.DIANPING, index=True)
    user_name = Column(String(50))
    user_avatar = Column(String(255))
    rating = Column(Integer, nullable=False, index=True)
    content = Column(Text, nullable=False)
    images = Column(JSON)
    review_time = Column(DateTime, index=True)
    sentiment = Column(Enum(Sentiment), default=Sentiment.NEUTRAL, index=True)
    sentiment_score = Column(DECIMAL(5, 4))
    topics = Column(JSON)
    is_replied = Column(Boolean, default=False, index=True)
    reply_content = Column(Text)
    reply_time = Column(DateTime)
    replied_by = Column(Integer)
    is_read = Column(Boolean, default=False, index=True)
    is_flagged = Column(Boolean, default=False)
    flag_reason = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
