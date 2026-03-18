# 评论 Schema
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Platform(str, Enum):
    """平台类型"""
    DIANPING = "dianping"
    MEITUAN = "meituan"
    ELEME = "eleme"

class Sentiment(str, Enum):
    """情感分类"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

# 评论创建
class ReviewCreate(BaseModel):
    merchant_id: int
    review_id: str
    platform: Platform = Platform.DIANPING
    user_name: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)
    content: str
    images: Optional[List[str]] = None
    review_time: Optional[datetime] = None

# 评论筛选
class ReviewFilter(BaseModel):
    merchant_id: Optional[int] = None
    platform: Optional[Platform] = None
    sentiment: Optional[Sentiment] = None
    rating: Optional[int] = None
    is_replied: Optional[bool] = None
    is_read: Optional[bool] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    page: int = 1
    size: int = 20

# 评论响应
class ReviewResponse(BaseModel):
    id: int
    merchant_id: int
    review_id: str
    platform: Platform
    user_name: Optional[str]
    rating: int
    content: str
    images: Optional[List[str]]
    review_time: Optional[datetime]
    sentiment: Sentiment
    is_replied: bool
    reply_content: Optional[str]
    reply_time: Optional[datetime]
    is_read: bool
    is_flagged: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# 评论统计
class ReviewStats(BaseModel):
    total: int
    positive_count: int
    neutral_count: int
    negative_count: int
    replied_count: int
    unreplied_count: int
    avg_rating: float
