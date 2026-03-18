# LLM 管理 API 路由
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.llm.llm_router import LLMRouter
from app.services.llm.qwen_adapter import QwenAdapter
from app.services.llm.ernie_adapter import ErnieAdapter
from app.config import settings
from app.utils.logger import logger

router = APIRouter()

# 初始化 LLM 路由
llm_router = LLMRouter()

# 注册 LLM 适配器（从配置加载）
if settings.QWEN_API_KEY:
    llm_router.register_adapter(
        QwenAdapter(
            api_key=settings.QWEN_API_KEY,
            config={"model": "qwen-turbo"}
        ),
        priority=0
    )

if settings.ERNIE_API_KEY and settings.ERNIE_SECRET_KEY:
    llm_router.register_adapter(
        ErnieAdapter(
            api_key=settings.ERNIE_API_KEY,
            secret_key=settings.ERNIE_SECRET_KEY,
            config={"model": "ernie-bot-4"}
        ),
        priority=1
    )

@router.get("/providers", summary="获取 LLM 提供商列表")
async def get_llm_providers(
    current_user: User = Depends(get_current_user)
):
    """
    获取所有可用的 LLM 提供商
    """
    providers = llm_router.get_available_providers()
    
    provider_info = {
        "aliyun_qwen": {
            "name": "通义千问",
            "models": ["qwen-turbo", "qwen-plus", "qwen-max"],
            "cost_per_1k": 0.002
        },
        "baidu_ernie": {
            "name": "文心一言",
            "models": ["ernie-bot-4", "ernie-bot-turbo"],
            "cost_per_1k": 0.003
        },
        "tencent_hunyuan": {
            "name": "腾讯混元",
            "models": ["hunyuan-pro"],
            "cost_per_1k": 0.0025
        }
    }
    
    result = []
    for provider_code in providers:
        info = provider_info.get(provider_code, {})
        result.append({
            "provider_code": provider_code,
            "provider_name": info.get("name", provider_code),
            "models": info.get("models", []),
            "cost_per_1k": info.get("cost_per_1k", 0)
        })
    
    return {
        "code": 200,
        "data": result,
        "message": "success"
    }

@router.post("/test", summary="测试 LLM 连接")
async def test_llm_connection(
    provider: str = None,
    current_user: User = Depends(get_current_user)
):
    """
    测试 LLM 连接状态
    
    - **provider**: 指定测试的提供商（可选）
    """
    try:
        if provider:
            # 测试指定提供商
            if provider not in llm_router.adapters:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"不支持的 LLM 提供商：{provider}"
                )
            
            adapter = llm_router.adapters[provider]
            success = await adapter.test_connection()
            
            return {
                "code": 200,
                "data": {
                    "provider": provider,
                    "status": "connected" if success else "failed"
                },
                "message": "测试成功"
            }
        else:
            # 测试所有提供商
            results = await llm_router.test_all_connections()
            
            return {
                "code": 200,
                "data": {
                    provider: "connected" if status else "failed"
                    for provider, status in results.items()
                },
                "message": "测试完成"
            }
    
    except Exception as e:
        logger.error(f"测试 LLM 连接失败：{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"测试失败：{str(e)}"
        )

@router.get("/settings", summary="获取 LLM 设置")
async def get_llm_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的 LLM 设置
    """
    # TODO: 从数据库获取商家 LLM 设置
    return {
        "code": 200,
        "data": {
            "preferred_provider": "aliyun_qwen",
            "preferred_model": "qwen-turbo",
            "auto_switch_enabled": True,
            "temperature": 0.7,
            "max_tokens": 500
        },
        "message": "success"
    }

@router.put("/settings", summary="更新 LLM 设置")
async def update_llm_settings(
    preferred_provider: str = None,
    preferred_model: str = None,
    auto_switch_enabled: bool = None,
    temperature: float = None,
    max_tokens: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新 LLM 设置
    
    - **preferred_provider**: 首选 LLM 提供商
    - **preferred_model**: 首选模型
    - **auto_switch_enabled**: 是否启用自动切换
    - **temperature**: 温度参数（0-1）
    - **max_tokens**: 最大输出 token
    """
    # TODO: 保存到数据库
    
    return {
        "code": 200,
        "data": {
            "preferred_provider": preferred_provider,
            "preferred_model": preferred_model,
            "auto_switch_enabled": auto_switch_enabled,
            "temperature": temperature,
            "max_tokens": max_tokens
        },
        "message": "设置已更新"
    }

@router.get("/usage", summary="获取使用统计")
async def get_llm_usage(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取 LLM 使用统计
    
    - **days**: 查询天数
    """
    # TODO: 从 llm_usage_logs 表查询统计
    
    return {
        "code": 200,
        "data": {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0,
            "success_rate": 100.0,
            "by_provider": {}
        },
        "message": "success"
    }
