# FastAPI 核心应用
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import auth, reviews, replies, analytics, llm, dianping, subscription, multi_store
from app.utils.logger import setup_logger
from app.database import init_db
from app.services.task_scheduler import task_scheduler
import uvicorn

# 配置日志
logger = setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🚀 智评管家系统启动中...")
    await init_db()
    logger.info("✅ 数据库连接成功")
    
    # 启动定时任务
    task_scheduler.start()
    logger.info("✅ 定时任务已启动")
    
    yield
    
    # 关闭时执行
    logger.info("👋 智评管家系统关闭中...")
    task_scheduler.stop()

# 创建 FastAPI 应用
app = FastAPI(
    title="智评管家 - 商家评论管理系统",
    description="帮助商家高效管理真实用户评论，AI 智能回复，数据分析",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局异常：{exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误", "data": None}
    )

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    import time
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration:.3f}s"
    )
    
    return response

# 健康检查
@app.get("/health", tags=["健康检查"])
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": asyncio.get_event_loop().time()
    }

# 根路径
@app.get("/", tags=["根路径"])
async def root():
    return {
        "message": "欢迎使用智评管家 API",
        "docs": "/docs",
        "version": "1.0.0"
    }

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["评论管理"])
app.include_router(replies.router, prefix="/api/v1/replies", tags=["AI 回复"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["数据分析"])
app.include_router(llm.router, prefix="/api/v1/llm", tags=["LLM 管理"])
app.include_router(dianping.router, prefix="/api/v1/dianping", tags=["大众点评"])
app.include_router(subscription.router, prefix="/api/v1/subscription", tags=["订阅管理"])
app.include_router(multi_store.router, prefix="/api/v1/stores", tags=["多店管理"])

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
