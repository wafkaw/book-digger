<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="container-responsive max-w-4xl">
      <div class="bg-white rounded-xl shadow-soft-lg p-8 md:p-12">
        <h1 class="text-3xl font-bold text-gray-900 mb-6">关于 Kindle 知识图谱生成器</h1>
        
        <div class="prose prose-gray max-w-none">
          <p class="text-xl text-gray-600 mb-8">
            一个现代化的Web应用，将您的Kindle阅读笔记转化为可视化的知识图谱
          </p>
          
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">功能特性</h2>
          <ul class="space-y-2 mb-8">
            <li class="flex items-start">
              <svg class="w-5 h-5 text-green-500 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span>AI 语义分析：智能提取核心概念、主题和人物关系</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-green-500 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span>知识图谱生成：创建125+个互联节点的双向链接网络</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-green-500 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span>实时进度追踪：WebSocket驱动的实时处理状态显示</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-green-500 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span>Obsidian兼容：生成完整的知识库文件，支持本地导入</span>
            </li>
          </ul>
          
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">技术架构</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div>
              <h3 class="text-lg font-medium text-gray-900 mb-3">后端技术</h3>
              <ul class="space-y-1 text-gray-600">
                <li>• FastAPI - 现代异步Web框架</li>
                <li>• Celery - 分布式任务队列</li>
                <li>• Redis - 消息代理和缓存</li>
                <li>• SQLAlchemy - 数据库ORM</li>
                <li>• PostgreSQL - 生产数据库</li>
              </ul>
            </div>
            <div>
              <h3 class="text-lg font-medium text-gray-900 mb-3">前端技术</h3>
              <ul class="space-y-1 text-gray-600">
                <li>• Vue 3 - 渐进式JavaScript框架</li>
                <li>• Vite - 快速构建工具</li>
                <li>• TailwindCSS - 实用至上的CSS框架</li>
                <li>• Pinia - 状态管理</li>
                <li>• Cytoscape.js - 图谱可视化</li>
              </ul>
            </div>
          </div>
          
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">使用指南</h2>
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
            <h3 class="font-medium text-blue-900 mb-3">第一步：导出Kindle笔记</h3>
            <p class="text-blue-800 text-sm mb-2">
              在Kindle阅读器或Kindle应用中，找到要导出的书籍，选择"导出笔记"功能，保存为HTML格式。
            </p>
            
            <h3 class="font-medium text-blue-900 mb-3 mt-4">第二步：上传文件</h3>
            <p class="text-blue-800 text-sm mb-2">
              在首页拖拽HTML文件到上传区域，或点击选择文件。支持最大10MB的HTML文件。
            </p>
            
            <h3 class="font-medium text-blue-900 mb-3 mt-4">第三步：等待分析</h3>
            <p class="text-blue-800 text-sm mb-2">
              AI将自动分析文件内容，通常需要5-6分钟。您可以实时查看处理进度。
            </p>
            
            <h3 class="font-medium text-blue-900 mb-3 mt-4">第四步：探索知识图谱</h3>
            <p class="text-blue-800 text-sm">
              分析完成后，您可以在Web端查看交互式知识图谱，或下载Obsidian文件包。
            </p>
          </div>
          
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">系统要求</h2>
          <div class="bg-gray-50 rounded-lg p-6 mb-8">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 class="font-medium text-gray-900 mb-2">文件要求</h3>
                <ul class="text-sm text-gray-600 space-y-1">
                  <li>• 格式：HTML (.html, .htm)</li>
                  <li>• 大小：最大 10MB</li>
                  <li>• 来源：Kindle导出的笔记文件</li>
                </ul>
              </div>
              <div>
                <h3 class="font-medium text-gray-900 mb-2">浏览器支持</h3>
                <ul class="text-sm text-gray-600 space-y-1">
                  <li>• Chrome 88+</li>
                  <li>• Firefox 78+</li>
                  <li>• Safari 14+</li>
                  <li>• Edge 88+</li>
                </ul>
              </div>
            </div>
          </div>
          
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">开源信息</h2>
          <p class="text-gray-600 mb-4">
            本项目是开源软件，基于MIT许可证发布。我们欢迎社区贡献和反馈。
          </p>
          
          <div class="flex flex-wrap gap-4">
            <a href="https://github.com" class="btn-secondary" target="_blank">
              <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
              </svg>
              GitHub仓库
            </a>
            
            <a href="/docs" class="btn-secondary" target="_blank">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              API文档
            </a>
            
            <router-link to="/tasks" class="btn-primary">
              查看任务历史
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 关于页面静态内容，无需响应式逻辑
</script>