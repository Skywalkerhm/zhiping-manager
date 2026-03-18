# LLM 路由服务
from typing import Dict, Any, Optional, List
from app.services.llm.base_adapter import BaseLLMAdapter, LLMResponse
from app.utils.logger import logger

class LLMRouter:
    """LLM 路由服务 - 支持多 LLM 提供商和故障切换"""
    
    def __init__(self):
        self.adapters: Dict[str, BaseLLMAdapter] = {}
        self.provider_priority: List[tuple] = []
    
    def register_adapter(self, adapter: BaseLLMAdapter, priority: int = 0):
        """
        注册 LLM 适配器
        
        Args:
            adapter: LLM 适配器实例
            priority: 优先级，数字越小优先级越高
        """
        provider_code = adapter.get_provider_code()
        self.adapters[provider_code] = adapter
        self.provider_priority.append((priority, provider_code))
        self.provider_priority.sort(key=lambda x: x[0])
        logger.info(f"注册 LLM 适配器：{provider_code}, 优先级：{priority}")
    
    async def generate_reply(self,
                            prompt: str,
                            system_prompt: str = None,
                            provider: str = None,
                            temperature: float = 0.7,
                            max_tokens: int = 500,
                            use_fallback: bool = True) -> LLMResponse:
        """
        生成回复
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            provider: 指定 LLM 提供商，不传则按优先级选择
            temperature: 温度参数
            max_tokens: 最大输出 token
            use_fallback: 是否启用故障切换
        
        Returns:
            LLMResponse
        """
        # 确定要使用的 LLM 列表
        if provider and provider in self.adapters:
            providers_to_try = [provider]
        elif use_fallback and self.provider_priority:
            providers_to_try = [p[1] for p in self.provider_priority]
        elif self.provider_priority:
            providers_to_try = [self.provider_priority[0][1]]
        else:
            return LLMResponse(
                content='',
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model='',
                provider='',
                latency_ms=0,
                request_id='',
                success=False,
                error_message="No LLM providers available"
            )
        
        # 依次尝试各个 LLM
        last_error = None
        for provider_code in providers_to_try:
            if provider_code not in self.adapters:
                continue
            
            adapter = self.adapters[provider_code]
            logger.info(f"尝试使用 LLM: {provider_code}")
            
            response = await adapter.generate_reply(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            if response.success:
                logger.info(f"LLM {provider_code} 成功，耗时：{response.latency_ms}ms")
                return response
            
            logger.warning(f"LLM {provider_code} 失败：{response.error_message}")
            last_error = response.error_message
        
        # 所有 LLM 都失败
        logger.error(f"所有 LLM 提供商都失败，最后错误：{last_error}")
        return LLMResponse(
            content='',
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            model='',
            provider='',
            latency_ms=0,
            request_id='',
            success=False,
            error_message=f"All LLM providers failed. Last error: {last_error}"
        )
    
    async def test_all_connections(self) -> Dict[str, bool]:
        """测试所有 LLM 连接"""
        results = {}
        for provider_code, adapter in self.adapters.items():
            try:
                results[provider_code] = await adapter.test_connection()
            except Exception as e:
                results[provider_code] = False
                logger.error(f"测试 {provider_code} 连接失败：{str(e)}")
        return results
    
    def get_available_providers(self) -> List[str]:
        """获取可用的 LLM 提供商列表"""
        return [p[1] for p in self.provider_priority if p[1] in self.adapters]
