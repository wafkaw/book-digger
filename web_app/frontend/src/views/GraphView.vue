<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="container-responsive max-w-7xl">
      <!-- 页面头部 -->
      <div class="mb-6">
        <nav class="flex mb-4" aria-label="Breadcrumb">
          <ol class="flex items-center space-x-4">
            <li>
              <router-link to="/" class="text-gray-500 hover:text-gray-700">
                首页
              </router-link>
            </li>
            <li>
              <svg class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </li>
            <li>
              <router-link to="/tasks" class="text-gray-500 hover:text-gray-700">
                任务历史
              </router-link>
            </li>
            <li>
              <svg class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </li>
            <li class="text-gray-900 font-medium">
              知识图谱
            </li>
          </ol>
        </nav>
        
        <div class="flex flex-col md:flex-row md:items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">知识图谱可视化</h1>
            <p class="text-gray-600 mt-2">
              任务ID: {{ taskId }} | 交互式探索125个节点的知识网络
            </p>
          </div>
          
          <div class="mt-4 md:mt-0 flex gap-3">
            <button
              @click="exportGraph"
              :disabled="isExporting"
              class="btn-secondary"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4-4m0 0l-4 4m4-4v12" />
              </svg>
              {{ isExporting ? '导出中...' : '导出图谱' }}
            </button>
            
            <router-link 
              :to="`/task/${taskId}`"
              class="btn-ghost"
            >
              返回任务详情
            </router-link>
          </div>
        </div>
      </div>

      <!-- 使用指南 -->
      <div v-if="showGuide" class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg class="w-5 h-5 text-blue-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="ml-3 flex-1">
            <h3 class="text-sm font-medium text-blue-800">使用指南</h3>
            <div class="mt-2 text-sm text-blue-700">
              <ul class="list-disc list-inside space-y-1">
                <li><strong>点击节点</strong> - 查看详细信息和关联节点</li>
                <li><strong>搜索功能</strong> - 在搜索框中输入关键词快速定位</li>
                <li><strong>类型筛选</strong> - 使用概念/主题/人物按钮筛选显示</li>
                <li><strong>布局调整</strong> - 尝试不同的布局算法优化视图</li>
                <li><strong>缩放拖拽</strong> - 鼠标滚轮缩放，拖拽平移视图</li>
              </ul>
            </div>
          </div>
          <button @click="showGuide = false" class="flex-shrink-0 ml-3 text-blue-400 hover:text-blue-600">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="error && !isLoading" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <div class="flex items-center">
          <svg class="w-5 h-5 text-red-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 class="text-sm font-medium text-red-800">加载失败</h3>
            <p class="text-sm text-red-700 mt-1">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- 主要图谱组件 -->
      <GraphViewComponent 
        v-if="!error"
        :taskId="taskId"
        @export-request="handleExportRequest"
        @error="handleGraphError"
      />
      
      <!-- 快速操作面板 -->
      <div class="fixed bottom-6 right-6 z-20">
        <div class="bg-white rounded-lg shadow-lg p-3 space-y-2">
          <button
            @click="showGuide = true"
            class="flex items-center justify-center w-10 h-10 bg-blue-100 hover:bg-blue-200 text-blue-600 rounded-full transition-colors"
            title="显示使用指南"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
          
          <button
            @click="scrollToTop"
            class="flex items-center justify-center w-10 h-10 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-full transition-colors"
            title="返回顶部"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11l5-5m0 0l5 5m-5-5v12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
    
    <!-- 全屏加载蒙层 -->
    <div v-if="isLoading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-8 max-w-sm mx-4">
        <div class="text-center">
          <div class="spinner w-12 h-12 mx-auto mb-4"></div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">正在加载知识图谱</h3>
          <p class="text-gray-600 text-sm">
            正在解析125个节点的关系网络...
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import GraphViewComponent from '@/components/GraphView.vue'
import ApiService from '@/services/api.js'
import { useAppStore } from '@/stores/app'

// 路由和状态
const route = useRoute()
const appStore = useAppStore()

// 响应式数据
const isLoading = ref(true)
const error = ref(null)
const isExporting = ref(false)
const showGuide = ref(true)

// 计算属性
const taskId = computed(() => route.params.id)

// 生命周期
onMounted(async () => {
  // 检查任务是否存在
  await validateTask()
})

// 方法
const validateTask = async () => {
  isLoading.value = true
  error.value = null
  
  try {
    // 验证任务存在且已完成
    const response = await ApiService.get(`/tasks/${taskId.value}`)
    const task = response.data.data
    
    if (task.status !== 'success') {
      throw new Error('任务尚未完成或失败，无法查看知识图谱')
    }
    
    // 任务验证成功
    isLoading.value = false
    
  } catch (err) {
    console.error('验证任务失败:', err)
    error.value = err.response?.data?.detail || err.message || '任务验证失败'
    isLoading.value = false
  }
}

const handleGraphError = (errorMessage) => {
  error.value = errorMessage
}

const handleExportRequest = () => {
  exportGraph()
}

const exportGraph = async () => {
  if (isExporting.value) return
  
  isExporting.value = true
  
  try {
    const response = await ApiService.get(
      `/graph/export/${taskId.value}`,
      { params: { format: 'json' } }
    )
    
    // 创建下载链接
    const data = JSON.stringify(response.data.data.graphData, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = `knowledge-graph-${taskId.value}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    window.URL.revokeObjectURL(url)
    
    appStore.showNotification({
      type: 'success',
      title: '导出成功',
      message: '知识图谱数据已下载'
    })
    
  } catch (err) {
    console.error('导出失败:', err)
    appStore.handleError(err, '导出图谱')
  } finally {
    isExporting.value = false
  }
}

const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}
</script>

<style scoped>
/* 确保容器样式正确 */
.container-responsive {
  @apply mx-auto px-4 sm:px-6 lg:px-8;
}

/* 自定义滚动条 */
:deep(.node-details-panel) {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e0 #f7fafc;
}

:deep(.node-details-panel::-webkit-scrollbar) {
  width: 6px;
}

:deep(.node-details-panel::-webkit-scrollbar-track) {
  background: #f7fafc;
  border-radius: 3px;
}

:deep(.node-details-panel::-webkit-scrollbar-thumb) {
  background: #cbd5e0;
  border-radius: 3px;
}

:deep(.node-details-panel::-webkit-scrollbar-thumb:hover) {
  background: #a0aec0;
}
</style>