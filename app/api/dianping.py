# 大众点评 OAuth API 路由
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.dianping_service import dianping_service
from app.utils.logger import logger
from app.config import settings
import urllib.parse

router = APIRouter()

@router.get("/authorize", summary="获取大众点评授权 URL")
async def get_dianping_auth_url(
    redirect_uri: str = Query(..., description="回调地址"),
    current_user: User = Depends(get_current_user)
):
    """
    获取大众点评 OAuth 授权 URL
    
    - **redirect_uri**: 授权成功后的回调地址
    """
    if not settings.DIANPING_APP_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="未配置大众点评 App Key"
        )
    
    # 构建授权 URL
    params = {
        "app_key": settings.DIANPING_APP_KEY,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "review_read,shop_read"
    }
    
    auth_url = f"https://api.dianping.com/oauth2/authorize?{urllib.parse.urlencode(params)}"
    
    return {
        "code": 200,
        "data": {
            "auth_url": auth_url
        },
        "message": "请访问此 URL 进行授权"
    }

@router.get("/callback", summary="大众点评 OAuth 回调")
async def dianping_callback(
    code: str = Query(..., description="授权码"),
    state: Optional[str] = Query(None, description="状态参数"),
    db: Session = Depends(get_db)
):
    """
    大众点评 OAuth 回调处理
    
    - **code**: 授权码
    - **state**: 状态参数（可选）
    """
    try:
        # 使用授权码换取 access_token
        params = {
            "app_key": settings.DIANPING_APP_KEY,
            "app_secret": settings.DIANPING_APP_SECRET,
            "grant_type": "authorization_code",
            "code": code
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.dianping.com/oauth2/access_token",
                json=params
            ) as response:
                result = await response.json()
                
                if result.get('error'):
                    logger.error(f"换取 Token 失败：{result['error']}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"授权失败：{result['error']}"
                    )
                
                access_token = result['access_token']
                expires_in = result.get('expires_in', 0)
                refresh_token = result.get('refresh_token', '')
                
                # TODO: 保存 Token 到数据库（关联当前用户）
                
                logger.info("大众点评授权成功")
                
                return {
                    "code": 200,
                    "data": {
                        "access_token": access_token,
                        "expires_in": expires_in,
                        "refresh_token": refresh_token
                    },
                    "message": "授权成功"
                }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth 回调异常：{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"授权失败：{str(e)}"
        )

@router.post("/sync/{shop_id}", summary="同步店铺评论")
async def sync_shop_reviews(
    shop_id: str,
    max_pages: int = Query(5, ge=1, le=20, description="最大同步页数"),
    page_size: int = Query(20, ge=1, le=50, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    同步大众点评店铺评论
    
    - **shop_id**: 店铺 ID
    - **max_pages**: 最大同步页数（1-20）
    - **page_size**: 每页数量（1-50）
    """
    try:
        # 获取评论
        reviews = await dianping_service.batch_sync_reviews(
            shop_id,
            max_pages,
            page_size
        )
        
        if not reviews:
            return {
                "code": 200,
                "data": {
                    "synced": 0
                },
                "message": "无评论可同步"
            }
        
        # TODO: 保存到数据库
        # from app.services.review_service import ReviewService
        # from app.models.review import Platform
        # 
        # merchant = get_merchant_by_shop_id(db, shop_id)
        # ReviewService.batch_sync_reviews(db, merchant.id, Platform.DIANPING, reviews)
        
        logger.info(f"同步 {len(reviews)} 条评论成功")
        
        return {
            "code": 200,
            "data": {
                "synced": len(reviews),
                "reviews": reviews[:10]  # 返回前 10 条预览
            },
            "message": "同步成功"
        }
    
    except Exception as e:
        logger.error(f"同步评论失败：{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步失败：{str(e)}"
        )

@router.get("/shop/{shop_id}", summary="获取店铺信息")
async def get_shop_info(
    shop_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    获取大众点评店铺信息
    
    - **shop_id**: 店铺 ID
    """
    try:
        shop_info = await dianping_service.get_shop_info(shop_id)
        
        if not shop_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="店铺不存在"
            )
        
        return {
            "code": 200,
            "data": shop_info,
            "message": "success"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取店铺信息失败：{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取失败：{str(e)}"
        )

@router.post("/test", summary="测试大众点评 API 连接")
async def test_dianping_connection(
    current_user: User = Depends(get_current_user)
):
    """
    测试大众点评 API 连接
    """
    try:
        success = await dianping_service.test_connection()
        
        return {
            "code": 200,
            "data": {
                "status": "connected" if success else "failed"
            },
            "message": "连接成功" if success else "连接失败"
        }
    
    except Exception as e:
        logger.error(f"测试连接失败：{str(e)}")
        return {
            "code": 500,
            "data": {
                "status": "failed"
            },
            "message": f"测试失败：{str(e)}"
        }
