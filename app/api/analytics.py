# 数据分析 API 路由
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.services.analytics_service import AnalyticsService
from app.api.deps import get_current_user
from app.models.user import User
from app.utils.logger import logger

router = APIRouter()

@router.get("/rating-trend", summary="获取评分趋势")
async def get_rating_trend(
    merchant_id: int = Query(..., description="商家 ID"),
    days: int = Query(30, ge=1, le=365, description="天数"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取评分变化趋势
    
    - **merchant_id**: 商家 ID
    - **days**: 查询天数（1-365）
    """
    try:
        trend = AnalyticsService.get_rating_trend(db, merchant_id, days)
        return {
            "code": 200,
            "data": trend,
            "message": "success"
        }
    except Exception as e:
        logger.error(f"获取评分趋势失败：{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取评分趋势失败"
        )

@router.get("/review-stats", summary="获取评论统计")
async def get_review_stats(
    merchant_id: int = Query(..., description="商家 ID"),
    days: int = Query(30, ge=1, le=365, description="天数"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取评论统计数据
    
    - **merchant_id**: 商家 ID
    - **days**: 查询天数
    """
    try:
        stats = AnalyticsService.get_review_stats(db, merchant_id, days)
        return {
            "code": 200,
            "data": stats,
            "message": "success"
        }
    except Exception as e:
        logger.error(f"获取评论统计失败：{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取评论统计失败"
        )

@router.get("/keywords", summary="获取关键词分析")
async def get_keywords(
    merchant_id: int = Query(..., description="商家 ID"),
    sentiment: Optional[str] = Query(None, description="情感：positive/negative"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取评论关键词分析
    
    - **merchant_id**: 商家 ID
    - **sentiment**: 情感分类（可选）
    - **limit**: 返回数量（1-100）
    """
    try:
        keywords = AnalyticsService.get_keywords(db, merchant_id, sentiment, limit)
        return {
            "code": 200,
            "data": keywords,
            "message": "success"
        }
    except Exception as e:
        logger.error(f"获取关键词失败：{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取关键词失败"
        )

@router.get("/topics", summary="获取主题分布")
async def get_topic_distribution(
    merchant_id: int = Query(..., description="商家 ID"),
    days: int = Query(30, ge=1, le=365, description="天数"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取评论主题分布
    
    - **merchant_id**: 商家 ID
    - **days**: 查询天数
    """
    try:
        topics = AnalyticsService.get_topic_distribution(db, merchant_id, days)
        return {
            "code": 200,
            "data": topics,
            "message": "success"
        }
    except Exception as e:
        logger.error(f"获取主题分布失败：{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取主题分布失败"
        )

@router.get("/unreplied", summary="获取未回复评论")
async def get_unreplied_reviews(
    merchant_id: int = Query(..., description="商家 ID"),
    limit: int = Query(10, ge=1, le=100, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取未回复的评论（优先差评）
    
    - **merchant_id**: 商家 ID
    - **limit**: 返回数量
    """
    try:
        reviews = AnalyticsService.get_unreplied_reviews(db, merchant_id, limit)
        return {
            "code": 200,
            "data": reviews,
            "message": "success"
        }
    except Exception as e:
        logger.error(f"获取未回复评论失败：{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取未回复评论失败"
        )

@router.get("/competitor", summary="竞品分析")
async def get_competitor_analysis(
    merchant_id: int = Query(..., description="商家 ID"),
    city: Optional[str] = Query(None, description="城市"),
    district: Optional[str] = Query(None, description="区域"),
    shop_type: Optional[str] = Query(None, description="店铺类型"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    竞品分析
    
    - **merchant_id**: 商家 ID
    - **city**: 城市（可选）
    - **district**: 区域（可选）
    - **shop_type**: 店铺类型（可选）
    """
    try:
        # 获取商家信息
        from app.services.review_service import ReviewService
        merchant = ReviewService.get_review_by_id(db, merchant_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="商家不存在"
            )
        
        analysis = AnalyticsService.get_competitor_analysis(
            db,
            merchant_id,
            city=city or merchant.city,
            district=district or merchant.district,
            shop_type=shop_type
        )
        
        return {
            "code": 200,
            "data": analysis,
            "message": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"竞品分析失败：{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="竞品分析失败"
        )

@router.get("/daily-report", summary="生成每日报告")
async def get_daily_report(
    merchant_id: int = Query(..., description="商家 ID"),
    date: Optional[str] = Query(None, description="日期 YYYY-MM-DD"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成每日报告
    
    - **merchant_id**: 商家 ID
    - **date**: 日期（可选，默认今天）
    """
    try:
        if date:
            report_date = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            report_date = datetime.utcnow().date()
        
        report = AnalyticsService.generate_daily_report(db, merchant_id, report_date)
        
        return {
            "code": 200,
            "data": report,
            "message": "success"
        }
    except Exception as e:
        logger.error(f"生成每日报告失败：{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="生成报告失败"
        )

@router.get("/dashboard", summary="获取仪表盘数据")
async def get_dashboard(
    merchant_id: int = Query(..., description="商家 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取仪表盘综合数据
    
    - **merchant_id**: 商家 ID
    """
    try:
        # 获取基础统计
        stats = AnalyticsService.get_review_stats(db, merchant_id, 30)
        
        # 获取评分趋势（最近 7 天）
        trend = AnalyticsService.get_rating_trend(db, merchant_id, 7)
        
        # 获取未回复评论
        unreplied = AnalyticsService.get_unreplied_reviews(db, merchant_id, 5)
        
        # 获取关键词
        keywords = AnalyticsService.get_keywords(db, merchant_id, limit=10)
        
        return {
            "code": 200,
            "data": {
                "stats": stats,
                "trend": trend,
                "unreplied": unreplied,
                "keywords": keywords
            },
            "message": "success"
        }
    except Exception as e:
        logger.error(f"获取仪表盘数据失败：{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取仪表盘数据失败"
        )
