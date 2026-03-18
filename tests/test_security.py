# 安全测试脚本
import requests
from typing import Dict, List

class SecurityTest:
    """安全测试工具"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.vulnerabilities: List[Dict] = []
    
    def test_sql_injection(self):
        """测试 SQL 注入"""
        print("\n🔍 测试 SQL 注入...")
        
        payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' AND '1'='1",
            "1' OR '1'='1' --",
            "admin'--"
        ]
        
        for payload in payloads:
            try:
                # 测试登录接口
                response = requests.post(
                    f"{self.base_url}/api/v1/auth/login",
                    json={"username": payload, "password": "test"}
                )
                
                # 检查是否有 SQL 错误信息
                if "sql" in response.text.lower() or "syntax" in response.text.lower():
                    self.vulnerabilities.append({
                        "type": "SQL Injection",
                        "endpoint": "/api/v1/auth/login",
                        "payload": payload,
                        "severity": "HIGH"
                    })
                    print(f"  ⚠️  发现潜在 SQL 注入：{payload}")
                
            except Exception as e:
                pass
        
        print("  ✅ SQL 注入测试完成")
    
    def test_xss(self):
        """测试 XSS 攻击"""
        print("\n🔍 测试 XSS 攻击...")
        
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>"
        ]
        
        for payload in payloads:
            try:
                # 测试注册接口
                response = requests.post(
                    f"{self.base_url}/api/v1/auth/register",
                    json={
                        "username": payload,
                        "password": "test123456",
                        "email": "test@example.com"
                    }
                )
                
                # 检查响应中是否包含 payload
                if payload in response.text:
                    self.vulnerabilities.append({
                        "type": "XSS",
                        "endpoint": "/api/v1/auth/register",
                        "payload": payload,
                        "severity": "HIGH"
                    })
                    print(f"  ⚠️  发现潜在 XSS：{payload}")
                
            except Exception as e:
                pass
        
        print("  ✅ XSS 测试完成")
    
    def test_authentication_bypass(self):
        """测试认证绕过"""
        print("\n🔍 测试认证绕过...")
        
        # 测试未授权访问
        protected_endpoints = [
            "/api/v1/auth/me",
            "/api/v1/reviews",
            "/api/v1/analytics/dashboard",
            "/api/v1/llm/providers"
        ]
        
        for endpoint in protected_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    self.vulnerabilities.append({
                        "type": "Authentication Bypass",
                        "endpoint": endpoint,
                        "severity": "CRITICAL"
                    })
                    print(f"  ⚠️  发现认证绕过：{endpoint}")
                elif response.status_code == 401:
                    print(f"  ✅ {endpoint} 需要认证")
                
            except Exception as e:
                pass
        
        print("  ✅ 认证绕过测试完成")
    
    def test_rate_limiting(self):
        """测试频率限制"""
        print("\n🔍 测试频率限制...")
        
        # 快速发送多个请求
        success_count = 0
        rate_limited_count = 0
        
        for i in range(20):
            try:
                response = requests.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 429:
                    rate_limited_count += 1
            except:
                pass
        
        if rate_limited_count > 0:
            print(f"  ✅ 频率限制生效：{rate_limited_count}/20 请求被限制")
        else:
            print(f"  ⚠️  未检测到频率限制：{success_count}/20 请求成功")
            self.vulnerabilities.append({
                "type": "No Rate Limiting",
                "endpoint": "/health",
                "severity": "MEDIUM"
            })
        
        print("  ✅ 频率限制测试完成")
    
    def test_sensitive_data_exposure(self):
        """测试敏感数据泄露"""
        print("\n🔍 测试敏感数据泄露...")
        
        # 检查错误信息是否泄露敏感数据
        try:
            # 访问不存在的接口
            response = requests.get(f"{self.base_url}/api/v1/nonexistent")
            
            if "traceback" in response.text.lower() or "stack" in response.text.lower():
                self.vulnerabilities.append({
                    "type": "Sensitive Data Exposure",
                    "endpoint": "/api/v1/nonexistent",
                    "severity": "MEDIUM"
                })
                print("  ⚠️  错误信息可能泄露敏感数据")
            else:
                print("  ✅ 错误信息处理良好")
        
        except Exception as e:
            pass
        
        print("  ✅ 敏感数据泄露测试完成")
    
    def test_cors(self):
        """测试 CORS 配置"""
        print("\n🔍 测试 CORS 配置...")
        
        try:
            response = requests.options(
                f"{self.base_url}/api/v1/auth/login",
                headers={
                    "Origin": "http://evil.com",
                    "Access-Control-Request-Method": "POST"
                }
            )
            
            # 检查是否允许任意来源
            if response.headers.get("Access-Control-Allow-Origin") == "*":
                print("  ⚠️  CORS 配置过于宽松（允许所有来源）")
                self.vulnerabilities.append({
                    "type": "Misconfigured CORS",
                    "endpoint": "Global",
                    "severity": "LOW"
                })
            else:
                print("  ✅ CORS 配置合理")
        
        except Exception as e:
            pass
        
        print("  ✅ CORS 测试完成")
    
    def run_all_tests(self):
        """运行所有安全测试"""
        print("=" * 80)
        print("🔒 安全测试开始")
        print("=" * 80)
        
        self.test_sql_injection()
        self.test_xss()
        self.test_authentication_bypass()
        self.test_rate_limiting()
        self.test_sensitive_data_exposure()
        self.test_cors()
        
        print("\n" + "=" * 80)
        print("📊 安全测试报告")
        print("=" * 80)
        
        if not self.vulnerabilities:
            print("✅ 未发现安全漏洞！")
        else:
            print(f"⚠️  发现 {len(self.vulnerabilities)} 个潜在安全问题:\n")
            
            for i, vuln in enumerate(self.vulnerabilities, 1):
                print(f"{i}. {vuln['type']}")
                print(f"   接口：{vuln['endpoint']}")
                print(f"   严重程度：{vuln['severity']}")
                if 'payload' in vuln:
                    print(f"   Payload: {vuln['payload']}")
                print()
        
        print("=" * 80)
        
        # 保存报告
        import json
        from datetime import datetime
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": self.vulnerabilities,
            "total_count": len(self.vulnerabilities),
            "by_severity": {
                "CRITICAL": sum(1 for v in self.vulnerabilities if v.get('severity') == 'CRITICAL'),
                "HIGH": sum(1 for v in self.vulnerabilities if v.get('severity') == 'HIGH'),
                "MEDIUM": sum(1 for v in self.vulnerabilities if v.get('severity') == 'MEDIUM'),
                "LOW": sum(1 for v in self.vulnerabilities if v.get('severity') == 'LOW')
            }
        }
        
        with open("security_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 报告已保存到：security_report.json")


if __name__ == "__main__":
    tester = SecurityTest()
    tester.run_all_tests()
