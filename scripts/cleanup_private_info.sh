#!/bin/bash

# 清理私人信息脚本
# 用于在上传 GitHub 前移除所有个人隐私信息

PROJECT_DIR="/Users/huangmin/Library/CloudStorage/OneDrive-个人/own/zhiping-manager"

echo "🧹 开始清理私人信息..."
echo ""

# 替换个人路径
find "$PROJECT_DIR" -type f \( -name "*.md" -o -name "*.txt" -o -name "*.sh" \) -exec sed -i '' \
  's|/Users/huangmin/Library/CloudStorage/OneDrive-个人/own/zhiping-manager|/path/to/zhiping-manager|g' {} \;

find "$PROJECT_DIR" -type f \( -name "*.md" -o -name "*.txt" -o -name "*.sh" \) -exec sed -i '' \
  's|huangmin|yourusername|g' {} \;

find "$PROJECT_DIR" -type f \( -name "*.md" -o -name "*.txt" -o -name "*.sh" \) -exec sed -i '' \
  's|OneDrive-个人/own|projects|g' {} \;

echo "✅ 个人路径已替换"
echo ""

# 显示清理结果
echo "📋 清理后的路径示例："
grep -r "path/to/zhiping-manager" "$PROJECT_DIR/docs/" | head -3 | while read line; do
  echo "  $line"
done

echo ""
echo "💡 下一步:"
echo "1. 检查清理结果是否满意"
echo "2. 运行 git add . 和 git commit"
echo "3. 上传到 GitHub"
echo ""
