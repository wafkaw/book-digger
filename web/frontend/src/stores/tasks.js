/**
 * 任务管理状态存储
 */
import { defineStore } from 'pinia'
import { ApiService } from '@/services/api'

export const useTasksStore = defineStore('tasks', {
  state: () => ({
    // 任务列表
    tasks: new Map(),
    
    // 活跃的轮询任务
    activePolling: new Map(),
    
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
        this.tasks.set(task.task_id, {
          id: task.task_id,
          fileId: task.file_id,
          status: task.status,
          stage: task.stage,
          progress: task.progress,
          createdAt: task.created_at,
          updatedAt: task.updated_at,
          errorMessage: task.error_message,
          estimatedRemaining: task.estimated_remaining
        })
        
        this.currentTask = task.task_id
        
        // 自动开始监听任务进度
        this.startTaskMonitoring(task.task_id)
        
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
          id: task.task_id,
          fileId: task.file_id,
          status: task.status,
          stage: task.stage,
          progress: task.progress,
          createdAt: task.created_at,
          updatedAt: task.updated_at,
          errorMessage: task.error_message,
          estimatedRemaining: task.estimated_remaining
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
     * 开始监听任务进度 (轮询模式)
     */
    startTaskMonitoring(taskId) {
      // 如果已经有轮询，先停止
      if (this.activePolling.has(taskId)) {
        this.stopTaskMonitoring(taskId)
      }
      
      console.log(`开始轮询任务进度: ${taskId}`)
      
      // 立即获取一次状态
      this.fetchTask(taskId)
      
      // 设置轮询
      const pollInterval = setInterval(async () => {
        try {
          const task = await this.fetchTask(taskId)
          
          // 如果任务已完成，停止轮询
          if (['success', 'failure', 'cancelled'].includes(task.status)) {
            console.log(`任务 ${taskId} 已完成，停止轮询`)
            this.stopTaskMonitoring(taskId)
          }
          
        } catch (error) {
          console.error(`轮询任务状态失败 ${taskId}:`, error)
          // 继续轮询，不停止
        }
      }, 2000) // 每2秒轮询一次
      
      this.activePolling.set(taskId, pollInterval)
    },

    /**
     * 停止监听任务进度
     */
    stopTaskMonitoring(taskId) {
      const pollInterval = this.activePolling.get(taskId)
      if (pollInterval) {
        clearInterval(pollInterval)
        this.activePolling.delete(taskId)
        console.log(`停止轮询任务: ${taskId}`)
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
     * 清理所有轮询任务
     */
    cleanup() {
      this.activePolling.forEach((interval, taskId) => {
        clearInterval(interval)
      })
      this.activePolling.clear()
    }
  }
})