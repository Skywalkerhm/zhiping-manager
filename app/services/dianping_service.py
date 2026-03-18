# 大众点评 API 服务
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import aiohttp
import hashlib
import time
from app.utils.logger import logger
from app.config import settings

class DianpingService:
    """大众点评开放平台服务"""
    
    def __init__(self):
        self.app_key = settings.DIANPING_APP_KEY
        self.app_secret = settings.DIANPING_APP_SECRET
        self.base_url = "https://api.dianping.com"
        self.access_token = None
        self.token_expire_time = 0
    
    def _generate_sign(self, params: Dict[str, Any]) -> str:
        """
        生成 API 签名
        
        签名算法：
        1. 将所有参数按 key 的 ASCII 码从小到大排序
        2. 拼接成 key=value&key=value 格式
        3. 在末尾加上 app_secret
        4. 进行 MD5 加密
        """
        sorted_params = sorted(params.items())
        param_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        sign_string = f"{param_string}{self.app_secret}"
        return hashlib.md5(sign_string.encode()).hexdigest().upper()
    
    async def _get_access_token(self) -> str:
        """获取访问令牌（OAuth 2.0）"""
        if self.access_token and time.time() < self.token_expire_time:
            return self.access_token
        
        # OAuth 授权流程
        params = {
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "grant_type": "client_credentials"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/oauth2/access_token",
                    json=params
                ) as response:
                    result = await response.json()
                    
                    if result.get('error'):
                        raise Exception(f"获取 Token 失败：{result['error']}")
                    
                    self.access_token = result['access_token']
                    self.token_expire_time = time.time() + result['expires_in'] - 60
                    
                    logger.info("成功获取大众点评 access_token")
                    return self.access_token
                    
        except Exception as e:
            logger.error(f"获取大众点评 Token 失败：{str(e)}")
            raise
    
    async def get_shop_reviews(
        self,
        shop_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取店铺评论列表
        
        Args:
            shop_id: 店铺 ID
            page: 页码
            page_size: 每页数量
        
        Returns:
            {
                "total": 100,
                "reviews": [...]
            }
        """
        try:
            access_token = await self._get_access_token()
            
            params = {
                "app_key": self.app_key,
                "shop_id": shop_id,
                "page": page,
                "page_size": page_size,
                "_sig": ""  # 将由 _generate_sign 生成
            }
            
            # 添加时间戳
            params["timestamp"] = str(int(time.time()))
            
            # 生成签名
            params["_sig"] = self._generate_sign(params)
            
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/review/1/shop_reviews",
                    params=params,
                    headers=headers
                ) as response:
                    result = await response.json()
                    
                    if result.get('error'):
                        logger.error(f"获取评论失败：{result['error']}")
                        return {"total": 0, "reviews": []}
                    
                    reviews = result.get('reviews', [])
                    total = result.get('total', 0)
                    
                    # 格式化评论数据
                    formatted_reviews = [
                        self._format_review(review)
                        for review in reviews
                    ]
                    
                    logger.info(f"获取店铺 {shop_id} 评论：{len(formatted_reviews)}条")
                    
                    return {
                        "total": total,
                        "reviews": formatted_reviews
                    }
                    
        except Exception as e:
            logger.error(f"获取评论异常：{str(e)}", exc_info=True)
            return {"total": 0, "reviews": []}
    
    def _format_review(self, review: Dict[str, Any]) -> Dict[str, Any]:
        """格式化评论数据"""
        return {
            "review_id": str(review.get('id', '')),
            "user_name": review.get('user', {}).get('nick', '匿名用户'),
            "user_avatar": review.get('user', {}).get('avatar', ''),
            "rating": review.get('rating', 5),
            "content": review.get('content', ''),
            "images": review.get('images', []),
            "review_time": self._parse_time(review.get('created_at')),
            "shop_id": review.get('shop', {}).get('id', ''),
            "shop_name": review.get('shop', {}).get('name', '')
        }
    
    def _parse_time(self, time_str: str) -> Optional[datetime]:
        """解析时间字符串"""
        if not time_str:
            return None
        
        try:
            # 尝试多种格式
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%Y/%m/%d %H:%M:%S"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(time_str, fmt)
                except ValueError:
                    continue
            
            return None
        except Exception:
            return None
    
    async def get_shop_info(self, shop_id: str) -> Optional[Dict[str, Any]]:
        """获取店铺信息"""
        try:
            access_token = await self._get_access_token()
            
            params = {
                "app_key": self.app_key,
                "shop_id": shop_id,
                "timestamp": str(int(time.time()))
            }
            params["_sig"] = self._generate_sign(params)
            
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/shop/1/get_shop_info",
                    params=params,
                    headers=headers
                ) as response:
                    result = await response.json()
                    
                    if result.get('error'):
                        return None
                    
                    shop_info = result.get('shop', {})
                    
                    return {
                        "shop_id": str(shop_info.get('id', '')),
                        "shop_name": shop_info.get('name', ''),
                        "address": shop_info.get('address', ''),
                        "city": shop_info.get('city', ''),
                        "district": shop_info.get('district', ''),
                        "latitude": shop_info.get('latitude'),
                        "longitude": shop_info.get('longitude'),
                        "avg_rating": shop_info.get('overall_rating', 0),
                        "total_reviews": shop_info.get('review_num', 0)
                    }
                    
        except Exception as e:
            logger.error(f"获取店铺信息失败：{str(e)}")
            return None
    
    async def batch_sync_reviews(
        self,
        shop_id: str,
        max_pages: int = 5,
        page_size: int = 20
    ) -> List[Dict[str, Any]]:
        """
        批量同步评论（多页）
        
        Args:
            shop_id: 店铺 ID
            max_pages: 最大页数
            page_size: 每页数量
        
        Returns:
            评论列表
        """
        all_reviews = []
        
        for page in range(1, max_pages + 1):
            logger.info(f"同步第 {page} 页评论...")
            
            result = await self.get_shop_reviews(shop_id, page, page_size)
            
            if not result['reviews']:
                logger.info(f"第 {page} 页无评论，停止同步")
                break
            
            all_reviews.extend(result['reviews'])
            
            # 避免请求过快
            await asyncio.sleep(0.5)
        
        logger.info(f"批量同步完成，共 {len(all_reviews)} 条评论")
        return all_reviews
    
    async def test_connection(self) -> bool:
        """测试 API 连接"""
        try:
            token = await self._get_access_token()
            return bool(token)
        except Exception:
            return False


# 创建单例
dianping_service = DianpingService()
