<template>
  <div class="w-full max-w-2xl mx-auto">
    <!-- 拖拽上传区域 -->
    <div
      @drop="handleDrop"
      @dragover="handleDragOver"  
      @dragenter="handleDragEnter"
      @dragleave="handleDragLeave"
      @click="openFileDialog"
      :class="[
        'upload-zone cursor-pointer p-12 text-center transition-all duration-200',
        {
          'upload-zone-active': isDragOver,
          'upload-zone-error': hasError,
          'border-green-400 bg-green-50': uploadSuccess,
          'opacity-50 cursor-not-allowed': isUploading
        }
      ]"
    >
      <!-- 上传图标 -->
      <div class="mb-4">
        <svg 
          v-if="!isUploading && !uploadSuccess" 
          class="mx-auto h-12 w-12 text-gray-400"
          stroke="currentColor" 
          fill="none" 
          viewBox="0 0 48 48"
        >
          <path 
            d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
            stroke-width="2" 
            stroke-linecap="round" 
            stroke-linejoin="round" 
          />
        </svg>
        
        <!-- 上传中动画 -->
        <div v-if="isUploading" class="mx-auto h-12 w-12 spinner"></div>
        
        <!-- 成功图标 -->
        <svg 
          v-if="uploadSuccess" 
          class="mx-auto h-12 w-12 text-green-500"
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            stroke-linecap="round" 
            stroke-linejoin="round" 
            stroke-width="2" 
            d="M5 13l4 4L19 7"
          />
        </svg>
      </div>

      <!-- 上传文本 -->
      <div class="space-y-2">
        <p class="text-lg font-medium text-gray-900">
          <span v-if="!isUploading && !uploadSuccess">
            {{ isDragOver ? '释放文件进行上传' : '拖拽HTML文件到此处' }}
          </span>
          <span v-if="isUploading">正在上传文件...</span>
          <span v-if="uploadSuccess">文件上传成功！</span>
        </p>
        
        <p v-if="!isUploading && !uploadSuccess" class="text-sm text-gray-500">
          或 <span class="text-blue-600 font-medium">点击选择文件</span>
        </p>
        
        <!-- 文件要求说明 -->
        <div v-if="!isUploading && !uploadSuccess" class="text-xs text-gray-400 space-y-1">
          <p>支持格式: HTML (.html, .htm)</p>
          <p>最大大小: {{ maxFileSizeFormatted }}</p>
        </div>
        
        <!-- 上传进度 -->
        <div v-if="isUploading" class="w-full max-w-xs mx-auto">
          <div class="progress">
            <div 
              class="progress-bar" 
              :style="{ width: `${uploadProgress}%` }"
            ></div>
          </div>
          <p class="text-sm text-gray-600 mt-2">{{ uploadProgress }}%</p>
        </div>
        
        <!-- 成功信息 -->
        <div v-if="uploadSuccess && uploadedFile" class="text-sm text-gray-600">
          <p class="font-medium">{{ uploadedFile.filename }}</p>
          <p>{{ formatFileSize(uploadedFile.size) }}</p>
        </div>
      </div>

      <!-- 错误信息 -->
      <div v-if="hasError" class="mt-4 alert-error">
        <p class="font-medium">上传失败</p>
        <p class="text-sm mt-1">{{ errorMessage }}</p>
        <button 
          @click="clearError" 
          class="mt-2 btn-ghost text-sm"
        >
          重试
        </button>
      </div>
    </div>

    <!-- 文件选择器 (隐藏) -->
    <input
      ref="fileInput"
      type="file"
      accept=".html,.htm"
      @change="handleFileSelect"
      class="hidden"
    />
    
    <!-- 操作按钮 -->
    <div v-if="uploadSuccess && uploadedFile" class="mt-6 flex justify-center space-x-4">
      <button 
        @click="startAnalysis"
        :disabled="isCreatingTask"
        class="btn-primary px-8 py-3 text-base"
      >
        <span v-if="!isCreatingTask">开始生成知识图谱</span>
        <span v-else class="flex items-center">
          <div class="spinner w-4 h-4 mr-2"></div>
          创建任务中...
        </span>
      </button>
      
      <button 
        @click="resetUpload"
        class="btn-secondary px-6 py-3"
      >
        重新上传
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useFilesStore } from '@/stores/files'
import { useTasksStore } from '@/stores/tasks'
import { useAppStore } from '@/stores/app'

// Stores
const filesStore = useFilesStore()
const tasksStore = useTasksStore()
const appStore = useAppStore()
const router = useRouter()

// 响应式状态
const isDragOver = ref(false)
const isUploading = ref(false)
const isCreatingTask = ref(false)
const uploadProgress = ref(0)
const uploadSuccess = ref(false)
const uploadedFile = ref(null)
const errorMessage = ref('')
const fileInput = ref(null)

// 计算属性
const hasError = computed(() => !!errorMessage.value)
const maxFileSizeFormatted = computed(() => appStore.maxFileSizeFormatted)

// 拖拽处理
const handleDragOver = (e) => {
  e.preventDefault()
  e.stopPropagation()
}

const handleDragEnter = (e) => {
  e.preventDefault()
  e.stopPropagation()
  isDragOver.value = true
}

const handleDragLeave = (e) => {
  e.preventDefault()
  e.stopPropagation()
  isDragOver.value = false
}

const handleDrop = (e) => {
  e.preventDefault()
  e.stopPropagation()
  isDragOver.value = false
  
  const files = Array.from(e.dataTransfer.files)
  if (files.length > 0) {
    handleFile(files[0])
  }
}

// 文件选择处理
const openFileDialog = () => {
  if (isUploading.value) return
  fileInput.value?.click()
}

const handleFileSelect = (e) => {
  const files = Array.from(e.target.files)
  if (files.length > 0) {
    handleFile(files[0])
  }
}

// 文件处理
const handleFile = async (file) => {
  // 重置状态
  clearError()
  uploadSuccess.value = false
  
  // 验证文件
  const validationErrors = filesStore.validateFile(file)
  if (validationErrors.length > 0) {
    errorMessage.value = validationErrors.join('; ')
    return
  }
  
  // 开始上传
  isUploading.value = true
  uploadProgress.value = 0
  
  try {
    const result = await filesStore.uploadFile(file)
    
    uploadedFile.value = {
      id: result.file_id,
      filename: result.filename,
      size: result.size,
      contentType: result.content_type
    }
    
    uploadSuccess.value = true
    
    appStore.showNotification({
      type: 'success',
      title: '文件上传成功',
      message: `${result.filename} 已准备好进行分析`
    })
    
  } catch (error) {
    errorMessage.value = error.message || '上传失败'
    
    appStore.showNotification({
      type: 'error', 
      title: '文件上传失败',
      message: error.message
    })
  } finally {
    isUploading.value = false
    uploadProgress.value = 0
  }
}

// 开始分析
const startAnalysis = async () => {
  if (!uploadedFile.value) return
  
  isCreatingTask.value = true
  
  try {
    const task = await tasksStore.createTask(uploadedFile.value.id)
    
    appStore.showNotification({
      type: 'success',
      title: '任务创建成功',
      message: '正在开始分析，即将跳转到进度页面'
    })
    
    // 跳转到任务详情页
    setTimeout(() => {
      router.push(`/task/${task.task_id}`)
    }, 1000)
    
  } catch (error) {
    appStore.handleError(error, '创建任务')
  } finally {
    isCreatingTask.value = false
  }
}

// 重置上传
const resetUpload = () => {
  uploadSuccess.value = false
  uploadedFile.value = null
  clearError()
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 清除错误
const clearError = () => {
  errorMessage.value = ''
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 监听上传进度
filesStore.$subscribe((mutation, state) => {
  if (state.isUploading) {
    // 获取当前文件的上传进度
    const progressValues = Object.values(state.uploadProgress)
    if (progressValues.length > 0) {
      uploadProgress.value = Math.max(...progressValues)
    }
  }
})
</script>

<style scoped>
/* 组件特定样式 */
.upload-zone {
  min-height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

/* 拖拽状态视觉反馈 */
.upload-zone-active {
  transform: scale(1.02);
  box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.1);
}

/* 错误状态样式 */
.upload-zone-error {
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

/* 成功状态动画 */
.upload-success {
  animation: bounce 0.6s ease-in-out;
}

@keyframes bounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
</style>