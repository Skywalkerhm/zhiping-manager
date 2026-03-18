# GitHub 提交指南

## 📋 提交前检查清单

### ✅ 必查项目

- [ ] 所有代码文件已保存
- [ ] .env 文件未包含（已在 .gitignore 中）
- [ ] 敏感信息已移除
- [ ] README.md 已更新
- [ ] LICENSE 文件存在
- [ ] .gitignore 配置正确
- [ ] 所有测试通过

### ✅ 文档检查

- [ ] README.md - 项目说明
- [ ] LICENSE - 开源许可证
- [ ] .gitignore - Git 忽略配置
- [ ] docs/ - 完整文档目录

---

## 🚀 GitHub 提交流程

### 步骤 1: 在 GitHub 创建仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `zhiping-manager`
   - **Description**: `智评管家 - 商家评论管理系统 | Smart Review Manager for Dianping Merchants`
   - **Visibility**: 选择 Public 或 Private
   - **不要勾选** "Initialize this repository with a README"
3. 点击 "Create repository"

### 步骤 2: 配置 Git 用户信息

```bash
# 配置 Git 用户名和邮箱（首次使用）
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 验证配置
git config --list
```

### 步骤 3: 初始化本地仓库

```bash
# 进入项目目录
cd /path/to/zhiping-manager

# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 查看状态
git status
```

### 步骤 4: 首次提交

```bash
# 提交代码
git commit -m "Initial commit: 智评管家项目 v1.0.0

- 完整的后端 API（35 个接口）
- 前端界面（5 个页面，大众点评风格）
- 数据库设计（12 张表）
- 测试套件（功能/性能/安全）
- 完整文档（13 个）
- 支持多 LLM（通义/文心/腾讯）
- 支付系统和多店管理
- 定时任务和微信推送"
```

### 步骤 5: 关联远程仓库

```bash
# 添加远程仓库（替换 yourusername 为你的 GitHub 用户名）
git remote add origin https://github.com/yourusername/zhiping-manager.git

# 验证远程仓库
git remote -v
```

### 步骤 6: 推送到 GitHub

```bash
# 重命名分支为 main
git branch -M main

# 推送到 GitHub
git push -u origin main
```

**输入认证信息**：
- Username: 你的 GitHub 用户名
- Password: 使用 Personal Access Token（不是登录密码）

---

## 🔑 获取 Personal Access Token

### 创建 Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 填写信息：
   - **Note**: `zhiping-manager upload`
   - **Expiration**: 选择过期时间（建议 90 天）
   - **Select scopes**: 勾选以下权限：
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (Update GitHub Action workflows)
     - ✅ `write:packages` (Upload packages to GitHub Package Registry)
4. 点击 "Generate token"
5. **重要**：复制并保存 Token（只显示一次！）

### 使用 Token

推送时使用 Token 代替密码：
```
Username: yourusername
Password: ghp_xxxxxxxxxxxxxxxxxxxx (你的 Token)
```

---

## 📝 提交规范

### Commit Message 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式（不影响代码运行）
- `refactor`: 重构（既不是新功能也不是 bug 修复）
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

### 示例

```bash
# 新功能
git commit -m "feat(auth): 添加用户注册和登录功能"

# 修复 bug
git commit -m "fix(api): 修复评论列表分页错误"

# 文档更新
git commit -m "docs(readme): 更新安装说明"

# 性能优化
git commit -m "perf(database): 优化数据库查询性能"
```

---

## 🔄 后续提交

### 日常开发提交

```bash
# 查看变更
git status

# 添加变更
git add .

# 或添加特定文件
git add app/api/reviews.py
git add frontend/src/views/Dashboard.vue

# 提交
git commit -m "feat(reviews): 添加评论筛选功能"

# 推送
git push origin main
```

### 批量提交

```bash
# 添加所有变更
git add .

# 提交
git commit -m "chore: 更新项目文档和配置"

# 推送
git push origin main
```

---

## 📊 项目统计信息

### 代码规模

```bash
# 统计代码行数
find . -name "*.py" -o -name "*.vue" -o -name "*.js" | xargs wc -l

# 查看文件数量
find . -type f | wc -l
```

### 提交统计

```bash
# 查看提交历史
git log --oneline

# 查看贡献统计
git shortlog -sn

# 查看文件变更
git diff --stat
```

---

## ⚠️ 注意事项

### 不要提交的文件

以下文件已在 `.gitignore` 中配置，**切勿手动添加**：

```
❌ .env                    # 环境变量（含密码）
❌ config/.env            # 配置文件
❌ *.log                  # 日志文件
❌ *.db                   # 数据库文件
❌ venv/                  # Python 虚拟环境
❌ node_modules/          # Node 依赖
❌ __pycache__/           # Python 缓存
❌ .DS_Store              # macOS 系统文件
❌ *.pyc                  # Python 编译文件
```

### 敏感信息处理

如果不小心提交了敏感文件：

```bash
# 1. 从 Git 历史中删除
git rm --cached .env
git commit -m "Remove sensitive .env file"
git push

# 2. 立即更改所有密码和 API Key！
# 3. 添加文件到 .gitignore
```

### 大文件处理

如果文件超过 100MB，使用 Git LFS：

```bash
# 安装 Git LFS
git lfs install

# 跟踪大文件
git lfs track "*.zip"
git lfs track "*.tar.gz"
git lfs track "frontend/dist/*"

# 提交 .gitattributes
git add .gitattributes
git commit -m "Configure Git LFS for large files"
```

---

## 🎯 上传后验证

### 1. 检查 GitHub 仓库

访问：`https://github.com/yourusername/zhiping-manager`

确认：
- ✅ 所有文件已上传
- ✅ README 正确显示
- ✅ 文件结构清晰
- ✅ 无敏感文件

### 2. 检查文件完整性

```bash
# 关键文件列表
ls -la README.md LICENSE .gitignore
ls -la app/main.py
ls -la frontend/src/views/
ls -la docs/
```

### 3. 测试克隆

```bash
# 在新目录测试克隆
cd /tmp
git clone https://github.com/yourusername/zhiping-manager.git
cd zhiping-manager

# 验证文件
ls -la
```

---

## 📋 推荐的 GitHub 配置

### 1. 添加 Topics

在仓库页面：
- Settings → General → Topics
- 添加：`fastapi` `vue` `dianping` `review-management` `ai` `llm` `python` `saas`

### 2. 设置默认分支

- Settings → Branches
- Default branch: `main`
- 添加分支保护规则

### 3. 添加 Issues 模板

创建 `.github/ISSUE_TEMPLATE/bug_report.md` 和 `feature_request.md`

### 4. 配置 GitHub Actions

创建 `.github/workflows/ci.yml` 实现自动测试

---

## 🚨 常见问题

### 1. 推送失败：Permission denied

**原因**: 认证失败

**解决**:
```bash
# 清除缓存的凭据
git credential-cache exit

# 重新配置
git config --global credential.helper store

# 再次推送，使用 Token
git push
```

### 2. 错误：Repository not found

**原因**: 仓库不存在或 URL 错误

**解决**:
1. 确认已在 GitHub 创建仓库
2. 检查仓库 URL 是否正确
3. 确认有访问权限

### 3. 错误：Updates were rejected

**原因**: 远程仓库有本地没有的提交

**解决**:
```bash
# 拉取远程更改
git pull origin main --allow-unrelated-histories

# 解决冲突（如果有）
# 再次推送
git push
```

### 4. Token 过期

**解决**:
1. 重新生成 Token
2. 更新本地凭据
```bash
git credential-cache exit
# 重新推送，使用新 Token
```

---

## 📞 需要帮助？

- **GitHub 文档**: https://docs.github.com
- **Git 教程**: https://git-scm.com/book
- **项目 Issues**: https://github.com/yourusername/zhiping-manager/issues

---

## 📄 相关文档

- [README.md](../README.md) - 项目说明
- [部署指南.md](部署指南.md) - 生产环境部署
- [GitHub 上传指南.md](GitHub 上传指南.md) - 上传步骤
- [开发完成总结.md](开发完成总结.md) - 开发总结

---

**最后更新**: 2026-03-18  
**文档版本**: v1.0  
**项目状态**: 🟢 可提交 GitHub
