
# GitHub 上传指南

## 📋 准备工作

### 1. 创建 GitHub 账号

如果没有 GitHub 账号，请先访问 https://github.com 注册

### 2. 创建 Personal Access Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 填写描述（如：zhiping-manager upload）
4. 选择权限：
   - ✅ repo (Full control of private repositories)
   - ✅ workflow (Update GitHub Action workflows)
5. 点击 "Generate token"
6. **重要**：复制并保存 Token（只会显示一次）

### 3. 在 GitHub 创建仓库

1. 访问 https://github.com/new
2. 仓库名称：`zhiping-manager`
3. 描述：智评管家 - 商家评论管理系统
4. 选择公开或私有
5. **不要**勾选 "Initialize this repository with a README"
6. 点击 "Create repository"

---

## 🚀 上传方法

### 方法一：使用上传脚本（推荐）

```bash
# 进入项目目录
cd /path/to/zhiping-manager

# 编辑脚本，修改 GitHub 用户名
nano scripts/upload_to_github.sh
# 将 yourusername 改为你的 GitHub 用户名

# 赋予执行权限
chmod +x scripts/upload_to_github.sh

# 运行脚本
./scripts/upload_to_github.sh
```

按提示输入：
1. 提交信息（如：Initial commit）
2. GitHub 用户名
3. Personal Access Token（代替密码）

### 方法二：手动上传

```bash
# 进入项目目录
cd /path/to/zhiping-manager

# 初始化 Git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: 智评管家项目"

# 添加远程仓库（替换 yourusername 为你的用户名）
git remote add origin https://github.com/yourusername/zhiping-manager.git

# 推送到 GitHub
git push -u origin main
```

推送时会提示输入用户名和密码：
- Username: 你的 GitHub 用户名
- Password: 使用 Personal Access Token（不是登录密码）

### 方法三：使用 GitHub Desktop

1. 下载并安装 GitHub Desktop: https://desktop.github.com
2. 打开应用，登录 GitHub 账号
3. File → Add Local Repository
4. 选择项目文件夹
5. 点击 "Publish repository"
6. 填写仓库信息
7. 点击 "Publish"

---

## ⚠️ 注意事项

### 1. 敏感信息

**绝对不要提交以下文件**：
- `.env` - 环境变量（包含密码和 API Key）
- `config/.env` - 配置文件
- `*.log` - 日志文件
- `*.db` - 数据库文件
- `secrets/` - 密钥文件夹

项目已配置 `.gitignore`，会自动忽略这些文件。

### 2. 大文件

如果文件超过 100MB，需要使用 Git LFS：

```bash
# 安装 Git LFS
git lfs install

# 跟踪大文件
git lfs track "*.zip"
git lfs track "*.tar.gz"

# 提交
git add .gitattributes
git commit -m "Configure Git LFS"
```

### 3. 分支管理

建议的分支策略：
- `main` - 主分支（生产环境）
- `develop` - 开发分支
- `feature/xxx` - 功能分支
- `bugfix/xxx` - 修复分支

---

## 🔧 常见问题

### 1. 推送失败：Permission denied

**原因**：认证失败

**解决**：
```bash
# 清除缓存的凭据
git credential-cache exit

# 重新配置
git config --global credential.helper store

# 再次推送
git push
```

### 2. 错误：Repository not found

**原因**：仓库不存在或 URL 错误

**解决**：
1. 确认已在 GitHub 创建仓库
2. 检查仓库 URL 是否正确
3. 确认有访问权限

### 3. 错误：Updates were rejected

**原因**：远程仓库有本地没有的提交

**解决**：
```bash
# 拉取远程更改
git pull origin main --allow-unrelated-histories

# 解决冲突（如果有）

# 再次推送
git push
```

### 4. 忘记提交 .env 文件

如果不小心提交了 `.env` 文件：

```bash
# 从 Git 历史中删除
git rm --cached .env
git commit -m "Remove .env from tracking"
git push

# 重要：立即更改 .env 中的所有密码和密钥！
```

---

## 📊 上传后验证

1. 访问 GitHub 仓库页面
2. 确认文件已上传
3. 检查 README 是否正确显示
4. 确认没有敏感文件

---

## 🎯 后续步骤

上传成功后：

1. **完善 README**
   - 添加项目截图
   - 更新安装说明
   - 添加演示链接

2. **设置 GitHub Pages**（可选）
   - Settings → Pages
   - 选择分支
   - 配置自定义域名

3. **添加 Issues 模板**
   - 创建 `.github/ISSUE_TEMPLATE/`
   - 添加 bug 报告和功能请求模板

4. **配置 GitHub Actions**（可选）
   - 自动测试
   - 自动部署
   - 自动发布

5. **邀请协作者**
   - Settings → Collaborators
   - 添加协作者

---

## 📞 需要帮助？

- GitHub 文档：https://docs.github.com
- Git 教程：https://git-scm.com/book
- 项目 Issues: https://github.com/yourusername/zhiping-manager/issues

---

**最后更新**: 2026-03-18

