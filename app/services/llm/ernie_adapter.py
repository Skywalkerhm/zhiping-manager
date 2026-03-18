# 文心一言 LLM 适配器
import aiohttp
import time
from typing import Dict, Any
from app.services.llm.base_adapter import BaseLLMAdapter, LLMResponse
from app.utils.logger import logger

class ErnieAdapter(BaseLLMAdapter):
    """百度文心一言 LLM 适配器"""
    
    def __init__(self, api_key: str, secret_key: str, config: Dict[str, Any]):
        super().__init__(api_key, config)
        self.secret_key = secret_key
        self.access_token = None
        self.token_expire_time = 0
    
    async def _get_access_token(self) -> str:
        """获取访问令牌"""
        if self.access_token and time.time() < self.token_expire_time:
            return self.access_token
        
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, params=params) as response:
                    result = await response.json()
                    self.access_token = result['access_token']
                    self.token_expire_time = time.time() + result['expires_in'] - 60
                    return self.access_token
        except Exception as e:
            logger.error(f"获取文心一言 access_token 失败：{str(e)}")
            raise
    
    async def generate_reply(self,
                            prompt: str,
                            system_prompt: str = None,
                            temperature: float = 0.7,
                            max_tokens: int = 500) -> LLMResponse:
        """生成回复"""
        start_time = time.time()
        model = self.config.get('model', 'ernie-bot-4')
        
        try:
            access_token = await self._get_access_token()
        except Exception as e:
            return LLMResponse(
                content='',
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model=model,
                provider='baidu_ernie',
                latency_ms=int((time.time() - start_time) * 1000),
                request_id='',
                success=False,
                error_message=f"Failed to get access token: {str(e)}"
            )
        
        messages = self._build_messages(prompt, system_prompt)
        
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_output_tokens": max_tokens
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token={access_token}",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    result = await response.json()
                    latency = int((time.time() - start_time) * 1000)
                    
                    if 'result' in result:
                        usage = result.get('usage', {})
                        return LLMResponse(
                            content=result['result'],
                            prompt_tokens=usage.get('prompt_tokens', 0),
                            completion_tokens=usage.get('completion_tokens', 0),
                            total_tokens=usage.get('total_tokens', 0),
                            model=model,
                            provider='baidu_ernie',
                            latency_ms=latency,
                            request_id=result.get('id', ''),
                            success=True
                        )
                    else:
                        error_msg = result.get('error_msg', 'Unknown error')
                        logger.error(f"文心一言 API 错误：{error_msg}")
                        return LLMResponse(
                            content='',
                            prompt_tokens=0,
                            completion_tokens=0,
                            total_tokens=0,
                            model=model,
                            provider='baidu_ernie',
                            latency_ms=latency,
                            request_id=result.get('id', ''),
                            success=False,
                            error_message=error_msg
                        )
        except aiohttp.ClientError as e:
            latency = int((time.time() - start_time) * 1000)
            logger.error(f"文心一言网络错误：{str(e)}")
            return LLMResponse(
                content='',
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model=model,
                provider='baidu_ernie',
                latency_ms=latency,
                request_id='',
                success=False,
                error_message=f"Network error: {str(e)}"
            )
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            logger.error(f"文心一言未知错误：{str(e)}", exc_info=True)
            return LLMResponse(
                content='',
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model=model,
                provider='baidu_ernie',
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
        return 'baidu_ernie'
