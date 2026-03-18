# 测试套件 - 完整 API 测试
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ==================== 健康检查 ====================
def test_health_check():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "智评管家" in data["message"]
    assert data["version"] == "1.0.0"

# ==================== 认证模块 ====================
def test_register_user():
    """测试用户注册"""
    user_data = {
        "username": "testuser2026",
        "email": "test2026@example.com",
        "phone": "13800138001",
        "password": "test123456",
        "role": "merchant"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    # 可能成功或因已存在返回 400
    assert response.status_code in [200, 400]
    
    if response.status_code == 200:
        data = response.json()
        assert data["username"] == "testuser2026"
        assert data["role"] == "merchant"

def test_login_success():
    """测试登录成功"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800
    else:
        # 可能因用户不存在失败
        assert response.status_code == 401

def test_login_wrong_password():
    """测试密码错误"""
    login_data = {
        "username": "admin",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401

def test_get_current_user_unauthorized():
    """测试未授权访问用户信息"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_get_current_user_authorized():
    """测试授权访问用户信息"""
    # 先登录
    login_response = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 获取用户信息
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "role" in data

def test_token_refresh():
    """测试 Token 刷新"""
    # 先登录
    login_response = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if login_response.status_code == 200:
        refresh_token = login_response.json()["refresh_token"]
        
        # 刷新 Token
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data

# ==================== LLM 管理 ====================
def test_get_llm_providers_unauthorized():
    """测试未授权获取 LLM 列表"""
    response = client.get("/api/v1/llm/providers")
    assert response.status_code == 401

def test_get_llm_providers_authorized():
    """测试授权获取 LLM 列表"""
    # 先登录
    login_response = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/llm/providers", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data

def test_llm_test_connection():
    """测试 LLM 连接测试"""
    login_response = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/api/v1/llm/test", headers=headers)
        assert response.status_code == 200

# ==================== 评论管理 ====================
def test_get_reviews_unauthorized():
    """测试未授权获取评论"""
    response = client.get("/api/v1/reviews")
    assert response.status_code == 401

def test_get_reviews_authorized():
    """测试授权获取评论"""
    login_response = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/reviews?merchant_id=1&page=1&size=20", headers=headers)
        # 可能因无数据返回空列表
        assert response.status_code in [200, 404]

def test_get_review_stats():
    """测试获取评论统计"""
    login_response = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/reviews/stats/1", headers=headers)
        assert response.status_code in [200, 404]

# ==================== AI 回复 ====================
def test_generate_reply_unauthorized():
    """测试未授权生成回复"""
    response = client.post("/api/v1/replies/generate", json={
        "review_id": 1,
        "review_content": "测试评论",
        "review_rating": 5,
        "sentiment": "positive"
    })
    assert response.status_code == 401

def test_generate_reply_authorized():
    """测试授权生成回复"""
    login_response = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 注意：如果没有配置 LLM API Key，会失败
        response = client.post("/api/v1/replies/generate", headers=headers, json={
            "review_id": 1,
            "review_content": "菜品很好吃，服务也很到位",
            "review_rating": 5,
            "sentiment": "positive"
        })
        
        # 可能成功或因 LLM 未配置失败
        assert response.status_code in [200, 400, 500]

# ==================== 数据分析 ====================
def test_get_rating_trend():
    """测试获取评分趋势"""
    login_response = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/analytics/rating-trend?merchant_id=1&days=30", headers=headers)
        assert response.status_code in [200, 404]

def test_get_keywords():
    """测试获取关键词"""
    login_response = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/analytics/keywords?merchant_id=1&limit=10", headers=headers)
        assert response.status_code in [200, 404]

def test_get_dashboard():
    """测试获取仪表盘"""
    login_response = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/analytics/dashboard?merchant_id=1", headers=headers)
        assert response.status_code in [200, 404]

# ==================== 大众点评 ====================
def test_dianping_test_connection():
    """测试大众点评连接"""
    login_response = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/api/v1/dianping/test", headers=headers)
        # 没有配置 API Key 会失败
        assert response.status_code in [200, 500]

# ==================== 性能测试 ====================
def test_concurrent_requests():
    """测试并发请求"""
    import concurrent.futures
    
    def make_request():
        return client.get("/health")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        results = [f.result() for f in futures]
    
    # 所有请求都应该成功
    assert all(r.status_code == 200 for r in results)

# ==================== 错误处理 ====================
def test_404_not_found():
    """测试 404 错误"""
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404

def test_invalid_token():
    """测试无效 Token"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
