<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="container-responsive">
      <!-- 页面头部 -->
      <div class="mb-8">
        <nav class="flex" aria-label="Breadcrumb">
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
              任务详情
            </li>
          </ol>
        </nav>
        
        <h1 class="text-3xl font-bold text-gray-900 mt-4">
          任务详情
        </h1>
        <p class="text-gray-600 mt-2">
          任务ID: {{ taskId }}
        </p>
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="flex justify-center py-12">
        <div class="spinner w-8 h-8"></div>
      </div>

      <!-- 任务不存在 -->
      <div v-else-if="!task" class="text-center py-12">
        <div class="max-w-md mx-auto">
          <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h2 class="text-xl font-semibold text-gray-900 mb-2">任务未找到</h2>
          <p class="text-gray-600 mb-6">请检查任务ID是否正确</p>
          <router-link to="/" class="btn-primary">
            返回首页
          </router-link>
        </div>
      </div>

      <!-- 任务详情 -->
      <div v-else class="space-y-6">
        <!-- 进度显示组件 -->
        <TaskProgress 
          :task="task"
          @retry="handleRetry"
          @cancel="handleCancel"
        />

        <!-- 文件信息卡片 -->
        <div class="bg-white rounded-lg shadow-soft p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">文件信息</h3>
          <div v-if="fileInfo" class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">文件名</label>
              <p class="text-gray-900">{{ fileInfo.filename }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">文件大小</label>
              <p class="text-gray-900">{{ formatFileSize(fileInfo.size) }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">上传时间</label>
              <p class="text-gray-900">{{ formatDateTime(fileInfo.uploadTimestamp) }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">文件类型</label>
              <p class="text-gray-900">{{ fileInfo.contentType }}</p>
            </div>
          </div>
        </div>

        <!-- 分析结果卡片 (仅在完成时显示) -->
        <div v-if="task.status === 'success' && taskResult" class="bg-white rounded-lg shadow-soft p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">分析结果</h3>
          
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div class="text-center p-4 bg-blue-50 rounded-lg">
              <div class="text-2xl font-bold text-blue-600">{{ taskResult.total_highlights }}</div>
              <div class="text-sm text-gray-600">标注数量</div>
            </div>
            <div class="text-center p-4 bg-green-50 rounded-lg">
              <div class="text-2xl font-bold text-green-600">{{ taskResult.concepts_count }}</div>
              <div class="text-sm text-gray-600">核心概念</div>
            </div>
            <div class="text-center p-4 bg-purple-50 rounded-lg">
              <div class="text-2xl font-bold text-purple-600">{{ taskResult.themes_count }}</div>
              <div class="text-sm text-gray-600">主题分类</div>
            </div>
            <div class="text-center p-4 bg-orange-50 rounded-lg">
              <div class="text-2xl font-bold text-orange-600">{{ taskResult.people_count }}</div>
              <div class="text-sm text-gray-600">相关人物</div>
            </div>
          </div>
          
          <div class="flex justify-center space-x-4">
            <router-link 
              :to="`/graph/${taskId}`"
              class="btn-primary px-6 py-3"
            >
              查看知识图谱
            </router-link>
            
            <button 
              @click="downloadResult"
              class="btn-secondary px-6 py-3"
            >
              下载 Obsidian 文件
            </button>
          </div>
        </div>

        <!-- 任务时间线 -->
        <div class="bg-white rounded-lg shadow-soft p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">任务时间线</h3>
          
          <div class="space-y-3">
            <div class="flex items-center text-sm">
              <span class="w-20 text-gray-500">创建时间:</span>
              <span class="text-gray-900">{{ formatDateTime(task.createdAt) }}</span>
            </div>
            <div v-if="task.startedAt" class="flex items-center text-sm">
              <span class="w-20 text-gray-500">开始时间:</span>
              <span class="text-gray-900">{{ formatDateTime(task.startedAt) }}</span>
            </div>
            <div v-if="task.completedAt" class="flex items-center text-sm">
              <span class="w-20 text-gray-500">完成时间:</span>
              <span class="text-gray-900">{{ formatDateTime(task.completedAt) }}</span>
            </div>
            <div v-if="taskResult?.processing_time" class="flex items-center text-sm">
              <span class="w-20 text-gray-500">处理耗时:</span>
              <span class="text-gray-900">{{ formatTime(taskResult.processing_time) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TaskProgress from '@/components/TaskProgress.vue'
import { useTasksStore } from '@/stores/tasks'
import { useFilesStore } from '@/stores/files'
import { useAppStore } from '@/stores/app'

// Props
const props = defineProps({
  id: {
    type: String,
    required: true
  }
})

// Stores & Router
const route = useRoute()
const router = useRouter()
const tasksStore = useTasksStore()
const filesStore = useFilesStore()
const appStore = useAppStore()

// 响应式状态
const isLoading = ref(true)
const taskId = computed(() => props.id || route.params.id)
const task = computed(() => tasksStore.getTaskById(taskId.value))
const taskResult = ref(null)
const fileInfo = ref(null)

// 生命周期
onMounted(async () => {
  await fetchTaskData()
  
  // 如果任务正在运行，开始监听进度
  if (task.value && ['pending', 'running'].includes(task.value.status)) {
    tasksStore.startTaskMonitoring(taskId.value)
  }
})

onUnmounted(() => {
  // 清理WebSocket连接
  if (taskId.value) {
    tasksStore.stopTaskMonitoring(taskId.value)
  }
})

// 监听任务状态变化
watch(() => task.value?.status, async (newStatus, oldStatus) => {
  if (newStatus === 'success' && oldStatus !== 'success') {
    // 任务完成时获取结果
    await fetchTaskResult()
  }
})

// 方法
const fetchTaskData = async () => {
  isLoading.value = true
  
  try {
    // 获取任务信息
    await tasksStore.fetchTask(taskId.value)
    
    // 获取文件信息
    if (task.value?.fileId) {
      fileInfo.value = await filesStore.fetchFileInfo(task.value.fileId)
    }
    
    // 如果任务已完成，获取结果
    if (task.value?.status === 'success') {
      await fetchTaskResult()
    }
    
  } catch (error) {
    appStore.handleError(error, '获取任务信息')
  } finally {
    isLoading.value = false
  }
}

const fetchTaskResult = async () => {
  try {
    taskResult.value = await tasksStore.fetchTaskResult(taskId.value)
  } catch (error) {
    console.error('Failed to fetch task result:', error)
  }
}

const handleRetry = () => {
  // 重新开始任务逻辑
  router.push('/')
}

const handleCancel = () => {
  // 取消后的处理逻辑
  router.push('/tasks')
}

const downloadResult = () => {
  if (taskResult.value?.download_url) {
    window.open(taskResult.value.download_url, '_blank')
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const formatTime = (seconds) => {
  if (seconds < 60) return `${Math.round(seconds)}秒`
  if (seconds < 3600) return `${Math.round(seconds / 60)}分钟`
  return `${Math.round(seconds / 3600)}小时`
}
</script>