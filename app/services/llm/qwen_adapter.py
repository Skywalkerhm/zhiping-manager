# 通义千问 LLM 适配器
import aiohttp
import time
from typing import Dict, Any
from app.services.llm.base_adapter import BaseLLMAdapter, LLMResponse
from app.utils.logger import logger

class QwenAdapter(BaseLLMAdapter):
    """通义千问 LLM 适配器"""
    
    def __init__(self, api_key: str, config: Dict[str, Any]):
        super().__init__(api_key, config)
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"
    
    async def generate_reply(self,
                            prompt: str,
                            system_prompt: str = None,
                            temperature: float = 0.7,
                            max_tokens: int = 500) -> LLMResponse:
        """生成回复"""
        start_time = time.time()
        model = self.config.get('model', 'qwen-turbo')
        
        messages = self._build_messages(prompt, system_prompt)
        
        payload = {
            "model": model,
            "input": {"messages": messages},
            "parameters": {
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/services/aigc/text-generation/generation",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    result = await response.json()
                    latency = int((time.time() - start_time) * 1000)
                    
                    if response.status == 200 and result.get('output', {}).get('text'):
                        usage = result.get('usage', {})
                        return LLMResponse(
                            content=result['output']['text'],
                            prompt_tokens=usage.get('input_tokens', 0),
                            completion_tokens=usage.get('output_tokens', 0),
                            total_tokens=usage.get('total_tokens', 0),
                            model=model,
                            provider='aliyun_qwen',
                            latency_ms=latency,
                            request_id=result.get('request_id', ''),
                            success=True
                        )
                    else:
                        error_msg = result.get('message', 'Unknown error')
                        logger.error(f"通义千问 API 错误：{error_msg}")
                        return LLMResponse(
                            content='',
                            prompt_tokens=0,
                            completion_tokens=0,
                            total_tokens=0,
                            model=model,
                            provider='aliyun_qwen',
                            latency_ms=latency,
                            request_id=result.get('request_id', ''),
                            success=False,
                            error_message=error_msg
                        )
        except aiohttp.ClientError as e:
            latency = int((time.time() - start_time) * 1000)
            logger.error(f"通义千问网络错误：{str(e)}")
            return LLMResponse(
                content='',
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model=model,
                provider='aliyun_qwen',
                latency_ms=latency,
                request_id='',
                success=False,
                error_message=f"Network error: {str(e)}"
            )
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            logger.error(f"通义千问未知错误：{str(e)}", exc_info=True)
            return LLMResponse(
                content='',
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model=model,
                provider='aliyun_qwen',
                latency_ms=latency,
                request_id='',
                success=False,
                error_message=str(e)
            )
    
    async def test_connection(self) -> bool:
        """测试连接"""
        response = await self.generate_reply(prompt="你好", max_tokens=10)
        return response.success
    
    def get_provider_code(self) -> str:
        return 'aliyun_qwen'
