/**
 * 应用全局状态存储
 */
import { defineStore } from 'pinia'
import { ApiService } from '@/services/api'

export const useAppStore = defineStore('app', {
  state: () => ({
    // 应用信息
    appTitle: 'Kindle 知识图谱生成器',
    appVersion: '1.0.0',
    
    // 系统状态
    isOnline: navigator.onLine,
    apiHealth: null,
    lastHealthCheck: null,
    
    // UI状态
    sidebarOpen: false,
    theme: 'light',
    
    // 通知系统
    notifications: [],
    
    // 加载状态
    isInitializing: false,
    globalLoading: false,
    
    // 配置
    config: {
      maxFileSize: 10 * 1024 * 1024, // 10MB
      allowedExtensions: ['.html', '.htm'],
      apiTimeout: 30000,
      wsHeartbeatInterval: 30000
    }
  }),

  getters: {
    // 是否健康
    isHealthy: (state) => state.apiHealth?.status === 'healthy',
    
    // 未读通知数量
    unreadNotifications: (state) => state.notifications.filter(n => !n.read).length,
    
    // 格式化文件大小限制
    maxFileSizeFormatted: (state) => {
      const bytes = state.config.maxFileSize
      return `${Math.round(bytes / 1024 / 1024)}MB`
    }
  },

  actions: {
    /**
     * 应用初始化
     */
    async initialize() {
      this.isInitializing = true
      
      try {
        // 检查API健康状态
        await this.checkHealth()
        
        // 设置在线状态监听
        this.setupOnlineStatusListener()
        
        // 设置定期健康检查
        this.setupHealthCheckInterval()
        
        console.log('App initialized successfully')
        
      } catch (error) {
        console.error('App initialization failed:', error)
        this.showNotification({
          type: 'error',
          title: '应用初始化失败',
          message: '无法连接到服务器，请检查网络连接'
        })
      } finally {
        this.isInitializing = false
      }
    },

    /**
     * 检查API健康状态
     */
    async checkHealth() {
      try {
        const health = await ApiService.detailedHealthCheck()
        this.apiHealth = health
        this.lastHealthCheck = new Date()
        
        if (!this.isHealthy) {
          this.showNotification({
            type: 'warning',
            title: '服务状态异常',
            message: '部分服务组件不可用，可能影响正常使用'
          })
        }
        
        return health
      } catch (error) {
        this.apiHealth = { status: 'unhealthy', error: error.message }
        this.lastHealthCheck = new Date()
        throw error
      }
    },

    /**
     * 设置在线状态监听
     */
    setupOnlineStatusListener() {
      window.addEventListener('online', () => {
        this.isOnline = true
        this.checkHealth()
        this.showNotification({
          type: 'success',
          title: '网络已恢复',
          message: '已重新连接到服务器'
        })
      })
      
      window.addEventListener('offline', () => {
        this.isOnline = false
        this.showNotification({
          type: 'warning',
          title: '网络连接断开',
          message: '请检查网络连接'
        })
      })
    },

    /**
     * 设置定期健康检查
     */
    setupHealthCheckInterval() {
      // 每30秒检查一次健康状态
      setInterval(async () => {
        if (this.isOnline) {
          try {
            await this.checkHealth()
          } catch (error) {
            // 静默失败，避免过多通知
            console.warn('Health check failed:', error.message)
          }
        }
      }, 30000)
    },

    /**
     * 显示通知
     */
    showNotification(notification) {
      const id = Date.now().toString()
      const newNotification = {
        id,
        type: 'info', // info, success, warning, error
        title: '通知',
        message: '',
        autoClose: true,
        duration: 5000,
        read: false,
        timestamp: new Date(),
        ...notification
      }
      
      this.notifications.unshift(newNotification)
      
      // 自动关闭通知
      if (newNotification.autoClose) {
        setTimeout(() => {
          this.removeNotification(id)
        }, newNotification.duration)
      }
      
      // 限制通知数量
      if (this.notifications.length > 50) {
        this.notifications = this.notifications.slice(0, 50)
      }
    },

    /**
     * 移除通知
     */
    removeNotification(id) {
      const index = this.notifications.findIndex(n => n.id === id)
      if (index > -1) {
        this.notifications.splice(index, 1)
      }
    },

    /**
     * 标记通知为已读
     */
    markNotificationAsRead(id) {
      const notification = this.notifications.find(n => n.id === id)
      if (notification) {
        notification.read = true
      }
    },

    /**
     * 清除所有通知
     */
    clearAllNotifications() {
      this.notifications = []
    },

    /**
     * 切换侧边栏
     */
    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen
    },

    /**
     * 切换主题
     */
    toggleTheme() {
      this.theme = this.theme === 'light' ? 'dark' : 'light'
      // 保存到localStorage
      localStorage.setItem('theme', this.theme)
      // 应用到document
      document.documentElement.className = this.theme
    },

    /**
     * 设置全局加载状态
     */
    setGlobalLoading(loading) {
      this.globalLoading = loading
    },

    /**
     * 错误处理
     */
    handleError(error, context = '') {
      console.error(`Error in ${context}:`, error)
      
      let message = '发生未知错误'
      if (typeof error === 'string') {
        message = error
      } else if (error.message) {
        message = error.message
      }
      
      this.showNotification({
        type: 'error',
        title: '操作失败',
        message,
        autoClose: true,
        duration: 8000
      })
    }
  }
})