#!/bin/bash

echo "=== 最终功能验证测试 ==="
echo ""

TEST_TASK_ID="5dfe1727-9484-433f-87e1-5ed3dc9a1cdc"

echo "🔍 验证任务状态..."
TASK_STATUS=$(curl -s "http://localhost:8000/api/v1/tasks/$TEST_TASK_ID" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('status', 'UNKNOWN'))")
echo "任务状态: $TASK_STATUS"

if [ "$TASK_STATUS" = "success" ]; then
    echo "✅ 任务已完成，可以访问知识图谱"
    
    echo ""
    echo "🌐 验证图谱数据..."
    GRAPH_DATA=$(curl -s "http://localhost:8000/api/v1/graph/tasks/$TEST_TASK_ID/graph")
    NODE_COUNT=$(echo $GRAPH_DATA | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data['data']['elements']['nodes']))")
    EDGE_COUNT=$(echo $GRAPH_DATA | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data['data']['elements']['edges']))")
    echo "图谱规模: $NODE_COUNT 个节点, $EDGE_COUNT 条边"
    
    echo ""
    echo "📊 验证图谱统计..."
    STATS_DATA=$(curl -s "http://localhost:8000/api/v1/graph/stats")
    TOTAL_NODES=$(echo $STATS_DATA | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['data']['total_nodes'])")
    TOTAL_EDGES=$(echo $STATS_DATA | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['data']['total_edges'])")
    echo "统计信息: $TOTAL_NODES 个节点, $TOTAL_EDGES 条边"
    
    echo ""
    echo "🔗 验证前端服务..."
    FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
    echo "前端服务状态: $FRONTEND_STATUS"
    
    if [ "$FRONTEND_STATUS" = "200" ]; then
        echo "✅ 前端服务正常"
        
        echo ""
        echo "🎯 测试链接:"
        echo "- 任务详情: http://localhost:3000/task/$TEST_TASK_ID"
        echo "- 知识图谱: http://localhost:3000/graph/$TEST_TASK_ID"
        
        echo ""
        echo "📋 修复内容总结:"
        echo "1. ✅ 修复了GraphService路径配置问题"
        echo "2. ✅ 修复了API路由重复问题"
        echo "3. ✅ 添加了前端图谱相关API接口"
        echo "4. ✅ 修复了API响应处理问题"
        echo "5. ✅ 完善了CORS配置"
        echo "6. ✅ 修复了GraphView中的ApiService调用问题"
        echo "7. ✅ 添加了详细的调试日志"
        
        echo ""
        echo "🎉 现在用户可以:"
        echo "1. 访问任务详情页面"
        echo "2. 点击'查看知识图谱'按钮"
        echo "3. 查看${NODE_COUNT}个节点的交互式知识图谱"
        echo "4. 使用搜索、筛选、布局切换等功能"
        echo "5. 点击节点查看详细信息和关联关系"
        
    else
        echo "❌ 前端服务异常，状态码: $FRONTEND_STATUS"
    fi
    
else
    echo "❌ 任务未完成，状态: $TASK_STATUS"
fi

echo ""
echo "=== 验证完成 ==="