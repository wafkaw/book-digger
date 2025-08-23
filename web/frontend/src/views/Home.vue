<template>
  <div class="min-h-screen bg-gradient-subtle">
    <!-- 英雄区域 -->
    <section class="container-responsive pt-16 pb-24">
      <div class="text-center max-w-4xl mx-auto">
        <!-- 主标题 -->
        <h1 class="text-4xl md:text-6xl font-bold text-gray-900 tracking-tight mb-6">
          将 <span class="text-blue-600">Kindle 笔记</span><br>
          转化为知识图谱
        </h1>
        
        <!-- 副标题 -->
        <p class="text-xl md:text-2xl text-gray-600 mb-12 leading-relaxed">
          基于 AI 的语义分析，自动生成 <span class="font-medium">125+</span> 个互联节点的知识网络<br>
          让你的阅读笔记变成可视化的智慧宝库
        </p>
        
        <!-- 特性亮点 -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <div class="bg-white rounded-xl p-6 shadow-soft">
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">AI 语义分析</h3>
            <p class="text-gray-600 text-sm">
              深度理解文本含义，提取核心概念、主题和人物关系
            </p>
          </div>
          
          <div class="bg-white rounded-xl p-6 shadow-soft">
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">实时处理</h3>
            <p class="text-gray-600 text-sm">
              5-6分钟内完成分析，实时显示处理进度和状态
            </p>
          </div>
          
          <div class="bg-white rounded-xl p-6 shadow-soft">
            <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">知识网络</h3>
            <p class="text-gray-600 text-sm">
              生成Obsidian兼容的双向链接知识库，支持图谱可视化
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- 文件上传区域 -->
    <section class="container-responsive pb-24">
      <div class="max-w-4xl mx-auto">
        <div class="bg-white rounded-2xl shadow-soft-lg p-8 md:p-12">
          <div class="text-center mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-3">
              开始创建你的知识图谱
            </h2>
            <p class="text-gray-600">
              上传从 Kindle 导出的 HTML 文件，我们将为你生成智能知识网络
            </p>
          </div>
          
          <!-- 文件上传组件 -->
          <FileUpload />
        </div>
      </div>
    </section>

    <!-- 使用流程 -->
    <section class="container-responsive pb-24">
      <div class="max-w-4xl mx-auto text-center">
        <h2 class="text-3xl font-bold text-gray-900 mb-4">
          如何使用
        </h2>
        <p class="text-gray-600 mb-12">
          三个简单步骤，将你的 Kindle 笔记转化为知识图谱
        </p>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- 步骤1 -->
          <div class="relative">
            <div class="bg-white rounded-xl p-8 shadow-soft">
              <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-6 mx-auto">
                <span class="text-2xl font-bold text-blue-600">1</span>
              </div>
              <h3 class="text-xl font-semibold text-gray-900 mb-3">导出 Kindle 笔记</h3>
              <p class="text-gray-600 text-sm leading-relaxed">
                在 Kindle 阅读器中选择"导出笔记"，保存为 HTML 格式文件
              </p>
            </div>
            
            <!-- 连接线 -->
            <div class="hidden md:block absolute top-1/2 right-0 transform translate-x-1/2 -translate-y-1/2">
              <svg class="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
          
          <!-- 步骤2 -->
          <div class="relative">
            <div class="bg-white rounded-xl p-8 shadow-soft">
              <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-6 mx-auto">
                <span class="text-2xl font-bold text-blue-600">2</span>
              </div>
              <h3 class="text-xl font-semibold text-gray-900 mb-3">上传并分析</h3>
              <p class="text-gray-600 text-sm leading-relaxed">
                将 HTML 文件拖拽到上方区域，AI 将自动分析并提取知识结构
              </p>
            </div>
            
            <!-- 连接线 -->
            <div class="hidden md:block absolute top-1/2 right-0 transform translate-x-1/2 -translate-y-1/2">
              <svg class="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
          
          <!-- 步骤3 -->
          <div class="bg-white rounded-xl p-8 shadow-soft">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-6 mx-auto">
              <span class="text-2xl font-bold text-blue-600">3</span>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-3">探索知识网络</h3>
            <p class="text-gray-600 text-sm leading-relaxed">
              在Web端查看交互式知识图谱，或下载Obsidian知识库文件
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- 示例展示 -->
    <section class="bg-gray-100 py-24">
      <div class="container-responsive">
        <div class="max-w-4xl mx-auto text-center">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">
            生成的知识图谱
          </h2>
          <p class="text-gray-600 mb-12">
            以《当尼采哭泣》为例，展示生成的知识网络结构
          </p>
          
          <!-- 示例统计 -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
            <div class="bg-white rounded-lg p-6 shadow-soft">
              <div class="text-3xl font-bold text-blue-600 mb-1">70</div>
              <div class="text-sm text-gray-600">核心概念</div>
            </div>
            <div class="bg-white rounded-lg p-6 shadow-soft">
              <div class="text-3xl font-bold text-green-600 mb-1">38</div>
              <div class="text-sm text-gray-600">主题分类</div>
            </div>
            <div class="bg-white rounded-lg p-6 shadow-soft">
              <div class="text-3xl font-bold text-purple-600 mb-1">17</div>
              <div class="text-sm text-gray-600">相关人物</div>
            </div>
            <div class="bg-white rounded-lg p-6 shadow-soft">
              <div class="text-3xl font-bold text-orange-600 mb-1">125</div>
              <div class="text-sm text-gray-600">互联节点</div>
            </div>
          </div>
          
          <!-- 示例概念 -->
          <div class="bg-white rounded-xl p-8 shadow-soft-lg">
            <h3 class="text-xl font-semibold text-gray-900 mb-6">核心概念网络</h3>
            <div class="flex flex-wrap justify-center gap-3">
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800">
                存在主义哲学
              </span>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-800">
                心理防御机制
              </span>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-purple-100 text-purple-800">
                人际关系
              </span>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-red-100 text-red-800">
                生命意义
              </span>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-yellow-100 text-yellow-800">
                自我认同
              </span>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-indigo-100 text-indigo-800">
                永劫回归
              </span>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-pink-100 text-pink-800">
                死亡意识
              </span>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-800">
                友谊本质
              </span>
            </div>
            <p class="text-gray-500 text-sm mt-4">
              每个概念都与相关概念建立智能双向链接，形成密集的知识网络
            </p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import FileUpload from '@/components/FileUpload.vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

onMounted(() => {
  // 页面加载时的初始化
  console.log('Home page loaded')
})
</script>

<style scoped>
/* 页面特定样式 */
.hero-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 特性卡片悬浮效果 */
.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}
</style>