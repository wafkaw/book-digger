/**
 * 任务管理状态存储
 */
import { defineStore } from 'pinia'
import { ApiService } from '@/services/api'

export const useTasksStore = defineStore('tasks', {
  state: () => ({
    // 任务列表
    tasks: new Map(),
    
    // 活跃的WebSocket连接
    activeConnections: new Map(),
    
    // 当前任务状态
    currentTask: null,
    
    // 加载状态
    isLoading: false,
    
    // 错误状态
    error: null
  }),

  getters: {
    // 获取任务列表（按创建时间倒序）
    tasksList: (state) => {
      return Array.from(state.tasks.values())
        .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    },
    
    // 获取特定任务
    getTaskById: (state) => (taskId) => state.tasks.get(taskId),
    
    // 获取运行中的任务
    runningTasks: (state) => {
      return Array.from(state.tasks.values())
        .filter(task => task.status === 'running' || task.status === 'pending')
    },
    
    // 获取已完成的任务
    completedTasks: (state) => {
      return Array.from(state.tasks.values())
        .filter(task => task.status === 'success')
    },
    
    // 获取失败的任务
    failedTasks: (state) => {
      return Array.from(state.tasks.values())
        .filter(task => task.status === 'failure')
    }
  },

  actions: {
    /**
     * 创建新任务
     */
    async createTask(fileId, config = {}) {
      this.isLoading = true
      this.error = null
      
      try {
        const task = await ApiService.createTask(fileId, config)
        
        // 保存任务信息
        this.tasks.set(task.taskId, {
          id: task.taskId,
          fileId: task.fileId,
          status: task.status,
          stage: task.stage,
          progress: task.progress,
          createdAt: task.createdAt,
          updatedAt: task.updatedAt,
          errorMessage: task.errorMessage,
          estimatedRemaining: task.estimatedRemaining
        })
        
        this.currentTask = task.taskId
        
        // 自动开始监听任务进度
        this.startTaskMonitoring(task.taskId)
        
        return task
        
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 获取任务信息
     */
    async fetchTask(taskId) {
      try {
        const task = await ApiService.getTask(taskId)
        
        this.tasks.set(taskId, {
          id: task.taskId,
          fileId: task.fileId,
          status: task.status,
          stage: task.stage,
          progress: task.progress,
          createdAt: task.createdAt,
          updatedAt: task.updatedAt,
          errorMessage: task.errorMessage,
          estimatedRemaining: task.estimatedRemaining
        })
        
        return task
      } catch (error) {
        console.error('Failed to fetch task:', error)
        throw error
      }
    },

    /**
     * 获取任务结果
     */
    async fetchTaskResult(taskId) {
      try {
        const result = await ApiService.getTaskResult(taskId)
        
        // 更新任务信息，添加结果数据
        const task = this.tasks.get(taskId)
        if (task) {
          this.tasks.set(taskId, {
            ...task,
            result: result
          })
        }
        
        return result
      } catch (error) {
        console.error('Failed to fetch task result:', error)
        throw error
      }
    },

    /**
     * 取消任务
     */
    async cancelTask(taskId) {
      try {
        await ApiService.cancelTask(taskId)
        
        // 停止监听
        this.stopTaskMonitoring(taskId)
        
        // 更新任务状态
        const task = this.tasks.get(taskId)
        if (task) {
          this.tasks.set(taskId, {
            ...task,
            status: 'cancelled',
            progress: task.progress // 保持当前进度
          })
        }
        
        return true
      } catch (error) {
        console.error('Failed to cancel task:', error)
        throw error
      }
    },

    /**
     * 获取任务列表
     */
    async fetchTasks(limit = 50, offset = 0) {
      this.isLoading = true
      
      try {
        const tasks = await ApiService.listTasks(limit, offset)
        
        // 批量更新任务信息
        tasks.forEach(task => {
          this.tasks.set(task.id, {
            id: task.id,
            fileId: task.fileId,
            status: task.status,
            stage: task.stage,
            progress: task.progress,
            createdAt: task.createdAt,
            updatedAt: task.updatedAt,
            errorMessage: task.errorMessage,
            estimatedRemaining: task.estimatedRemaining
          })
        })
        
        return tasks
        
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 开始监听任务进度 (WebSocket)
     */
    startTaskMonitoring(taskId) {
      // 如果已经有连接，先关闭
      if (this.activeConnections.has(taskId)) {
        this.stopTaskMonitoring(taskId)
      }
      
      try {
        const ws = ApiService.createTaskWebSocket(taskId)
        
        ws.onopen = () => {
          console.log(`WebSocket connected for task ${taskId}`)
        }
        
        ws.onmessage = (event) => {
          const data = JSON.parse(event.data)
          this.handleTaskUpdate(taskId, data)
        }
        
        ws.onerror = (error) => {
          console.error(`WebSocket error for task ${taskId}:`, error)
        }
        
        ws.onclose = () => {
          console.log(`WebSocket closed for task ${taskId}`)
          this.activeConnections.delete(taskId)
        }
        
        this.activeConnections.set(taskId, ws)
        
      } catch (error) {
        console.error(`Failed to create WebSocket for task ${taskId}:`, error)
      }
    },

    /**
     * 停止监听任务进度
     */
    stopTaskMonitoring(taskId) {
      const ws = this.activeConnections.get(taskId)
      if (ws) {
        ws.close()
        this.activeConnections.delete(taskId)
      }
    },

    /**
     * 处理任务更新
     */
    handleTaskUpdate(taskId, data) {
      const task = this.tasks.get(taskId)
      if (!task) return
      
      // 更新任务状态
      this.tasks.set(taskId, {
        ...task,
        status: data.status,
        stage: data.stage,
        progress: data.progress,
        updatedAt: data.timestamp,
        errorMessage: data.errorMessage,
        estimatedRemaining: data.estimatedRemaining
      })
      
      // 如果任务完成，停止监听
      if (['success', 'failure', 'cancelled'].includes(data.status)) {
        this.stopTaskMonitoring(taskId)
      }
      
      console.log(`Task ${taskId} updated:`, data)
    },

    /**
     * 清理错误状态
     */
    clearError() {
      this.error = null
    },

    /**
     * 清理所有WebSocket连接
     */
    cleanup() {
      this.activeConnections.forEach((ws, taskId) => {
        ws.close()
      })
      this.activeConnections.clear()
    }
  }
})