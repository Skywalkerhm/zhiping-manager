# 评论管理 API 路由
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.schemas.review import ReviewFilter, ReviewResponse, ReviewStats
from app.services.review_service import ReviewService
from app.api.deps import get_current_user
from app.models.user import User
from app.utils.logger import logger

router = APIRouter()

@router.get("", response_model=Dict, summary="获取评论列表")
async def get_reviews(
    merchant_id: Optional[int] = Query(None, description="商家 ID"),
    platform: Optional[str] = Query(None, description="平台：dianping/meituan/eleme"),
    sentiment: Optional[str] = Query(None, description="情感：positive/neutral/negative"),
    rating: Optional[int] = Query(None, description="评分 1-5"),
    is_replied: Optional[bool] = Query(None, description="是否已回复"),
    is_read: Optional[bool] = Query(None, description="是否已读"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取评论列表（支持多条件筛选和分页）
    
    - **merchant_id**: 商家 ID（必填）
    - **platform**: 平台类型
    - **sentiment**: 情感分类
    - **rating**: 评分
    - **is_replied**: 是否已回复
    - **is_read**: 是否已读
    - **start_time**: 开始时间
    - **end_time**: 结束时间
    - **page**: 页码
    - **size**: 每页数量（1-100）
    """
    try:
        filter_data = ReviewFilter(
            merchant_id=merchant_id,
            platform=platform,
            sentiment=sentiment,
            rating=rating,
            is_replied=is_replied,
            is_read=is_read,
            start_time=start_time,
            end_time=end_time,
            page=page,
            size=size
        )
        
        result = ReviewService.get_reviews(db, filter_data)
        
        # 转换为响应格式
        items = [
            ReviewResponse(
                id=item.id,
                merchant_id=item.merchant_id,
                review_id=item.review_id,
                platform=item.platform,
                user_name=item.user_name,
                rating=item.rating,
                content=item.content,
                images=item.images,
                review_time=item.review_time,
                sentiment=item.sentiment,
                is_replied=item.is_replied,
                reply_content=item.reply_content,
                reply_time=item.reply_time,
                is_read=item.is_read,
                is_flagged=item.is_flagged,
                created_at=item.created_at
            )
            for item in result['items']
        ]
        
        return {
            "total": result['total'],
            "items": items,
            "page": result['page'],
            "size": result['size'],
            "total_pages": (result['total'] + result['size'] - 1) // result['size']
        }
    
    except Exception as e:
        logger.error(f"获取评论列表失败：{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取评论列表失败"
        )

@router.get("/{review_id}", response_model=ReviewResponse, summary="获取评论详情")
async def get_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取单条评论详情
    
    - **review_id**: 评论 ID
    """
    review = ReviewService.get_review_by_id(db, review_id)
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    return ReviewResponse(
        id=review.id,
        merchant_id=review.merchant_id,
        review_id=review.review_id,
        platform=review.platform,
        user_name=review.user_name,
        rating=review.rating,
        content=review.content,
        images=review.images,
        review_time=review.review_time,
        sentiment=review.sentiment,
        is_replied=review.is_replied,
        reply_content=review.reply_content,
        reply_time=review.reply_time,
        is_read=review.is_read,
        is_flagged=review.is_flagged,
        created_at=review.created_at
    )

@router.put("/{review_id}/read", summary="标记为已读")
async def mark_as_read(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    标记评论为已读
    
    - **review_id**: 评论 ID
    """
    try:
        review = ReviewService.mark_as_read(db, review_id)
        return {"message": "标记成功", "review_id": review_id}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/{review_id}/flag", summary="标记评论")
async def flag_review(
    review_id: int,
    flag_reason: str = Query(..., description="标记原因"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    标记评论（需重点关注）
    
    - **review_id**: 评论 ID
    - **flag_reason**: 标记原因
    """
    try:
        review = ReviewService.flag_review(db, review_id, flag_reason)
        return {"message": "标记成功", "review_id": review_id}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/stats/{merchant_id}", response_model=ReviewStats, summary="获取评论统计")
async def get_review_stats(
    merchant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取商家评论统计
    
    - **merchant_id**: 商家 ID
    """
    stats = ReviewService.get_stats(db, merchant_id)
    return ReviewStats(**stats)

@router.post("/sync", summary="批量同步评论")
async def sync_reviews(
    merchant_id: int,
    platform: str,
    reviews: List[dict],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量同步评论（从平台导入）
    
    - **merchant_id**: 商家 ID
    - **platform**: 平台类型
    - **reviews**: 评论数据列表
    """
    try:
        from app.models.review import Platform
        
        platform_enum = Platform(platform)
        
        result = ReviewService.batch_sync_reviews(
            db,
            merchant_id,
            platform_enum,
            reviews
        )
        
        return {
            "message": "同步成功",
            "created": result['created'],
            "updated": result['updated'],
            "skipped": result['skipped']
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"批量同步评论失败：{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="同步失败"
        )
