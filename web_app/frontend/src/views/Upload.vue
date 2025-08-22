<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="container-responsive max-w-3xl">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-4">
          上传 Kindle 笔记文件
        </h1>
        <p class="text-lg text-gray-600">
          选择您从 Kindle 导出的 HTML 文件，我们将为您生成知识图谱
        </p>
      </div>

      <!-- 文件上传组件 -->
      <FileUpload 
        @upload-success="handleUploadSuccess"
        @upload-error="handleUploadError"
      />
      
      <!-- 上传状态 -->
      <div v-if="uploadStatus" class="mt-6">
        <div v-if="uploadStatus === 'success'" class="alert-success">
          <h3 class="font-semibold">上传成功！</h3>
          <p>文件已成功上传，正在跳转到处理页面...</p>
        </div>
        <div v-else-if="uploadStatus === 'error'" class="alert-error">
          <h3 class="font-semibold">上传失败</h3>
          <p>{{ errorMessage }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import FileUpload from '@/components/FileUpload.vue'
import { useAppStore } from '@/stores/app'

const router = useRouter()
const appStore = useAppStore()

const uploadStatus = ref(null)
const errorMessage = ref('')

const handleUploadSuccess = (response) => {
  uploadStatus.value = 'success'
  
  // 显示成功消息
  appStore.showNotification({
    type: 'success',
    title: '上传成功',
    message: '文件已成功上传，正在开始分析...'
  })
  
  // 跳转到任务详情页面
  setTimeout(() => {
    if (response.taskId) {
      router.push(`/task/${response.taskId}`)
    } else {
      router.push('/tasks')
    }
  }, 2000)
}

const handleUploadError = (error) => {
  uploadStatus.value = 'error'
  errorMessage.value = error.message || '上传过程中出现未知错误'
  
  appStore.showNotification({
    type: 'error',
    title: '上传失败',
    message: errorMessage.value
  })
}
</script>

<style scoped>
/* 页面特定样式 */
</style>