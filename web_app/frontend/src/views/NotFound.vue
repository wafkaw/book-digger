<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="max-w-md mx-auto text-center">
      <!-- 404图标 -->
      <div class="mb-8">
        <svg class="w-24 h-24 text-gray-400 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" 
                d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      
      <!-- 错误信息 -->
      <h1 class="text-6xl font-bold text-gray-900 mb-4">404</h1>
      <h2 class="text-2xl font-semibold text-gray-700 mb-4">页面未找到</h2>
      <p class="text-gray-600 mb-8">
        抱歉，您访问的页面不存在或已被移动。
      </p>
      
      <!-- 返回按钮 -->
      <div class="space-y-4">
        <router-link to="/" class="btn-primary inline-flex">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          返回首页
        </router-link>
        
        <div class="text-center">
          <router-link to="/tasks" class="text-blue-600 hover:text-blue-700 text-sm">
            或查看任务历史
          </router-link>
        </div>
      </div>
      
      <!-- 帮助链接 -->
      <div class="mt-12 pt-8 border-t border-gray-200">
        <p class="text-sm text-gray-500 mb-4">需要帮助？</p>
        <div class="flex justify-center space-x-6 text-sm">
          <router-link to="/about" class="text-gray-600 hover:text-gray-900">
            使用指南
          </router-link>
          <a href="/docs" target="_blank" class="text-gray-600 hover:text-gray-900">
            API文档
          </a>
          <a href="https://github.com" target="_blank" class="text-gray-600 hover:text-gray-900">
            GitHub
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 404页面静态内容，无需响应式逻辑
</script>