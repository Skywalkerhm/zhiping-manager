# 测试配置
import pytest

@pytest.fixture
def test_db():
    """测试数据库夹具"""
    # TODO: 实现测试数据库设置
    pass

@pytest.fixture
def test_user():
    """测试用户夹具"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "test123456"
    }

@pytest.fixture
def test_merchant():
    """测试商家夹具"""
    return {
        "shop_name": "测试餐厅",
        "shop_type": "餐饮"
    }
