#!/bin/bash

echo "=== 前端API响应处理测试 ==="
echo ""

API_BASE="http://localhost:8000/api/v1"
TEST_TASK_ID="5dfe1727-9484-433f-87e1-5ed3dc9a1cdc"

echo "1. 测试任务API响应格式..."
curl -s "$API_BASE/tasks/$TEST_TASK_ID" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('原始响应结构:')
print(json.dumps(data, indent=2, ensure_ascii=False))
print('')
print('字段访问测试:')
print(f'- task_id: {data.get(\"task_id\", \"NOT_FOUND\")}')
print(f'- status: {data.get(\"status\", \"NOT_FOUND\")}')
print(f'- stage: {data.get(\"stage\", \"NOT_FOUND\")}')
print(f'- progress: {data.get(\"progress\", \"NOT_FOUND\")}')
"

echo ""
echo "2. 测试任务是否可以访问图谱..."
TASK_STATUS=$(curl -s "$API_BASE/tasks/$TEST_TASK_ID" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('status', 'NOT_FOUND'))")
echo "任务状态: $TASK_STATUS"

if [ "$TASK_STATUS" = "success" ]; then
    echo "✅ 任务已完成，可以访问图谱"
    
    echo ""
    echo "3. 测试图谱API访问..."
    curl -s "$API_BASE/graph/tasks/$TEST_TASK_ID/graph" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('success'):
    graph_data = data['data']
    nodes = graph_data['elements']['nodes']
    edges = graph_data['elements']['edges']
    print(f'✅ 图谱数据加载成功')
    print(f'   - 节点数: {len(nodes)}')
    print(f'   - 边数: {len(edges)}')
    print(f'   - 前3个节点: {[n[\"data\"][\"label\"] for n in nodes[:3]]}')
else:
    print('❌ 图谱数据加载失败')
"
else
    echo "❌ 任务未完成，无法访问图谱"
fi

echo ""
echo "=== 测试完成 ==="