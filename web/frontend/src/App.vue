<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- 简洁的顶部导航 -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="container-responsive py-4">
        <div class="flex items-center justify-between">
          <!-- Logo和标题 -->
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h1 class="text-xl font-semibold text-gray-900">Kindle 知识图谱</h1>
              <p class="text-sm text-gray-500">将笔记转化为可视化知识网络</p>
            </div>
          </div>
          
          <!-- 导航链接 -->
          <div class="flex items-center space-x-6">
            <router-link 
              to="/"
              class="text-gray-600 hover:text-gray-900 transition-colors"
              :class="{ 'text-blue-600 font-medium': $route.path === '/' }"
            >
              上传分析
            </router-link>
            <router-link 
              to="/tasks"
              class="text-gray-600 hover:text-gray-900 transition-colors"
              :class="{ 'text-blue-600 font-medium': $route.path.startsWith('/tasks') }"
            >
              任务历史
            </router-link>
            <a 
              href="/api/v1/health" 
              target="_blank"
              class="text-gray-400 hover:text-gray-600 transition-colors text-sm"
            >
              API状态
            </a>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主要内容区域 -->
    <main class="flex-1">
      <router-view v-slot="{ Component, route }">
        <transition 
          name="page" 
          mode="out-in"
          enter-active-class="transition-all duration-300 ease-out"
          enter-from-class="opacity-0 transform translate-y-4"
          enter-to-class="opacity-100 transform translate-y-0"
          leave-active-class="transition-all duration-200 ease-in"
          leave-from-class="opacity-100 transform translate-y-0"
          leave-to-class="opacity-0 transform -translate-y-4"
        >
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </main>

    <!-- 全局通知 -->
    <div id="notifications" class="fixed top-4 right-4 z-50 space-y-2">
      <!-- 通知组件将在这里渲染 -->
    </div>

    <!-- 简洁的页脚 -->
    <footer class="bg-white border-t border-gray-200 mt-16">
      <div class="container-responsive py-8">
        <div class="flex items-center justify-between text-sm text-gray-500">
          <div class="flex items-center space-x-4">
            <span>&copy; 2024 Kindle Knowledge Graph</span>
            <span class="text-gray-300">|</span>
            <span>基于 AI 的知识图谱生成</span>
          </div>
          <div class="flex items-center space-x-4">
            <a href="https://github.com" class="hover:text-gray-700 transition-colors">
              GitHub
            </a>
            <a href="/docs" class="hover:text-gray-700 transition-colors">
              API 文档
            </a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
// 页面级配置和状态管理
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  // 应用启动时的初始化逻辑
  console.log('Kindle Knowledge Graph App initialized')
})
</script>

<style scoped>
/* 路由过渡动画 */
.page-enter-active,
.page-leave-active {
  transition: all 0.3s ease;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>