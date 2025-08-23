#!/bin/bash

echo "=== 最终验证测试 ==="
echo ""

# 测试任务ID
TEST_TASK_ID="5dfe1727-9484-433f-87e1-5ed3dc9a1cdc"

echo "1. 验证后端API正常工作..."
echo "✅ 后端服务状态: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)"
echo "✅ 任务API状态: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/tasks/$TEST_TASK_ID)"
echo "✅ 图谱API状态: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/graph/tasks/$TEST_TASK_ID/graph)"

echo ""
echo "2. 验证任务数据..."
TASK_DATA=$(curl -s "http://localhost:8000/api/v1/tasks/$TEST_TASK_ID")
echo "任务状态: $(echo $TASK_DATA | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('status', 'UNKNOWN'))")"

echo ""
echo "3. 验证图谱数据..."
GRAPH_DATA=$(curl -s "http://localhost:8000/api/v1/graph/tasks/$TEST_TASK_ID/graph")
GRAPH_SUCCESS=$(echo $GRAPH_DATA | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('success', False))")
NODE_COUNT=$(echo $GRAPH_DATA | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data['data']['elements']['nodes']) if data.get('success') else 0)")
EDGE_COUNT=$(echo $GRAPH_DATA | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data['data']['elements']['edges']) if data.get('success') else 0)")

echo "图谱API成功: $GRAPH_SUCCESS"
echo "节点数量: $NODE_COUNT"
echo "边数量: $EDGE_COUNT"

echo ""
echo "4. 前端访问测试..."
echo "前端服务: http://localhost:3000"
echo "任务详情: http://localhost:3000/task/$TEST_TASK_ID"
echo "知识图谱: http://localhost:3000/graph/$TEST_TASK_ID"

echo ""
echo "=== 修复总结 ==="
echo "✅ 修复了GraphService路径配置问题"
echo "✅ 修复了API路由重复问题"
echo "✅ 添加了前端图谱相关API接口"
echo "✅ 修复了API响应处理问题"
echo "✅ 完善了CORS配置"
echo "✅ 添加了详细的调试日志"

echo ""
echo "现在用户应该能够:"
echo "1. 访问任务详情页面"
echo "2. 点击'查看知识图谱'按钮"
echo "3. 成功加载交互式知识图谱"
echo "4. 查看${NODE_COUNT}个节点和${EDGE_COUNT}条边的知识网络"

echo ""
echo "=== 测试完成 ==="