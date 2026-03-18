# AI 回复 API 路由
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.llm import ReplyGenerateRequest, ReplyGenerateResponse
from app.services.reply_service import ReplyService
from app.services.llm.llm_router import LLMRouter
from app.api.deps import get_current_user
from app.models.user import User
from app.utils.logger import logger

router = APIRouter()

# 创建 LLM 路由和回复服务（实际应该用依赖注入）
llm_router = LLMRouter()
reply_service = ReplyService(llm_router)

@router.post("/generate", response_model=ReplyGenerateResponse, summary="生成 AI 回复")
async def generate_reply(
    request: ReplyGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    使用 AI 生成评论回复
    
    - **review_id**: 评论 ID
    - **review_content**: 评论内容
    - **review_rating**: 评分 (1-5)
    - **sentiment**: 情感分类 (positive/negative/neutral)
    - **topics**: 评价标签列表
    - **llm_config**: LLM 配置（可选）
    - **custom_prompt**: 自定义提示词（可选）
    
    返回生成的回复内容和备选回复
    """
    try:
        # 获取商家 ID（简化处理，实际应从用户关联获取）
        merchant_id = 1
        
        response = await reply_service.generate_reply(
            request=request,
            merchant_id=merchant_id,
            db=db
        )
        
        logger.info(f"生成回复成功：{response.reply_id}, LLM: {response.llm_info.provider}")
        return response
    
    except ValueError as e:
        logger.error(f"生成回复失败：{str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"生成回复异常：{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )

@router.post("/send/{reply_id}", summary="发送回复")
async def send_reply(
    reply_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    发送回复到评论平台
    
    - **reply_id**: 回复 ID
    """
    # TODO: 实现发送到大众点评/美团平台
    return {"message": "回复发送成功", "reply_id": reply_id}

@router.get("/{reply_id}", summary="获取回复详情")
async def get_reply(
    reply_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取回复详情
    
    - **reply_id**: 回复 ID
    """
    # TODO: 从数据库获取回复详情
    return {"reply_id": reply_id, "content": "示例回复内容"}
