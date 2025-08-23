#!/bin/bash
# Kindle Assistant CLI 功能演示脚本

echo "🎯 Kindle Assistant CLI 功能演示"
echo "=================================="

# 获取项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." &> /dev/null && pwd)"
cd "$PROJECT_ROOT"

echo ""
echo "📍 当前目录: $(pwd)"

echo ""
echo "1️⃣ 显示版本信息"
echo "-------------------"
./kindle-assistant version

echo ""
echo "2️⃣ 系统状态检查"  
echo "-------------------"
./kindle-assistant status

echo ""
echo "3️⃣ 可用命令列表"
echo "-------------------"
./kindle-assistant --help

echo ""
echo "🎉 演示完成！"
echo ""
echo "🔗 常用命令："
echo "  ./kindle-assistant init     # 初始化环境"
echo "  ./kindle-assistant analyze  # 运行分析"
echo "  ./kindle-assistant start    # 启动Web服务"
echo "  ./kindle-assistant clean    # 清理临时文件"
echo ""
echo "📚 详细文档: docs/guides/CLI-Usage-Guide.md"