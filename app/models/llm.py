# LLM 模型
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, DECIMAL, Text
from sqlalchemy.sql import func
from app.database import Base

class LLMProvider(Base):
    """LLM 提供商配置"""
    __tablename__ = "llm_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_code = Column(String(50), unique=True, nullable=False, index=True)
    provider_name = Column(String(100), nullable=False)
    api_base_url = Column(String(255))
    api_key = Column(String(255))
    secret_key = Column(String(255))
    models = Column(JSON)
    is_enabled = Column(Boolean, default=True, index=True)
    priority = Column(Integer, default=0, index=True)
    rate_limit = Column(Integer, default=100)
    daily_quota = Column(Integer, default=10000)
    daily_used = Column(Integer, default=0)
    cost_per_1k_tokens = Column(DECIMAL(10, 6), default=0.000000)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class MerchantLLMSetting(Base):
    """商家 LLM 设置"""
    __tablename__ = "merchant_llm_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, unique=True, nullable=False, index=True)
    preferred_provider = Column(String(50), default="aliyun_qwen")
    preferred_model = Column(String(50), default="qwen-turbo")
    auto_switch_enabled = Column(Boolean, default=True)
    temperature = Column(DECIMAL(3, 2), default=0.70)
    max_tokens = Column(Integer, default=500)
    custom_system_prompt = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class AIReply(Base):
    """AI 回复记录"""
    __tablename__ = "ai_replies"
    
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, nullable=False, index=True)
    original_content = Column(Text)
    ai_generated = Column(Text, nullable=False)
    final_content = Column(Text)
    prompt_used = Column(Text)
    system_prompt = Column(Text)
    llm_provider = Column(String(50), index=True)
    llm_model = Column(String(50))
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost = Column(DECIMAL(10, 6), default=0.000000)
    latency_ms = Column(Integer, default=0)
    status = Column(String(20), default="draft", index=True)
    request_id = Column(String(100))
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime)

class LLMUsageLog(Base):
    """LLM 使用日志"""
    __tablename__ = "llm_usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, nullable=False, index=True)
    provider_code = Column(String(50), nullable=False, index=True)
    model = Column(String(50), nullable=False)
    request_id = Column(String(100))
    review_id = Column(Integer)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost = Column(DECIMAL(10, 6), default=0.000000)
    latency_ms = Column(Integer, default=0)
    status = Column(String(20), default="success", index=True)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
