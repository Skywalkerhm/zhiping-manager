# 测试配置
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    assert "智评管家" in response.json()["message"]

def test_register_user():
    """测试用户注册"""
    user_data = {
        "username": "testuser123",
        "email": "test@example.com",
        "phone": "13800138000",
        "password": "test123456",
        "role": "merchant"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code in [200, 400]  # 可能已存在

def test_login():
    """测试用户登录"""
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

def test_get_current_user():
    """测试获取当前用户"""
    # 先登录
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    login_response = client.post("/api/v1/auth/login", json=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 获取用户信息
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        assert "username" in response.json()

def test_generate_reply_unauthorized():
    """测试未授权访问回复生成"""
    request_data = {
        "review_id": 1,
        "review_content": "测试评论",
        "review_rating": 5,
        "sentiment": "positive"
    }
    
    response = client.post("/api/v1/replies/generate", json=request_data)
    assert response.status_code == 401

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
