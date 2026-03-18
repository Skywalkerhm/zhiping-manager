#!/bin/bash

# GitHub 上传脚本
# 用于将项目推送到 GitHub

# 配置
GITHUB_USERNAME="yourusername"  # 替换为你的 GitHub 用户名
REPO_NAME="zhiping-manager"
GITHUB_REPO="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}   智评管家 - GitHub 上传脚本${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""

# 检查 Git 是否安装
if ! command -v git &> /dev/null; then
    echo -e "${RED}错误：Git 未安装，请先安装 Git${NC}"
    exit 1
fi

# 检查是否在正确的目录
if [ ! -f "README.md" ]; then
    echo -e "${RED}错误：请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 检查是否已初始化 Git
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}初始化 Git 仓库...${NC}"
    git init
fi

# 添加远程仓库（如果不存在）
if ! git remote | grep -q "^origin$"; then
    echo -e "${YELLOW}添加远程仓库...${NC}"
    git remote add origin $GITHUB_REPO
fi

# 检查 .env 文件是否存在
if [ -f ".env" ]; then
    echo -e "${YELLOW}警告：发现 .env 文件，请确保不要提交敏感信息！${NC}"
    echo "建议删除或重命名 .env 文件"
    read -p "是否继续？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 添加所有文件
echo -e "${YELLOW}添加文件到暂存区...${NC}"
git add .

# 显示变更
echo -e "${YELLOW}以下文件将被提交:${NC}"
git status --short

# 输入提交信息
echo ""
read -p "输入提交信息: " COMMIT_MESSAGE

if [ -z "$COMMIT_MESSAGE" ]; then
    COMMIT_MESSAGE="Update project files"
fi

# 提交
echo -e "${YELLOW}提交更改...${NC}"
git commit -m "$COMMIT_MESSAGE"

# 推送
echo -e "${YELLOW}推送到 GitHub...${NC}"
echo "提示：可能需要输入 GitHub 用户名和密码（或 Token）"
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}==================================${NC}"
    echo -e "${GREEN}   ✅ 推送成功！${NC}"
    echo -e "${GREEN}==================================${NC}"
    echo ""
    echo "项目地址：https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
    echo ""
else
    echo ""
    echo -e "${RED}==================================${NC}"
    echo -e "${RED}   ❌ 推送失败！${NC}"
    echo -e "${RED}==================================${NC}"
    echo ""
    echo "可能的原因:"
    echo "1. GitHub 用户名或密码错误"
    echo "2. 网络连接问题"
    echo "3. 仓库不存在或无权限"
    echo ""
    echo "解决方案:"
    echo "1. 检查 GitHub 用户名是否正确"
    echo "2. 使用 Personal Access Token 代替密码"
    echo "3. 确保已在 GitHub 创建仓库"
    echo ""
fi
