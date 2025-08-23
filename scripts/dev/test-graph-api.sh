#!/bin/bash

echo "=== 知识图谱API测试 ==="
echo ""

API_BASE="http://localhost:8000/api/v1"

echo "1. 测试图谱统计API..."
curl -s "$API_BASE/graph/stats" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data['success']:
    stats = data['data']
    print(f'✅ 总节点数: {stats[\"total_nodes\"]}')
    print(f'✅ 总边数: {stats[\"total_edges\"]}')
    print(f'✅ 节点类型: {stats[\"node_types\"]}')
    print(f'✅ 平均连接数: {stats[\"average_connections\"]}')
else:
    print('❌ 统计API失败')
"

echo ""
echo "2. 测试图谱数据API..."
curl -s "$API_BASE/graph/tasks/test_task/graph" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data['success']:
    graph = data['data']
    nodes = graph['elements']['nodes']
    edges = graph['elements']['edges']
    print(f'✅ 节点数量: {len(nodes)}')
    print(f'✅ 边数量: {len(edges)}')
    
    # 显示前几个节点
    print('✅ 前5个节点:')
    for i, node in enumerate(nodes[:5]):
        node_data = node['data']
        print(f'   {i+1}. {node_data[\"label\"]} ({node_data[\"type\"]})')
        
else:
    print('❌ 图谱数据API失败')
"

echo ""
echo "3. 测试搜索API..."
curl -s "$API_BASE/graph/search?q=死亡" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data['success']:
        results = data['data']
        print(f'✅ 搜索结果数: {results[\"total\"]}')
        if results['results']:
            print('✅ 前3个结果:')
            for i, result in enumerate(results['results'][:3]):
                print(f'   {i+1}. {result[\"label\"]} ({result[\"type\"]})')
        else:
            print('ℹ️  没有找到匹配结果')
    else:
        print('❌ 搜索API失败')
except:
    print('❌ 搜索API响应解析失败 (可能中文编码问题)')
"

echo ""
echo "4. 测试节点邻居API..."
curl -s "$API_BASE/graph/nodes/尼采/neighbors" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data['success']:
        subgraph = data['data']['subgraph']
        nodes = subgraph['elements']['nodes']
        edges = subgraph['elements']['edges']
        print(f'✅ 邻居节点数: {len(nodes)-1}')
        print(f'✅ 连接边数: {len(edges)}')
    else:
        print('❌ 节点邻居API失败')
except:
    print('❌ 节点邻居API响应解析失败')
"

echo ""
echo "=== 测试完成 ==="