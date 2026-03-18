# 定时任务服务
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.utils.logger import logger
from app.database import get_db
from app.services.review_service import ReviewService
from app.services.analytics_service import AnalyticsService
from app.services.wechat_service import wechat_service
from app.models.merchant import Merchant
from datetime import datetime, timedelta

class TaskScheduler:
    """定时任务调度器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
    
    def start(self):
        """启动调度器"""
        # 每 10 分钟检查新评论
        self.scheduler.add_job(
            self.check_new_reviews,
            CronTrigger(minute='*/10'),
            id='check_new_reviews',
            name='检查新评论'
        )
        
        # 每天早上 9 点发送日报
        self.scheduler.add_job(
            self.send_daily_reports,
            CronTrigger(hour=9, minute=0),
            id='send_daily_reports',
            name='发送每日报告'
        )
        
        # 每小时同步一次评论
        self.scheduler.add_job(
            self.sync_all_reviews,
            CronTrigger(minute=0),
            id='sync_all_reviews',
            name='同步所有评论'
        )
        
        self.scheduler.start()
        logger.info("定时任务调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        logger.info("定时任务调度器已停止")
    
    async def check_new_reviews(self):
        """检查新评论并发送通知"""
        logger.info("开始检查新评论...")
        
        try:
            db = next(get_db())
            
            # 获取所有商家
            merchants = db.query(Merchant).filter(Merchant.status == True).all()
            
            for merchant in merchants:
                # 获取未读评论
                stats = AnalyticsService.get_stats(db, merchant.id)
                unreplied = AnalyticsService.get_unreplied_reviews(db, merchant.id, 1)
                
                if unreplied:
                    # 获取商家通知设置
                    # TODO: 从数据库获取 openid
                    openid = merchant.phone  # 简化处理
                    
                    # 发送通知
                    review = unreplied[0]
                    await wechat_service.send_new_review_notification(
                        openid=openid,
                        shop_name=merchant.shop_name,
                        rating=review['rating'],
                        content=review['content'],
                        review_url=f"https://zhiping.com/reviews/{review['id']}"
                    )
            
            logger.info("新评论检查完成")
            
        except Exception as e:
            logger.error(f"检查新评论失败：{str(e)}", exc_info=True)
        finally:
            db.close()
    
    async def send_daily_reports(self):
        """发送每日报告"""
        logger.info("开始发送每日报告...")
        
        try:
            db = next(get_db())
            merchants = db.query(Merchant).filter(Merchant.status == True).all()
            
            for merchant in merchants:
                # 生成日报
                report = AnalyticsService.generate_daily_report(db, merchant.id)
                
                if report['new_reviews'] > 0:
                    # TODO: 获取商家 openid
                    openid = merchant.phone
                    
                    await wechat_service.send_daily_report(
                        openid=openid,
                        shop_name=merchant.shop_name,
                        new_reviews=report['new_reviews'],
                        avg_rating=report['avg_rating'],
                        unreplied=report.get('unreplied_count', 0),
                        report_url=f"https://zhiping.com/reports/{merchant.id}"
                    )
            
            logger.info("每日报告发送完成")
            
        except Exception as e:
            logger.error(f"发送每日报告失败：{str(e)}", exc_info=True)
        finally:
            db.close()
    
    async def sync_all_reviews(self):
        """同步所有商家评论"""
        logger.info("开始同步评论...")
        
        try:
            db = next(get_db())
            merchants = db.query(Merchant).filter(
                Merchant.status == True,
                Merchant.dianping_shop_id != None
            ).all()
            
            for merchant in merchants:
                try:
                    # 从大众点评同步
                    from app.services.dianping_service import dianping_service
                    
                    reviews = await dianping_service.batch_sync_reviews(
                        merchant.dianping_shop_id,
                        max_pages=2,
                        page_size=20
                    )
                    
                    if reviews:
                        # 保存到数据库
                        from app.models.review import Platform
                        ReviewService.batch_sync_reviews(
                            db,
                            merchant.id,
                            Platform.DIANPING,
                            reviews
                        )
                        
                        logger.info(f"商家 {merchant.shop_name} 同步 {len(reviews)} 条评论")
                    
                except Exception as e:
                    logger.error(f"同步商家 {merchant.shop_name} 评论失败：{str(e)}")
            
            logger.info("评论同步完成")
            
        except Exception as e:
            logger.error(f"同步评论失败：{str(e)}", exc_info=True)
        finally:
            db.close()


# 创建单例
task_scheduler = TaskScheduler()
