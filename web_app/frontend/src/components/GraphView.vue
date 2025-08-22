<template>
  <div class="graph-view-container">
    <!-- 控制面板 -->
    <div class="graph-controls bg-white rounded-lg shadow-soft p-4 mb-4">
      <div class="flex flex-col md:flex-row gap-4 items-start md:items-center">
        <!-- 搜索框 -->
        <div class="flex-1 min-w-0">
          <div class="relative">
            <input
              v-model="searchQuery"
              @input="handleSearch"
              type="text"
              placeholder="搜索节点..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
            <svg class="w-5 h-5 text-gray-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        <!-- 节点类型筛选 -->
        <div class="flex gap-2">
          <button
            v-for="filterType in nodeFilters"
            :key="filterType.value"
            @click="toggleFilter(filterType.value)"
            :class="{
              'bg-blue-600 text-white': activeFilters.includes(filterType.value),
              'bg-gray-100 text-gray-700 hover:bg-gray-200': !activeFilters.includes(filterType.value)
            }"
            class="px-3 py-1.5 rounded-full text-sm font-medium transition-colors"
          >
            {{ filterType.label }}
          </button>
          
          <!-- 重置筛选 -->
          <button
            v-if="activeFilters.length > 0"
            @click="resetFilters"
            class="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700"
          >
            重置
          </button>
        </div>

        <!-- 布局控制 -->
        <div class="flex gap-2">
          <select
            v-model="selectedLayout"
            @change="changeLayout"
            class="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
          >
            <option value="cose-bilkent">智能布局</option>
            <option value="circle">圆形布局</option>
            <option value="grid">网格布局</option>
            <option value="concentric">同心圆</option>
            <option value="breadthfirst">层次布局</option>
          </select>
          
          <button
            @click="fitGraph"
            class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium"
          >
            适应屏幕
          </button>
        </div>
      </div>
    </div>

    <!-- 图谱容器 -->
    <div class="graph-container bg-white rounded-lg shadow-soft overflow-hidden">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="flex items-center justify-center h-96">
        <div class="text-center">
          <div class="spinner w-8 h-8 mx-auto mb-4"></div>
          <p class="text-gray-600">加载知识图谱...</p>
        </div>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="flex items-center justify-center h-96">
        <div class="text-center">
          <svg class="w-16 h-16 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">加载失败</h3>
          <p class="text-gray-600 mb-4">{{ error }}</p>
          <button @click="loadGraph" class="btn-primary">
            重试
          </button>
        </div>
      </div>

      <!-- 图谱渲染区域 -->
      <div 
        v-show="!isLoading && !error"
        ref="graphContainer"
        class="cytoscape-container"
        style="width: 100%; height: 600px;"
      ></div>
    </div>

    <!-- 节点详情面板 -->
    <div 
      v-if="selectedNode"
      class="node-details-panel fixed right-4 top-1/2 transform -translate-y-1/2 bg-white rounded-lg shadow-lg p-4 w-80 z-10"
    >
      <div class="flex items-center justify-between mb-3">
        <h3 class="font-semibold text-gray-900">节点详情</h3>
        <button @click="closeNodeDetails" class="text-gray-400 hover:text-gray-600">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="space-y-3">
        <div>
          <label class="block text-sm font-medium text-gray-700">名称</label>
          <p class="mt-1 text-gray-900">{{ selectedNode.label }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">类型</label>
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                :class="getNodeTypeClass(selectedNode.type)">
            {{ getNodeTypeLabel(selectedNode.type) }}
          </span>
        </div>

        <div v-if="selectedNode.importance">
          <label class="block text-sm font-medium text-gray-700">重要性</label>
          <div class="mt-1 flex items-center">
            <div class="flex-1 bg-gray-200 rounded-full h-2">
              <div 
                class="bg-blue-600 h-2 rounded-full"
                :style="{ width: `${selectedNode.importance * 100}%` }"
              ></div>
            </div>
            <span class="ml-2 text-sm text-gray-600">{{ (selectedNode.importance * 100).toFixed(0) }}%</span>
          </div>
        </div>

        <div v-if="neighborNodes.length > 0">
          <label class="block text-sm font-medium text-gray-700 mb-2">相关节点 ({{ neighborNodes.length }})</label>
          <div class="space-y-1 max-h-32 overflow-y-auto">
            <button
              v-for="neighbor in neighborNodes"
              :key="neighbor.id"
              @click="focusNode(neighbor.id)"
              class="w-full text-left px-2 py-1 text-sm text-gray-700 hover:bg-gray-100 rounded"
            >
              {{ neighbor.label }}
            </button>
          </div>
        </div>

        <div class="pt-2 border-t border-gray-200">
          <button
            @click="showNeighbors"
            class="w-full btn-ghost text-sm"
          >
            显示邻居网络
          </button>
        </div>
      </div>
    </div>

    <!-- 图谱统计信息 -->
    <div v-if="graphStats" class="mt-4 bg-white rounded-lg shadow-soft p-4">
      <h3 class="font-semibold text-gray-900 mb-3">图谱统计</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
        <div class="bg-blue-50 rounded-lg p-3">
          <div class="text-2xl font-bold text-blue-600">{{ graphStats.total_nodes }}</div>
          <div class="text-sm text-gray-600">总节点数</div>
        </div>
        <div class="bg-green-50 rounded-lg p-3">
          <div class="text-2xl font-bold text-green-600">{{ graphStats.total_edges }}</div>
          <div class="text-sm text-gray-600">连接数</div>
        </div>
        <div class="bg-purple-50 rounded-lg p-3">
          <div class="text-2xl font-bold text-purple-600">{{ graphStats.average_connections }}</div>
          <div class="text-sm text-gray-600">平均连接</div>
        </div>
        <div class="bg-orange-50 rounded-lg p-3">
          <div class="text-2xl font-bold text-orange-600">{{ Object.keys(graphStats.node_types).length }}</div>
          <div class="text-sm text-gray-600">节点类型</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import cytoscape from 'cytoscape'
import dagre from 'cytoscape-dagre'
import cola from 'cytoscape-cola'
import coseBilkent from 'cytoscape-cose-bilkent'
import { ApiService } from '@/services/api.js'

// 注册布局插件
cytoscape.use(dagre)
cytoscape.use(cola)
cytoscape.use(coseBilkent)

// Props
const props = defineProps({
  taskId: {
    type: String,
    required: true
  }
})

// 响应式数据
const graphContainer = ref(null)
const isLoading = ref(true)
const error = ref(null)
const cy = ref(null)
const graphData = ref(null)
const graphStats = ref(null)

// 搜索和筛选
const searchQuery = ref('')
const activeFilters = ref([])
const nodeFilters = [
  { label: '概念', value: 'concept' },
  { label: '主题', value: 'theme' },
  { label: '人物', value: 'person' }
]

// 布局控制
const selectedLayout = ref('cose-bilkent')

// 节点详情
const selectedNode = ref(null)
const neighborNodes = ref([])

// 生命周期
onMounted(async () => {
  await loadGraph()
  await loadGraphStats()
})

onUnmounted(() => {
  if (cy.value) {
    cy.value.destroy()
  }
})

// 方法
const loadGraph = async () => {
  isLoading.value = true
  error.value = null
  
  try {
    const response = await ApiService.getGraphData(props.taskId)
    graphData.value = response
    
    await nextTick()
    initializeGraph()
    
  } catch (err) {
    console.error('加载图谱失败:', err)
    error.value = err.response?.data?.detail || '加载图谱失败'
  } finally {
    isLoading.value = false
  }
}

const loadGraphStats = async () => {
  try {
    const response = await ApiService.getGraphStats()
    graphStats.value = response
  } catch (err) {
    console.error('加载图谱统计失败:', err)
  }
}

const initializeGraph = () => {
  if (!graphContainer.value || !graphData.value) return
  
  // 销毁现有实例
  if (cy.value) {
    cy.value.destroy()
  }
  
  // 创建新的Cytoscape实例
  cy.value = cytoscape({
    container: graphContainer.value,
    elements: graphData.value.elements,
    style: graphData.value.style,
    layout: graphData.value.layout,
    
    // 交互设置
    minZoom: 0.3,
    maxZoom: 3,
    wheelSensitivity: 0.5,
    
    // 性能设置
    pixelRatio: 'auto',
    motionBlur: true,
    textureOnViewport: true,
    hideEdgesOnViewport: true,
    hideLabelsOnViewport: true
  })
  
  // 绑定事件
  setupGraphEvents()
}

const setupGraphEvents = () => {
  if (!cy.value) return
  
  // 节点点击事件
  cy.value.on('tap', 'node', async (event) => {
    const node = event.target
    const nodeData = node.data()
    
    selectedNode.value = {
      id: nodeData.id,
      label: nodeData.label,
      type: nodeData.type,
      category: nodeData.category,
      importance: nodeData.importance,
      conceptType: nodeData.conceptType
    }
    
    // 获取邻居节点
    await loadNeighborNodes(nodeData.id)
    
    // 高亮选中节点
    cy.value.elements().removeClass('highlighted')
    node.addClass('highlighted')
    node.neighborhood().addClass('highlighted')
  })
  
  // 背景点击事件
  cy.value.on('tap', (event) => {
    if (event.target === cy.value) {
      closeNodeDetails()
    }
  })
  
  // 节点悬浮事件
  cy.value.on('mouseover', 'node', (event) => {
    const node = event.target
    node.style('cursor', 'pointer')
  })
  
  cy.value.on('mouseout', 'node', (event) => {
    const node = event.target
    node.style('cursor', 'default')
  })
}

const loadNeighborNodes = async (nodeId) => {
  try {
    const response = await ApiService.getNodeNeighbors(nodeId)
    const neighbors = response.subgraph.elements.nodes
    
    neighborNodes.value = neighbors
      .filter(n => n.data.id !== nodeId)
      .map(n => ({
        id: n.data.id,
        label: n.data.label,
        type: n.data.type
      }))
      
  } catch (err) {
    console.error('加载邻居节点失败:', err)
    neighborNodes.value = []
  }
}

const handleSearch = async () => {
  if (!searchQuery.value.trim() || !cy.value) {
    // 重置高亮
    cy.value.elements().removeClass('search-highlighted')
    return
  }
  
  try {
    const response = await ApiService.searchGraphNodes(searchQuery.value)
    
    const matchedNodes = response.results
    
    // 重置所有高亮
    cy.value.elements().removeClass('search-highlighted')
    
    // 高亮匹配的节点
    matchedNodes.forEach(nodeData => {
      const node = cy.value.getElementById(nodeData.id)
      if (node.length > 0) {
        node.addClass('search-highlighted')
      }
    })
    
    // 如果有匹配结果，聚焦到第一个
    if (matchedNodes.length > 0) {
      const firstNode = cy.value.getElementById(matchedNodes[0].id)
      if (firstNode.length > 0) {
        cy.value.center(firstNode)
      }
    }
    
  } catch (err) {
    console.error('搜索失败:', err)
  }
}

const toggleFilter = (filterType) => {
  const index = activeFilters.value.indexOf(filterType)
  if (index > -1) {
    activeFilters.value.splice(index, 1)
  } else {
    activeFilters.value.push(filterType)
  }
  
  applyFilters()
}

const resetFilters = () => {
  activeFilters.value = []
  applyFilters()
}

const applyFilters = () => {
  if (!cy.value) return
  
  if (activeFilters.value.length === 0) {
    // 显示所有节点
    cy.value.elements().style('display', 'element')
  } else {
    // 隐藏所有节点
    cy.value.elements().style('display', 'none')
    
    // 显示匹配类型的节点
    activeFilters.value.forEach(filterType => {
      cy.value.nodes(`[type="${filterType}"]`).style('display', 'element')
    })
    
    // 显示连接可见节点的边
    const visibleNodes = cy.value.nodes('[?style.display != "none"]')
    visibleNodes.connectedEdges().style('display', 'element')
  }
}

const changeLayout = () => {
  if (!cy.value) return
  
  const layoutOptions = {
    name: selectedLayout.value,
    fit: true,
    padding: 30,
    animate: true,
    animationDuration: 1000
  }
  
  // 根据不同布局添加特定选项
  switch (selectedLayout.value) {
    case 'cose-bilkent':
      layoutOptions.idealEdgeLength = 50
      layoutOptions.nodeOverlap = 10
      layoutOptions.refresh = 20
      break
    case 'circle':
      layoutOptions.radius = 200
      break
    case 'grid':
      layoutOptions.rows = Math.ceil(Math.sqrt(cy.value.nodes().length))
      break
    case 'concentric':
      layoutOptions.concentric = (node) => node.data('importance') || 0.5
      break
    case 'breadthfirst':
      layoutOptions.directed = true
      break
  }
  
  const layout = cy.value.layout(layoutOptions)
  layout.run()
}

const fitGraph = () => {
  if (cy.value) {
    cy.value.fit(null, 50)
  }
}

const focusNode = (nodeId) => {
  if (cy.value) {
    const node = cy.value.getElementById(nodeId)
    if (node.length > 0) {
      cy.value.center(node)
      cy.value.zoom(1.5)
    }
  }
}

const showNeighbors = async () => {
  if (!selectedNode.value) return
  
  try {
    const response = await ApiService.getNodeNeighbors(selectedNode.value.id)
    const subgraphData = response.subgraph
    
    // 用子图数据替换当前图谱
    cy.value.elements().remove()
    cy.value.add(subgraphData.elements)
    
    // 应用布局
    const layout = cy.value.layout({
      name: 'cose-bilkent',
      fit: true,
      padding: 30
    })
    layout.run()
    
  } catch (err) {
    console.error('显示邻居网络失败:', err)
  }
}

const closeNodeDetails = () => {
  selectedNode.value = null
  neighborNodes.value = []
  
  if (cy.value) {
    cy.value.elements().removeClass('highlighted')
  }
}

// 辅助函数
const getNodeTypeClass = (type) => {
  switch (type) {
    case 'concept': return 'bg-blue-100 text-blue-800'
    case 'theme': return 'bg-green-100 text-green-800'
    case 'person': return 'bg-purple-100 text-purple-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const getNodeTypeLabel = (type) => {
  switch (type) {
    case 'concept': return '概念'
    case 'theme': return '主题'
    case 'person': return '人物'
    default: return '未知'
  }
}
</script>

<style scoped>
.graph-view-container {
  @apply max-w-7xl mx-auto p-4;
}

.cytoscape-container {
  border: 1px solid #e5e7eb;
}

.node-details-panel {
  max-height: 80vh;
  overflow-y: auto;
}

/* Cytoscape样式增强 */
:deep(.cy-node.highlighted) {
  background-color: #fbbf24 !important;
  border-color: #f59e0b !important;
  border-width: 3px !important;
}

:deep(.cy-edge.highlighted) {
  line-color: #f59e0b !important;
  target-arrow-color: #f59e0b !important;
  width: 4px !important;
}

:deep(.cy-node.search-highlighted) {
  background-color: #ef4444 !important;
  border-color: #dc2626 !important;
  border-width: 3px !important;
}
</style>