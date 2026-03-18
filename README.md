# 智评管家 - 商家评论管理系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/vue-3.4+-green.svg)](https://vuejs.org/)

**智评管家** 是一个帮助大众点评/美团商家高效管理真实用户评论的 SaaS 系统，提供 AI 智能回复、数据分析、多店管理等功能。

## ✨ 核心功能

- 📊 **多平台评论聚合** - 支持大众点评、美团、饿了么评论统一管理
- 🤖 **AI 智能回复** - 集成 6+ 个 LLM（通义千问、文心一言等），自动生成回复
- 📈 **深度数据分析** - 评分趋势、关键词提取、竞品分析、每日报告
- 🏪 **多店管理** - 支持连锁店，一键切换店铺
- 💳 **付费订阅** - 4 档订阅计划，完整的支付系统
- 🔔 **实时通知** - 微信消息推送，新评论实时提醒
- ⏰ **定时任务** - 自动同步评论、自动发送日报

## 🚀 快速开始

### 后端启动

```bash
# 克隆项目
git clone https://github.com/yourusername/zhiping-manager.git
cd zhiping-manager

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp config/.env.example .env
# 编辑 .env 文件，填写数据库和 API Key

# 启动 Docker（MySQL + Redis）
docker-compose up -d

# 初始化数据库
mysql -h 127.0.0.1 -u root -p < scripts/init_db.sql

# 启动应用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 访问 API 文档
open http://localhost:8000/docs
```

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问前端界面
open http://localhost:3000
```

## 📁 项目结构

```
zhiping-manager/
├── app/                          # 后端代码
│   ├── api/                      # API 路由
│   │   ├── auth.py              # 认证接口
│   │   ├── reviews.py           # 评论管理
│   │   ├── replies.py           # AI 回复
│   │   ├── analytics.py         # 数据分析
│   │   ├── llm.py               # LLM 管理
│   │   ├── dianping.py          # 大众点评
│   │   ├── subscription.py      # 订阅管理
│   │   └── multi_store.py       # 多店管理
│   ├── models/                   # 数据模型
│   ├── schemas/                  # Pydantic 模式
│   ├── services/                 # 业务服务
│   │   └── llm/                 # LLM 适配器
│   ├── utils/                    # 工具函数
│   ├── config.py                 # 配置管理
│   ├── database.py               # 数据库连接
│   └── main.py                   # 应用入口
├── frontend/                     # 前端代码
│   ├── src/
│   │   ├── views/               # 页面组件
│   │   ├── layouts/             # 布局组件
│   │   ├── router/              # 路由配置
│   │   ├── stores/              # 状态管理
│   │   └── utils/               # 工具函数
│   ├── package.json
│   └── vite.config.js
├── tests/                        # 测试文件
├── scripts/                      # 脚本文件
│   └── init_db.sql              # 数据库初始化
├── docker/                       # Docker 配置
│   ├── Dockerfile
│   └── docker-compose.yml
├── config/                       # 配置文件
│   └── .env.example             # 环境变量示例
├── docs/                         # 文档
├── requirements.txt              # Python 依赖
├── README.md                     # 项目说明
└── LICENSE                       # 许可证
```

## 🛠️ 技术栈

### 后端
- **FastAPI** - 高性能 Web 框架
- **SQLAlchemy** - ORM 框架
- **MySQL** - 数据库
- **Redis** - 缓存
- **Pydantic** - 数据验证
- **JWT** - 认证
- **APScheduler** - 定时任务

### 前端
- **Vue 3** - 前端框架
- **Element Plus** - UI 组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由
- **Axios** - HTTP 请求
- **ECharts** - 数据可视化
- **Vite** - 构建工具

### AI 集成
- **通义千问** - 阿里云
- **文心一言** - 百度
- **腾讯混元** - 腾讯
- 支持自定义扩展

## 📊 API 接口

项目包含 **35+ 个 API 接口**：

### 认证模块
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - Token 刷新
- `GET /api/v1/auth/me` - 获取用户信息

### 评论管理
- `GET /api/v1/reviews` - 评论列表
- `GET /api/v1/reviews/{id}` - 评论详情
- `PUT /api/v1/reviews/{id}/read` - 标记已读
- `POST /api/v1/reviews/sync` - 批量同步

### AI 回复
- `POST /api/v1/replies/generate` - 生成 AI 回复
- `POST /api/v1/replies/{id}/send` - 发送回复

### 数据分析
- `GET /api/v1/analytics/dashboard` - 仪表盘数据
- `GET /api/v1/analytics/rating-trend` - 评分趋势
- `GET /api/v1/analytics/keywords` - 关键词分析
- `GET /api/v1/analytics/competitor` - 竞品分析

### 订阅管理
- `POST /api/v1/subscription/orders` - 创建订单
- `GET /api/v1/subscription/subscription` - 获取订阅信息

### 多店管理
- `GET /api/v1/stores/stores` - 店铺列表
- `POST /api/v1/stores/stores` - 创建店铺
- `POST /api/v1/stores/stores/{id}/switch` - 切换店铺

完整 API 文档：http://localhost:8000/docs

## 🧪 测试

```bash
# 运行功能测试
pytest tests/test_full.py -v

# 运行性能测试
python tests/test_performance.py

# 运行安全测试
python tests/test_security.py

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 📄 文档

- [开发执行计划](docs/开发执行计划.md)
- [LLM 接口设计方案](docs/LLM 接口设计方案.md)
- [测试验收报告](docs/测试验收报告.md)
- [前端开发总结](docs/前端开发完成总结.md)
- [最终验收报告](docs/最终验收报告.md)

## 🔧 配置说明

复制环境变量模板并修改：

```bash
cp config/.env.example .env
```

需要配置的关键变量：

```bash
# 数据库
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password

# LLM API
QWEN_API_KEY=sk-xxx
ERNIE_API_KEY=xxx

# 大众点评
DIANPING_APP_KEY=xxx
DIANPING_APP_SECRET=xxx

# 微信
WECHAT_APP_ID=xxx
WECHAT_APP_SECRET=xxx
```

## 🚀 部署

### Docker 部署

```bash
# 构建镜像
docker-compose -f docker/docker-compose.yml build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 生产环境

参考 [部署指南](docs/部署指南.md)

## 📈 项目统计

| 指标 | 数量 |
|------|------|
| 文件数 | 52+ |
| 代码行数 | 20000+ |
| API 接口 | 35+ |
| 数据库表 | 12 张 |
| 测试用例 | 25+ |
| 前端页面 | 5 个 |

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 开发规范

- 遵循 [PEP 8](https://pep8.org/) 代码规范
- 使用类型注解
- 编写单元测试
- 提交信息清晰明了

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👥 作者

- **开发团队** - 智评管家团队
- **AI 助手** - 马上有钱

## 📞 联系方式

- 项目 Issues: https://github.com/yourusername/zhiping-manager/issues
- 邮箱：support@zhiping.com

## 🙏 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [ECharts](https://echarts.apache.org/)

---

**⭐ 如果这个项目对你有帮助，请给一个 Star！**

**📅 最后更新**: 2026-03-18
