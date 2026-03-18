# 评论回复服务
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.services.llm.llm_router import LLMRouter
from app.schemas.llm import ReplyGenerateRequest, ReplyGenerateResponse, LLMInfo
from app.models.llm import AIReply, LLMUsageLog
from app.utils.logger import logger
from datetime import datetime

class ReplyService:
    """评论回复服务"""
    
    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router
        self.system_prompts = {
            'positive': """你是一个专业的商家客服助手。请针对顾客的好评，生成一条真诚、热情的回复。
要求：
1. 表达感谢
2. 提及顾客评论中的具体内容
3. 邀请再次光临
4. 语气亲切自然
5. 字数控制在 100-200 字""",
            
            'negative': """你是一个专业的商家客服助手。请针对顾客的差评，生成一条诚恳、负责任的回复。
要求：
1. 首先真诚道歉
2. 针对顾客提到的具体问题给出解释或改进措施
3. 提供补偿方案或联系方式
4. 表达改进决心
5. 语气诚恳，不推卸责任
6. 字数控制在 150-250 字""",
            
            'neutral': """你是一个专业的商家客服助手。请针对顾客的中评，生成一条友好、积极的回复。
要求：
1. 感谢顾客的反馈
2. 对顾客提到的不足表示重视
3. 说明改进计划
4. 邀请再次体验
5. 语气友好
6. 字数控制在 100-200 字"""
        }
    
    async def generate_reply(self, 
                            request: ReplyGenerateRequest,
                            merchant_id: int,
                            db: Session) -> ReplyGenerateResponse:
        """
        生成回复
        
        Args:
            request: 回复生成请求
            merchant_id: 商家 ID
            db: 数据库会话
        
        Returns:
            ReplyGenerateResponse
        """
        # 获取商家 LLM 设置（简化处理，使用默认配置）
        preferred_provider = 'aliyun_qwen'
        preferred_model = 'qwen-turbo'
        temperature = 0.7
        max_tokens = 500
        use_fallback = True
        
        # 覆盖为用户请求的配置
        if request.llm_config:
            preferred_provider = request.llm_config.provider or preferred_provider
            preferred_model = request.llm_config.model or preferred_model
            temperature = request.llm_config.temperature
            max_tokens = request.llm_config.max_tokens
            use_fallback = request.llm_config.use_fallback
        
        # 获取系统提示词
        system_prompt = request.custom_prompt or self.system_prompts.get(
            request.sentiment, 
            self.system_prompts['neutral']
        )
        
        # 构建用户提示词
        user_prompt = self._build_user_prompt(request)
        
        # 调用 LLM 生成回复
        llm_response = await self.llm_router.generate_reply(
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider=preferred_provider,
            temperature=temperature,
            max_tokens=max_tokens,
            use_fallback=use_fallback
        )
        
        # 记录 LLM 使用日志
        if llm_response.success:
            await self._log_llm_usage(
                merchant_id=merchant_id,
                llm_response=llm_response,
                review_id=request.review_id,
                db=db
            )
            
            # 保存到 AI 回复记录表
            ai_reply = AIReply(
                review_id=request.review_id,
                ai_generated=llm_response.content,
                final_content=llm_response.content,
                prompt_used=user_prompt,
                system_prompt=system_prompt,
                llm_provider=llm_response.provider,
                llm_model=llm_response.model,
                prompt_tokens=llm_response.prompt_tokens,
                completion_tokens=llm_response.completion_tokens,
                total_tokens=llm_response.total_tokens,
                cost=self._calculate_cost(llm_response),
                latency_ms=llm_response.latency_ms,
                status='draft',
                request_id=llm_response.request_id
            )
            db.add(ai_reply)
            db.commit()
            db.refresh(ai_reply)
            
            # 生成备选回复（可选）
            alternatives = await self._generate_alternatives(
                request=request,
                system_prompt=system_prompt,
                provider=preferred_provider,
                temperature=temperature + 0.2,
                max_tokens=max_tokens
            )
            
            return ReplyGenerateResponse(
                reply_id=f"rpl_{ai_reply.id}",
                content=llm_response.content,
                llm_info=LLMInfo(
                    provider=llm_response.provider,
                    model=llm_response.model,
                    tokens_used=llm_response.total_tokens,
                    latency_ms=llm_response.latency_ms,
                    cost=self._calculate_cost(llm_response)
                ),
                alternatives=alternatives[:2]
            )
        else:
            # LLM 失败
            logger.error(f"生成回复失败：{llm_response.error_message}")
            raise ValueError(f"AI 回复生成失败：{llm_response.error_message}")
    
    def _build_user_prompt(self, request: ReplyGenerateRequest) -> str:
        """构建用户提示词"""
        prompt = f"""顾客评价信息：
- 评分：{request.review_rating}星
- 评论内容：{request.review_content}
- 评价标签：{', '.join(request.topics) if request.topics else '无'}

请根据以上信息生成回复。"""
        
        if request.custom_prompt:
            prompt += f"\n\n特殊要求：{request.custom_prompt}"
        
        return prompt
    
    async def _generate_alternatives(self, 
                                    request: ReplyGenerateRequest,
                                    system_prompt: str,
                                    provider: str,
                                    temperature: float,
                                    max_tokens: int) -> List[str]:
        """生成备选回复"""
        alternatives = []
        user_prompt = self._build_user_prompt(request)
        
        # 生成 2 个备选回复
        for i in range(2):
            response = await self.llm_router.generate_reply(
                prompt=user_prompt,
                system_prompt=system_prompt,
                provider=provider,
                temperature=temperature,
                max_tokens=max_tokens,
                use_fallback=False
            )
            if response.success:
                alternatives.append(response.content)
        
        return alternatives
    
    def _calculate_cost(self, llm_response) -> float:
        """计算成本"""
        cost_per_1k = {
            'aliyun_qwen': 0.002,
            'baidu_ernie': 0.003,
            'tencent_hunyuan': 0.0025,
            'openai_gpt35': 0.0015,
            'openai_gpt4': 0.03
        }
        
        rate = cost_per_1k.get(f"{llm_response.provider}", 0.002)
        return (llm_response.total_tokens / 1000) * rate
    
    async def _log_llm_usage(self, 
                            merchant_id: int,
                            llm_response,
                            review_id: int,
                            db: Session):
        """记录 LLM 使用日志"""
        log = LLMUsageLog(
            merchant_id=merchant_id,
            provider_code=llm_response.provider,
            model=llm_response.model,
            request_id=llm_response.request_id,
            review_id=review_id,
            prompt_tokens=llm_response.prompt_tokens,
            completion_tokens=llm_response.completion_tokens,
            total_tokens=llm_response.total_tokens,
            cost=self._calculate_cost(llm_response),
            latency_ms=llm_response.latency_ms,
            status='success' if llm_response.success else 'failed'
        )
        db.add(log)
        db.commit()
