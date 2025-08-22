<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="container-responsive">
      <!-- 页面头部 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">任务历史</h1>
        <p class="text-gray-600 mt-2">查看所有分析任务的历史记录和状态</p>
      </div>

      <!-- 任务统计概览 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg p-6 shadow-soft">
          <div class="flex items-center">
            <div class="p-2 bg-blue-100 rounded-lg">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-2xl font-bold text-gray-900">{{ totalTasks }}</p>
              <p class="text-gray-600 text-sm">总任务数</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg p-6 shadow-soft">
          <div class="flex items-center">
            <div class="p-2 bg-green-100 rounded-lg">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-2xl font-bold text-gray-900">{{ completedTasksCount }}</p>
              <p class="text-gray-600 text-sm">已完成</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg p-6 shadow-soft">
          <div class="flex items-center">
            <div class="p-2 bg-yellow-100 rounded-lg">
              <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-2xl font-bold text-gray-900">{{ runningTasksCount }}</p>
              <p class="text-gray-600 text-sm">进行中</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg p-6 shadow-soft">
          <div class="flex items-center">
            <div class="p-2 bg-red-100 rounded-lg">
              <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-2xl font-bold text-gray-900">{{ failedTasksCount }}</p>
              <p class="text-gray-600 text-sm">失败</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 任务列表 -->
      <div class="bg-white rounded-lg shadow-soft">
        <!-- 列表头部 -->
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900">任务列表</h2>
            <div class="flex items-center space-x-4">
              <!-- 刷新按钮 -->
              <button 
                @click="refreshTasks"
                :disabled="isRefreshing"
                class="btn-ghost"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                     :class="{ 'animate-spin': isRefreshing }">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span class="ml-1">刷新</span>
              </button>
              
              <!-- 新建任务按钮 -->
              <router-link to="/" class="btn-primary">
                新建任务
              </router-link>
            </div>
          </div>
        </div>

        <!-- 任务列表内容 -->
        <div class="divide-y divide-gray-200">
          <!-- 加载状态 -->
          <div v-if="isLoading" class="p-12 text-center">
            <div class="spinner w-8 h-8 mx-auto mb-4"></div>
            <p class="text-gray-600">加载任务列表...</p>
          </div>

          <!-- 空状态 -->
          <div v-else-if="tasksList.length === 0" class="p-12 text-center">
            <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">暂无任务</h3>
            <p class="text-gray-600 mb-6">开始上传你的第一个 Kindle 文件吧</p>
            <router-link to="/" class="btn-primary">
              立即开始
            </router-link>
          </div>

          <!-- 任务列表项 -->
          <div 
            v-for="task in tasksList" 
            :key="task.id"
            class="p-6 hover:bg-gray-50 transition-colors cursor-pointer"
            @click="viewTask(task.id)"
          >
            <div class="flex items-center justify-between">
              <!-- 任务信息 -->
              <div class="flex-1">
                <div class="flex items-center space-x-3 mb-2">
                  <h3 class="font-medium text-gray-900">
                    任务 {{ task.id.slice(0, 8) }}...
                  </h3>
                  
                  <!-- 状态标签 -->
                  <span :class="getStatusClass(task.status)">
                    {{ getStatusText(task.status) }}
                  </span>
                  
                  <!-- 进度百分比 -->
                  <span v-if="task.status === 'running'" class="text-sm text-gray-500">
                    {{ Math.round(task.progress) }}%
                  </span>
                </div>
                
                <div class="flex items-center text-sm text-gray-500 space-x-4">
                  <span>{{ formatDateTime(task.createdAt) }}</span>
                  <span>文件: {{ task.fileId?.slice(0, 8) }}...</span>
                  <span v-if="task.processingTime">
                    耗时: {{ formatTime(task.processingTime) }}
                  </span>
                </div>
                
                <!-- 错误信息 -->
                <div v-if="task.errorMessage" class="mt-2">
                  <p class="text-sm text-red-600">{{ task.errorMessage }}</p>
                </div>
              </div>

              <!-- 进度条 (仅运行中任务) -->
              <div v-if="task.status === 'running'" class="w-32 ml-6">
                <div class="progress">
                  <div 
                    class="progress-bar"
                    :style="{ width: `${task.progress}%` }"
                  ></div>
                </div>
              </div>

              <!-- 操作按钮 -->
              <div class="flex items-center space-x-2 ml-6">
                <button 
                  v-if="task.status === 'success'"
                  @click.stop="viewGraph(task.id)"
                  class="btn-ghost text-sm"
                >
                  查看图谱
                </button>
                
                <button 
                  v-if="task.status === 'running'"
                  @click.stop="cancelTask(task.id)"
                  class="btn-ghost text-sm text-red-600"
                >
                  取消
                </button>
                
                <button 
                  v-if="task.status === 'failure'"
                  @click.stop="retryTask(task)"
                  class="btn-ghost text-sm text-blue-600"
                >
                  重试
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTasksStore } from '@/stores/tasks'
import { useAppStore } from '@/stores/app'

// Stores & Router
const router = useRouter()
const tasksStore = useTasksStore()
const appStore = useAppStore()

// 响应式状态
const isLoading = ref(false)
const isRefreshing = ref(false)

// 计算属性
const tasksList = computed(() => tasksStore.tasksList)
const totalTasks = computed(() => tasksList.value.length)
const completedTasksCount = computed(() => tasksStore.completedTasks.length)
const runningTasksCount = computed(() => tasksStore.runningTasks.length)
const failedTasksCount = computed(() => tasksStore.failedTasks.length)

// 生命周期
onMounted(async () => {
  await loadTasks()
})

// 方法
const loadTasks = async () => {
  isLoading.value = true
  
  try {
    await tasksStore.fetchTasks()
  } catch (error) {
    appStore.handleError(error, '加载任务列表')
  } finally {
    isLoading.value = false
  }
}

const refreshTasks = async () => {
  isRefreshing.value = true
  
  try {
    await tasksStore.fetchTasks()
    appStore.showNotification({
      type: 'success',
      title: '刷新成功',
      message: '任务列表已更新'
    })
  } catch (error) {
    appStore.handleError(error, '刷新任务列表')
  } finally {
    isRefreshing.value = false
  }
}

const viewTask = (taskId) => {
  router.push(`/task/${taskId}`)
}

const viewGraph = (taskId) => {
  router.push(`/graph/${taskId}`)
}

const cancelTask = async (taskId) => {
  try {
    await tasksStore.cancelTask(taskId)
    appStore.showNotification({
      type: 'info',
      title: '任务已取消',
      message: '分析任务已成功取消'
    })
  } catch (error) {
    appStore.handleError(error, '取消任务')
  }
}

const retryTask = (task) => {
  // 实现重试逻辑 - 跳转到首页重新开始
  router.push('/')
}

const getStatusClass = (status) => {
  switch (status) {
    case 'pending': return 'status-pending'
    case 'running': return 'status-running'
    case 'success': return 'status-success'
    case 'failure': return 'status-error'
    case 'cancelled': return 'status-pending'
    default: return 'status-pending'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'pending': return '等待中'
    case 'running': return '处理中'
    case 'success': return '已完成'
    case 'failure': return '失败'
    case 'cancelled': return '已取消'
    default: return '未知'
  }
}

const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  const now = new Date()
  const diffInMinutes = Math.round((now - date) / (1000 * 60))
  
  if (diffInMinutes < 1) return '刚刚'
  if (diffInMinutes < 60) return `${diffInMinutes}分钟前`
  if (diffInMinutes < 1440) return `${Math.round(diffInMinutes / 60)}小时前`
  
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatTime = (seconds) => {
  if (seconds < 60) return `${Math.round(seconds)}秒`
  if (seconds < 3600) return `${Math.round(seconds / 60)}分钟`
  return `${Math.round(seconds / 3600)}小时`
}
</script>