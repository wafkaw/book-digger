<template>
  <div class="bg-white rounded-xl shadow-soft-lg p-6 max-w-2xl mx-auto">
    <!-- 任务标题 -->
    <div class="text-center mb-8">
      <h2 class="text-2xl font-semibold text-gray-900 mb-2">
        正在处理您的 Kindle 笔记
      </h2>
      <p class="text-gray-600">
        {{ task?.fileId ? `文件ID: ${task.fileId}` : '准备开始分析...' }}
      </p>
    </div>

    <!-- 总体进度条 -->
    <div class="mb-8">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium text-gray-700">总体进度</span>
        <span class="text-sm text-gray-500">{{ Math.round(task?.progress || 0) }}%</span>
      </div>
      <div class="progress">
        <div 
          class="progress-bar transition-all duration-500 ease-out"
          :style="{ width: `${task?.progress || 0}%` }"
          :class="{
            'bg-green-500': isCompleted,
            'bg-red-500': isFailed,
            'bg-blue-600': isRunning
          }"
        ></div>
      </div>
      
      <!-- 预计剩余时间 -->
      <div v-if="task?.estimatedRemaining && isRunning" class="text-center mt-3">
        <p class="text-sm text-gray-500">
          预计剩余时间: {{ formatTime(task.estimatedRemaining) }}
        </p>
      </div>
    </div>

    <!-- 当前状态指示器 -->
    <div class="flex items-center justify-center mb-8">
      <div class="flex items-center space-x-3">
        <!-- 状态图标 -->
        <div class="relative">
          <div 
            v-if="isRunning"
            class="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"
          ></div>
          
          <div 
            v-else-if="isCompleted"
            class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center"
          >
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          
          <div 
            v-else-if="isFailed"
            class="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center"
          >
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          
          <div 
            v-else
            class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center"
          >
            <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        
        <!-- 状态文本 -->
        <div class="text-center">
          <p class="font-medium text-gray-900">{{ statusText }}</p>
          <p class="text-sm text-gray-500">{{ stageText }}</p>
        </div>
      </div>
    </div>

    <!-- 处理步骤 -->
    <div class="space-y-4 mb-8">
      <div 
        v-for="(step, index) in processingSteps" 
        :key="index"
        class="flex items-center space-x-4 p-4 rounded-lg"
        :class="{
          'bg-green-50 border border-green-200': step.completed,
          'bg-blue-50 border border-blue-200': step.current,
          'bg-gray-50 border border-gray-200': step.pending
        }"
      >
        <!-- 步骤图标 -->
        <div class="flex-shrink-0">
          <div 
            v-if="step.completed"
            class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center"
          >
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          
          <div 
            v-else-if="step.current"
            class="w-8 h-8 border-2 border-blue-500 rounded-full flex items-center justify-center animate-pulse-soft"
          >
            <div class="w-3 h-3 bg-blue-500 rounded-full"></div>
          </div>
          
          <div 
            v-else
            class="w-8 h-8 border-2 border-gray-300 rounded-full flex items-center justify-center"
          >
            <span class="text-gray-400 text-sm font-medium">{{ index + 1 }}</span>
          </div>
        </div>
        
        <!-- 步骤信息 -->
        <div class="flex-1">
          <h3 class="font-medium" :class="{
            'text-green-800': step.completed,
            'text-blue-800': step.current,
            'text-gray-700': step.pending
          }">
            {{ step.title }}
          </h3>
          <p class="text-sm" :class="{
            'text-green-600': step.completed,
            'text-blue-600': step.current,
            'text-gray-500': step.pending
          }">
            {{ step.description }}
          </p>
          
          <!-- 当前步骤进度 -->
          <div v-if="step.current && step.progress !== undefined" class="mt-2">
            <div class="w-full bg-blue-200 rounded-full h-2">
              <div 
                class="bg-blue-500 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${step.progress}%` }"
              ></div>
            </div>
          </div>
        </div>
        
        <!-- 持续时间 -->
        <div v-if="step.duration" class="text-xs text-gray-500">
          {{ formatTime(step.duration) }}
        </div>
      </div>
    </div>

    <!-- 错误信息 -->
    <div v-if="isFailed && task?.errorMessage" class="alert-error mb-6">
      <div class="flex items-center">
        <svg class="w-5 h-5 text-red-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <p class="font-medium">处理失败</p>
          <p class="text-sm mt-1">{{ task.errorMessage }}</p>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="flex justify-center space-x-4">
      <button 
        v-if="isCompleted"
        @click="viewResults"
        class="btn-primary px-8 py-3"
      >
        查看知识图谱
      </button>
      
      <button 
        v-if="isRunning"
        @click="cancelTask"
        class="btn-secondary px-6 py-3"
        :disabled="isCancelling"
      >
        {{ isCancelling ? '取消中...' : '取消任务' }}
      </button>
      
      <button 
        v-if="isFailed"
        @click="retryTask"
        class="btn-primary px-6 py-3"
      >
        重试
      </button>
      
      <router-link 
        to="/"
        class="btn-ghost px-6 py-3"
      >
        返回首页
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTasksStore } from '@/stores/tasks'
import { useAppStore } from '@/stores/app'

// Props
const props = defineProps({
  task: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['retry', 'cancel'])

// Stores & Router
const tasksStore = useTasksStore()
const appStore = useAppStore()
const router = useRouter()

// 响应式状态
const isCancelling = ref(false)

// 计算属性
const isRunning = computed(() => 
  props.task?.status === 'running' || props.task?.status === 'pending'
)

const isCompleted = computed(() => props.task?.status === 'success')
const isFailed = computed(() => props.task?.status === 'failure')
const isCancelled = computed(() => props.task?.status === 'cancelled')

const statusText = computed(() => {
  switch (props.task?.status) {
    case 'pending': return '准备开始'
    case 'running': return '正在处理'
    case 'success': return '处理完成'
    case 'failure': return '处理失败'
    case 'cancelled': return '已取消'
    default: return '未知状态'
  }
})

const stageText = computed(() => {
  switch (props.task?.stage) {
    case 'uploaded': return '文件已上传'
    case 'parsing': return '正在解析文件结构'
    case 'ai_analysis': return 'AI 正在分析内容'
    case 'graph_generation': return '正在生成知识图谱'
    case 'completed': return '所有步骤已完成'
    default: return ''
  }
})

const processingSteps = computed(() => {
  const currentStage = props.task?.stage || 'uploaded'
  const stages = ['uploaded', 'parsing', 'ai_analysis', 'graph_generation', 'completed']
  const currentIndex = stages.indexOf(currentStage)
  
  return [
    {
      title: '文件解析',
      description: '分析 Kindle HTML 文件结构，提取标注内容',
      completed: currentIndex > 0,
      current: currentStage === 'parsing',
      pending: currentIndex < 1,
      progress: currentStage === 'parsing' ? Math.min(props.task?.progress || 0, 20) * 5 : undefined
    },
    {
      title: 'AI 语义分析',
      description: '使用人工智能提取概念、主题和人物关系',
      completed: currentIndex > 2,
      current: currentStage === 'ai_analysis',
      pending: currentIndex < 2,
      progress: currentStage === 'ai_analysis' ? Math.max(0, (props.task?.progress || 0) - 20) * 1.67 : undefined
    },
    {
      title: '知识图谱生成',
      description: '构建双向链接网络，生成 Obsidian 文件',
      completed: currentIndex > 3,
      current: currentStage === 'graph_generation',
      pending: currentIndex < 3,
      progress: currentStage === 'graph_generation' ? Math.max(0, (props.task?.progress || 0) - 80) * 5 : undefined
    },
    {
      title: '完成',
      description: '知识图谱已生成，可以查看和下载',
      completed: currentStage === 'completed',
      current: false,
      pending: currentIndex < 4
    }
  ]
})

// 方法
const viewResults = () => {
  if (props.task?.id) {
    router.push(`/graph/${props.task.id}`)
  }
}

const cancelTask = async () => {
  if (!props.task?.id || isCancelling.value) return
  
  isCancelling.value = true
  
  try {
    await tasksStore.cancelTask(props.task.id)
    emit('cancel', props.task.id)
    
    appStore.showNotification({
      type: 'info',
      title: '任务已取消',
      message: '分析任务已成功取消'
    })
  } catch (error) {
    appStore.handleError(error, '取消任务')
  } finally {
    isCancelling.value = false
  }
}

const retryTask = () => {
  emit('retry', props.task)
}

const formatTime = (seconds) => {
  if (seconds < 60) return `${Math.round(seconds)}秒`
  if (seconds < 3600) return `${Math.round(seconds / 60)}分钟`
  return `${Math.round(seconds / 3600)}小时`
}
</script>

<style scoped>
/* 自定义动画 */
@keyframes pulseSoft {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.animate-pulse-soft {
  animation: pulseSoft 2s ease-in-out infinite;
}

/* 进度条动画 */
.progress-bar {
  transition: width 0.5s ease-out, background-color 0.3s ease;
}

/* 步骤过渡动画 */
.processing-step {
  transition: all 0.3s ease;
}

/* 状态指示器动画 */
.status-indicator {
  transition: all 0.3s ease;
}
</style>