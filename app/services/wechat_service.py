# 微信消息推送服务
from typing import List, Optional
import aiohttp
from app.utils.logger import logger
from app.config import settings

class WechatService:
    """微信模板消息推送服务"""
    
    def __init__(self):
        self.app_id = settings.WECHAT_APP_ID
        self.app_secret = settings.WECHAT_APP_SECRET
        self.access_token = None
        self.token_expire_time = 0
    
    async def _get_access_token(self) -> str:
        """获取微信 access_token"""
        if self.access_token and self.token_expire_time > 0:
            import time
            if time.time() < self.token_expire_time:
                return self.access_token
        
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    result = await response.json()
                    
                    if result.get('errcode'):
                        raise Exception(f"获取微信 Token 失败：{result['errmsg']}")
                    
                    self.access_token = result['access_token']
                    self.token_expire_time = int(time.time()) + result['expires_in'] - 300
                    
                    return self.access_token
                    
        except Exception as e:
            logger.error(f"获取微信 Token 失败：{str(e)}")
            raise
    
    async def send_template_message(
        self,
        openid: str,
        template_id: str,
        data: dict,
        url: str = None,
        miniprogram: dict = None
    ) -> bool:
        """
        发送模板消息
        
        Args:
            openid: 用户 OpenID
            template_id: 模板 ID
            data: 模板数据
            url: 点击跳转链接
            miniprogram: 小程序信息
        
        Returns:
            是否发送成功
        """
        try:
            access_token = await self._get_access_token()
            
            payload = {
                "touser": openid,
                "template_id": template_id,
                "data": data
            }
            
            if url:
                payload["url"] = url
            
            if miniprogram:
                payload["miniprogram"] = miniprogram
            
            send_url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(send_url, json=payload) as response:
                    result = await response.json()
                    
                    if result.get('errcode') == 0:
                        logger.info(f"微信模板消息发送成功：{openid}")
                        return True
                    else:
                        logger.error(f"微信模板消息发送失败：{result['errmsg']}")
                        return False
                        
        except Exception as e:
            logger.error(f"发送微信消息异常：{str(e)}", exc_info=True)
            return False
    
    async def send_new_review_notification(
        self,
        openid: str,
        shop_name: str,
        rating: int,
        content: str,
        review_url: str
    ) -> bool:
        """
        发送新评论通知
        
        Args:
            openid: 用户 OpenID
            shop_name: 店铺名称
            rating: 评分
            content: 评论内容
            review_url: 评论详情链接
        """
        template_id = settings.WECHAT_TEMPLATE_ID_NOTICE or "new_review_notice"
        
        data = {
            "thing1": {"value": shop_name},
            "thing2": {"value": f"{'⭐' * rating}"},
            "thing3": {"value": content[:20] + "..." if len(content) > 20 else content},
            "time4": {"value": "刚刚"}
        }
        
        return await self.send_template_message(
            openid=openid,
            template_id=template_id,
            data=data,
            url=review_url
        )
    
    async def send_daily_report(
        self,
        openid: str,
        shop_name: str,
        new_reviews: int,
        avg_rating: float,
        unreplied: int,
        report_url: str
    ) -> bool:
        """
        发送每日报告
        
        Args:
            openid: 用户 OpenID
            shop_name: 店铺名称
            new_reviews: 新评论数
            avg_rating: 平均评分
            unreplied: 未回复数
            report_url: 报告链接
        """
        template_id = "daily_report_template"
        
        data = {
            "thing1": {"value": shop_name},
            "character_string2": {"value": str(new_reviews)},
            "thing3": {"value": f"{avg_rating:.1f}分"},
            "thing4": {"value": str(unreplied)},
            "time5": {"value": "今天"}
        }
        
        return await self.send_template_message(
            openid=openid,
            template_id=template_id,
            data=data,
            url=report_url
        )


# 创建单例
wechat_service = WechatService()
