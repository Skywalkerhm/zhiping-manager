# LLM 适配器基类
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LLMResponse:
    """LLM 响应数据类"""
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    provider: str
    latency_ms: int
    request_id: str
    success: bool
    error_message: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class BaseLLMAdapter(ABC):
    """LLM 适配器基类"""
    
    def __init__(self, api_key: str, config: Dict[str, Any]):
        self.api_key = api_key
        self.config = config
        self.base_url = config.get('base_url', '')
    
    @abstractmethod
    async def generate_reply(self, 
                            prompt: str,
                            system_prompt: str = None,
                            temperature: float = 0.7,
                            max_tokens: int = 500) -> LLMResponse:
        """
        生成回复
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大输出 token
        
        Returns:
            LLMResponse
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """测试连接"""
        pass
    
    @abstractmethod
    def get_provider_code(self) -> str:
        """获取提供商代码"""
        pass
    
    def _build_messages(self, prompt: str, system_prompt: str = None) -> list:
        """构建消息列表"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages
