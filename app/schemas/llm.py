# LLM Schema
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# LLM 配置
class LLMConfig(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=500, ge=100, le=4000)
    use_fallback: bool = True

# 回复生成请求
class ReplyGenerateRequest(BaseModel):
    review_id: int
    review_content: str
    review_rating: int = Field(..., ge=1, le=5)
    sentiment: str = "neutral"
    topics: Optional[List[str]] = None
    llm_config: Optional[LLMConfig] = None
    custom_prompt: Optional[str] = None

# LLM 信息
class LLMInfo(BaseModel):
    provider: str
    model: str
    tokens_used: int
    latency_ms: int
    cost: float

# 回复生成响应
class ReplyGenerateResponse(BaseModel):
    reply_id: str
    content: str
    llm_info: LLMInfo
    alternatives: Optional[List[str]] = None

# LLM 提供商信息
class LLMProviderInfo(BaseModel):
    provider_code: str
    provider_name: str
    models: List[str]
    is_enabled: bool
    priority: int
    cost_per_1k: float

# LLM 使用统计
class LLMUsageStats(BaseModel):
    total_requests: int
    total_tokens: int
    total_cost: float
    success_rate: float
    avg_latency_ms: int
    by_provider: dict
