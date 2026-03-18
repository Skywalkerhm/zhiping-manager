-- 智评管家数据库初始化脚本
-- MySQL 8.0+
-- 创建时间：2026-03-17

-- 创建数据库
CREATE DATABASE IF NOT EXISTS zhiping_manager 
DEFAULT CHARACTER SET utf8mb4 
DEFAULT COLLATE utf8mb4_unicode_ci;

USE zhiping_manager;

-- ============================================
-- 1. 用户表
-- ============================================
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE COMMENT '邮箱',
    phone VARCHAR(20) UNIQUE COMMENT '手机号',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    role ENUM('admin', 'merchant', 'staff') DEFAULT 'merchant' COMMENT '角色',
    status TINYINT DEFAULT 1 COMMENT '状态：1-正常 0-禁用',
    avatar_url VARCHAR(255) COMMENT '头像 URL',
    last_login_at DATETIME COMMENT '最后登录时间',
    last_login_ip VARCHAR(50) COMMENT '最后登录 IP',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_phone (phone),
    INDEX idx_email (email),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================
-- 2. 商家表
-- ============================================
CREATE TABLE merchants (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL COMMENT '所属用户 ID',
    shop_name VARCHAR(100) NOT NULL COMMENT '店铺名称',
    shop_type VARCHAR(50) COMMENT '店铺类型：餐饮/美容/娱乐等',
    shop_category VARCHAR(100) COMMENT '店铺分类',
    address VARCHAR(255) COMMENT '地址',
    city VARCHAR(50) COMMENT '城市',
    district VARCHAR(50) COMMENT '区域',
    latitude DECIMAL(10, 8) COMMENT '纬度',
    longitude DECIMAL(11, 8) COMMENT '经度',
    phone VARCHAR(20) COMMENT '联系电话',
    dianping_shop_id VARCHAR(50) COMMENT '大众点评店铺 ID',
    meituan_shop_id VARCHAR(50) COMMENT '美团店铺 ID',
    eleme_shop_id VARCHAR(50) COMMENT '饿了么店铺 ID',
    authorization_token TEXT COMMENT '平台授权 Token',
    authorization_expire DATETIME COMMENT '授权过期时间',
    subscription_plan ENUM('free', 'pro', 'premium', 'enterprise') DEFAULT 'free' COMMENT '订阅计划',
    subscription_start DATE COMMENT '订阅开始日期',
    subscription_expire DATE COMMENT '订阅过期日期',
    total_reviews INT DEFAULT 0 COMMENT '总评论数',
    avg_rating DECIMAL(3, 2) DEFAULT 0.00 COMMENT '平均评分',
    status TINYINT DEFAULT 1 COMMENT '状态：1-正常 0-禁用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_dianping_id (dianping_shop_id),
    INDEX idx_meituan_id (meituan_shop_id),
    INDEX idx_shop_type (shop_type),
    INDEX idx_city (city),
    INDEX idx_status (status),
    INDEX idx_subscription (subscription_plan, subscription_expire)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商家表';

-- ============================================
-- 3. 评论表
-- ============================================
CREATE TABLE reviews (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    merchant_id BIGINT NOT NULL COMMENT '商家 ID',
    review_id VARCHAR(50) UNIQUE NOT NULL COMMENT '平台评论 ID',
    platform ENUM('dianping', 'meituan', 'eleme') DEFAULT 'dianping' COMMENT '来源平台',
    user_name VARCHAR(50) COMMENT '用户昵称（脱敏）',
    user_avatar VARCHAR(255) COMMENT '用户头像',
    rating TINYINT NOT NULL COMMENT '评分 1-5',
    content TEXT NOT NULL COMMENT '评论内容',
    images JSON COMMENT '图片 URL 列表',
    review_time DATETIME COMMENT '评论时间',
    sentiment ENUM('positive', 'neutral', 'negative') DEFAULT 'neutral' COMMENT '情感分类',
    sentiment_score DECIMAL(5, 4) COMMENT '情感得分 -1 到 1',
    topics JSON COMMENT '主题标签 ["菜品", "服务", "环境"]',
    is_replied TINYINT DEFAULT 0 COMMENT '是否已回复 0-否 1-是',
    reply_content TEXT COMMENT '回复内容',
    reply_time DATETIME COMMENT '回复时间',
    replied_by BIGINT COMMENT '回复人 ID',
    is_read TINYINT DEFAULT 0 COMMENT '是否已读',
    is_flagged TINYINT DEFAULT 0 COMMENT '是否标记（需重点关注）',
    flag_reason VARCHAR(100) COMMENT '标记原因',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE,
    INDEX idx_merchant_id (merchant_id),
    INDEX idx_review_id (review_id),
    INDEX idx_platform (platform),
    INDEX idx_rating (rating),
    INDEX idx_sentiment (sentiment),
    INDEX idx_review_time (review_time),
    INDEX idx_is_replied (is_replied),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at),
    INDEX idx_merchant_time (merchant_id, review_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评论表';

-- ============================================
-- 4. LLM 提供商配置表
-- ============================================
CREATE TABLE llm_providers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    provider_code VARCHAR(50) UNIQUE NOT NULL COMMENT '提供商代码',
    provider_name VARCHAR(100) NOT NULL COMMENT '提供商名称',
    api_base_url VARCHAR(255) COMMENT 'API 基础 URL',
    api_key VARCHAR(255) COMMENT 'API Key',
    secret_key VARCHAR(255) COMMENT 'Secret Key（部分厂商需要）',
    models JSON COMMENT '支持的模型列表',
    is_enabled TINYINT DEFAULT 1 COMMENT '是否启用',
    priority INT DEFAULT 0 COMMENT '优先级，数字越小优先级越高',
    rate_limit INT DEFAULT 100 COMMENT '每分钟请求限制',
    daily_quota INT DEFAULT 10000 COMMENT '每日配额',
    daily_used INT DEFAULT 0 COMMENT '今日已用',
    cost_per_1k_tokens DECIMAL(10, 6) DEFAULT 0.000000 COMMENT '每千 token 成本',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_enabled_priority (is_enabled, priority),
    INDEX idx_provider_code (provider_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='LLM 提供商配置表';

-- 插入默认 LLM 配置
INSERT INTO llm_providers (provider_code, provider_name, api_base_url, models, is_enabled, priority, cost_per_1k_tokens) VALUES
('aliyun_qwen', '通义千问', 'https://dashscope.aliyuncs.com/api/v1', 
 '[{"name": "qwen-turbo", "cost": 0.002}, {"name": "qwen-plus", "cost": 0.004}, {"name": "qwen-max", "cost": 0.012}]', 
 1, 0, 0.002),
('baidu_ernie', '文心一言', 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat',
 '[{"name": "ernie-bot-4", "cost": 0.003}, {"name": "ernie-bot-turbo", "cost": 0.001}]',
 1, 1, 0.003),
('tencent_hunyuan', '腾讯混元', 'https://hunyuan.tencentcloudapi.com',
 '[{"name": "hunyuan-pro", "cost": 0.0025}]',
 1, 2, 0.0025);

-- ============================================
-- 5. 商家 LLM 设置表
-- ============================================
CREATE TABLE merchant_llm_settings (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    merchant_id BIGINT UNIQUE NOT NULL COMMENT '商家 ID',
    preferred_provider VARCHAR(50) DEFAULT 'aliyun_qwen' COMMENT '首选 LLM 提供商',
    preferred_model VARCHAR(50) DEFAULT 'qwen-turbo' COMMENT '首选模型',
    auto_switch_enabled TINYINT DEFAULT 1 COMMENT '是否启用自动切换',
    temperature DECIMAL(3, 2) DEFAULT 0.70 COMMENT '温度参数',
    max_tokens INT DEFAULT 500 COMMENT '最大输出 token',
    custom_system_prompt TEXT COMMENT '自定义系统提示词',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE,
    INDEX idx_merchant_id (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商家 LLM 设置表';

-- ============================================
-- 6. AI 回复记录表
-- ============================================
CREATE TABLE ai_replies (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    review_id BIGINT NOT NULL COMMENT '评论 ID',
    original_content TEXT COMMENT '原始回复内容',
    ai_generated TEXT NOT NULL COMMENT 'AI 生成内容',
    final_content TEXT COMMENT '最终发送内容',
    prompt_used TEXT COMMENT '使用的 Prompt',
    system_prompt TEXT COMMENT '系统提示词',
    llm_provider VARCHAR(50) COMMENT '使用的 LLM 提供商',
    llm_model VARCHAR(50) COMMENT '使用的模型',
    prompt_tokens INT DEFAULT 0 COMMENT '输入 token 数',
    completion_tokens INT DEFAULT 0 COMMENT '输出 token 数',
    total_tokens INT DEFAULT 0 COMMENT '总 token 数',
    cost DECIMAL(10, 6) DEFAULT 0.000000 COMMENT '成本',
    latency_ms INT DEFAULT 0 COMMENT '响应时间 (ms)',
    status ENUM('draft', 'pending', 'sent', 'rejected') DEFAULT 'draft' COMMENT '状态',
    request_id VARCHAR(100) COMMENT 'LLM 请求 ID',
    error_message TEXT COMMENT '错误信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at DATETIME COMMENT '发送时间',
    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE,
    INDEX idx_review_id (review_id),
    INDEX idx_status (status),
    INDEX idx_llm_provider (llm_provider),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI 回复记录表';

-- ============================================
-- 7. LLM 使用日志表
-- ============================================
CREATE TABLE llm_usage_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    merchant_id BIGINT NOT NULL COMMENT '商家 ID',
    provider_code VARCHAR(50) NOT NULL COMMENT 'LLM 提供商代码',
    model VARCHAR(50) NOT NULL COMMENT '模型名称',
    request_id VARCHAR(100) COMMENT '请求 ID',
    review_id BIGINT COMMENT '关联评论 ID',
    prompt_tokens INT DEFAULT 0,
    completion_tokens INT DEFAULT 0,
    total_tokens INT DEFAULT 0,
    cost DECIMAL(10, 6) DEFAULT 0.000000,
    latency_ms INT DEFAULT 0,
    status ENUM('success', 'failed', 'timeout') DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_merchant_time (merchant_id, created_at),
    INDEX idx_provider (provider_code),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='LLM 使用日志表';

-- ============================================
-- 8. 操作日志表
-- ============================================
CREATE TABLE operation_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL COMMENT '操作用户 ID',
    merchant_id BIGINT COMMENT '关联商家 ID',
    action VARCHAR(50) NOT NULL COMMENT '操作类型',
    resource_type VARCHAR(50) COMMENT '资源类型',
    resource_id BIGINT COMMENT '资源 ID',
    old_value JSON COMMENT '旧值',
    new_value JSON COMMENT '新值',
    ip_address VARCHAR(50) COMMENT 'IP 地址',
    user_agent VARCHAR(255) COMMENT 'User-Agent',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_time (user_id, created_at),
    INDEX idx_action (action),
    INDEX idx_merchant (merchant_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表';

-- ============================================
-- 9. 订阅订单表
-- ============================================
CREATE TABLE subscription_orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    merchant_id BIGINT NOT NULL COMMENT '商家 ID',
    order_no VARCHAR(50) UNIQUE NOT NULL COMMENT '订单号',
    plan_type ENUM('free', 'pro', 'premium', 'enterprise') NOT NULL COMMENT '计划类型',
    amount DECIMAL(10, 2) NOT NULL COMMENT '金额',
    currency VARCHAR(10) DEFAULT 'CNY' COMMENT '货币',
    payment_method VARCHAR(50) COMMENT '支付方式',
    payment_status ENUM('pending', 'paid', 'failed', 'refunded') DEFAULT 'pending',
    payment_time DATETIME COMMENT '支付时间',
    start_date DATE COMMENT '开始日期',
    end_date DATE COMMENT '结束日期',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE,
    INDEX idx_merchant_id (merchant_id),
    INDEX idx_order_no (order_no),
    INDEX idx_payment_status (payment_status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订阅订单表';

-- ============================================
-- 10. 通知配置表
-- ============================================
CREATE TABLE notification_settings (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    merchant_id BIGINT UNIQUE NOT NULL COMMENT '商家 ID',
    wechat_enabled TINYINT DEFAULT 1 COMMENT '是否启用微信通知',
    wechat_openid VARCHAR(100) COMMENT '微信 OpenID',
    sms_enabled TINYINT DEFAULT 0 COMMENT '是否启用短信通知',
    sms_phone VARCHAR(20) COMMENT '短信手机号',
    email_enabled TINYINT DEFAULT 0 COMMENT '是否启用邮件通知',
    email_address VARCHAR(100) COMMENT '邮箱地址',
    notify_negative_only TINYINT DEFAULT 0 COMMENT '仅通知差评',
    notify_realtime TINYINT DEFAULT 1 COMMENT '实时通知',
    notify_summary_daily TINYINT DEFAULT 0 COMMENT '每日汇总',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE,
    INDEX idx_merchant_id (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='通知配置表';

-- ============================================
-- 初始化测试数据
-- ============================================

-- 创建管理员账号（密码：admin123，实际使用需哈希）
INSERT INTO users (username, email, phone, password_hash, role, status) VALUES
('admin', 'admin@zhiping.com', '13800138000', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu', 'admin', 1);

-- 创建测试商家
INSERT INTO merchants (user_id, shop_name, shop_type, shop_category, city, district, subscription_plan, status) VALUES
(1, '测试餐厅', '餐饮', '中餐', '上海', '浦东新区', 'pro', 1);

-- 创建商家 LLM 设置
INSERT INTO merchant_llm_settings (merchant_id, preferred_provider, preferred_model) VALUES
(1, 'aliyun_qwen', 'qwen-turbo');

-- 创建通知配置
INSERT INTO notification_settings (merchant_id, wechat_enabled, notify_realtime) VALUES
(1, 1, 1);

-- ============================================
-- 视图：评论统计
-- ============================================
CREATE OR REPLACE VIEW v_merchant_stats AS
SELECT 
    m.id AS merchant_id,
    m.shop_name,
    COUNT(r.id) AS total_reviews,
    AVG(r.rating) AS avg_rating,
    SUM(CASE WHEN r.sentiment = 'positive' THEN 1 ELSE 0 END) AS positive_count,
    SUM(CASE WHEN r.sentiment = 'neutral' THEN 1 ELSE 0 END) AS neutral_count,
    SUM(CASE WHEN r.sentiment = 'negative' THEN 1 ELSE 0 END) AS negative_count,
    SUM(CASE WHEN r.is_replied = 1 THEN 1 ELSE 0 END) AS replied_count,
    SUM(CASE WHEN r.is_replied = 0 THEN 1 ELSE 0 END) AS unreplied_count
FROM merchants m
LEFT JOIN reviews r ON m.id = r.merchant_id
WHERE m.status = 1
GROUP BY m.id, m.shop_name;

-- ============================================
-- 存储过程：更新商家统计
-- ============================================
DELIMITER $$
CREATE PROCEDURE update_merchant_stats(IN p_merchant_id BIGINT)
BEGIN
    UPDATE merchants m
    SET 
        m.total_reviews = (SELECT COUNT(*) FROM reviews r WHERE r.merchant_id = m.id),
        m.avg_rating = (SELECT COALESCE(AVG(r.rating), 0) FROM reviews r WHERE r.merchant_id = m.id)
    WHERE m.id = p_merchant_id;
END$$
DELIMITER ;

-- ============================================
-- 完成提示
-- ============================================
SELECT '数据库初始化完成！' AS message;
