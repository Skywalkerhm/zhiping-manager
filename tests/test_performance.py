# 性能测试脚本
import time
import asyncio
import aiohttp
from typing import List, Dict
from datetime import datetime

class PerformanceTest:
    """性能测试工具"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[Dict] = []
    
    async def test_endpoint(
        self,
        session: aiohttp.ClientSession,
        method: str,
        endpoint: str,
        headers: Dict = None,
        json_data: Dict = None,
        concurrency: int = 1
    ) -> Dict:
        """测试单个接口"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        tasks = []
        for _ in range(concurrency):
            if method.upper() == "GET":
                task = session.get(url, headers=headers)
            elif method.upper() == "POST":
                task = session.post(url, headers=headers, json=json_data)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 统计结果
        success_count = sum(1 for r in responses if not isinstance(r, Exception))
        failed_count = len(responses) - success_count
        
        result = {
            "endpoint": endpoint,
            "method": method,
            "concurrency": concurrency,
            "total_requests": len(responses),
            "success": success_count,
            "failed": failed_count,
            "duration_seconds": round(duration, 3),
            "requests_per_second": round(len(responses) / duration, 2) if duration > 0 else 0,
            "avg_response_time_ms": round((duration / len(responses)) * 1000, 2)
        }
        
        self.results.append(result)
        return result
    
    async def run_all_tests(self, token: str = None):
        """运行所有性能测试"""
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        async with aiohttp.ClientSession() as session:
            print("\n🚀 开始性能测试...\n")
            
            # 1. 健康检查（高并发）
            print("1. 测试健康检查接口（并发 50）...")
            await self.test_endpoint(session, "GET", "/health", concurrency=50)
            
            # 2. 获取评论列表
            print("2. 测试评论列表接口（并发 20）...")
            await self.test_endpoint(
                session, "GET",
                "/api/v1/reviews?merchant_id=1&page=1&size=20",
                headers=headers,
                concurrency=20
            )
            
            # 3. 获取评论统计
            print("3. 测试评论统计接口（并发 20）...")
            await self.test_endpoint(
                session, "GET",
                "/api/v1/reviews/stats/1",
                headers=headers,
                concurrency=20
            )
            
            # 4. 获取评分趋势
            print("4. 测试评分趋势接口（并发 20）...")
            await self.test_endpoint(
                session, "GET",
                "/api/v1/analytics/rating-trend?merchant_id=1&days=30",
                headers=headers,
                concurrency=20
            )
            
            # 5. 获取关键词
            print("5. 测试关键词接口（并发 20）...")
            await self.test_endpoint(
                session, "GET",
                "/api/v1/analytics/keywords?merchant_id=1&limit=10",
                headers=headers,
                concurrency=20
            )
            
            # 6. 获取仪表盘
            print("6. 测试仪表盘接口（并发 20）...")
            await self.test_endpoint(
                session, "GET",
                "/api/v1/analytics/dashboard?merchant_id=1",
                headers=headers,
                concurrency=20
            )
            
            # 7. 获取 LLM 列表
            print("7. 测试 LLM 列表接口（并发 20）...")
            await self.test_endpoint(
                session, "GET",
                "/api/v1/llm/providers",
                headers=headers,
                concurrency=20
            )
            
            print("\n✅ 性能测试完成！\n")
    
    def print_report(self):
        """打印测试报告"""
        print("=" * 80)
        print("📊 性能测试报告")
        print("=" * 80)
        print(f"{'接口':<40} {'并发':<8} {'成功':<8} {'失败':<8} {'QPS':<10} {'平均响应':<10}")
        print("-" * 80)
        
        for result in self.results:
            print(
                f"{result['endpoint']:<40} "
                f"{result['concurrency']:<8} "
                f"{result['success']:<8} "
                f"{result['failed']:<8} "
                f"{result['requests_per_second']:<10} "
                f"{result['avg_response_time_ms']}ms"
            )
        
        print("=" * 80)
        
        # 总体统计
        total_requests = sum(r['total_requests'] for r in self.results)
        total_success = sum(r['success'] for r in self.results)
        total_failed = sum(r['failed'] for r in self.results)
        total_duration = sum(r['duration_seconds'] for r in self.results)
        
        print(f"\n总体统计:")
        print(f"  总请求数：{total_requests}")
        print(f"  成功：{total_success}")
        print(f"  失败：{total_failed}")
        print(f"  成功率：{total_success/total_requests*100:.2f}%" if total_requests > 0 else "N/A")
        print(f"  总耗时：{total_duration:.2f}秒")
        print(f"  平均 QPS: {total_requests/total_duration:.2f}" if total_duration > 0 else "N/A")
        print("=" * 80)


async def main():
    """主函数"""
    # 先登录获取 Token
    async with aiohttp.ClientSession() as session:
        login_response = await session.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        
        if login_response.status == 200:
            login_data = await login_response.json()
            token = login_data.get("access_token")
            print(f"✅ 登录成功，Token: {token[:20]}...")
        else:
            print("⚠️  登录失败，将使用未授权模式测试")
            token = None
    
    # 运行性能测试
    tester = PerformanceTest()
    await tester.run_all_tests(token)
    
    # 打印报告
    tester.print_report()
    
    # 保存报告
    import json
    report = {
        "timestamp": datetime.now().isoformat(),
        "results": tester.results
    }
    
    with open("performance_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 报告已保存到：performance_report.json")


if __name__ == "__main__":
    asyncio.run(main())
