/**
 * API服务模块 - 统一的HTTP请求处理
 */
import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 添加请求时间戳用于调试
    config.metadata = { startTime: new Date() }
    console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`)
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    // 记录响应时间
    const duration = new Date() - response.config.metadata.startTime
    console.log(`API Response: ${response.config.method.toUpperCase()} ${response.config.url} - ${duration}ms`)
    
    // 如果后端返回包装格式 {success, message, data}，提取data字段
    if (response.data && typeof response.data === 'object' && 'data' in response.data) {
      return response.data.data
    }
    
    return response.data
  },
  error => {
    const duration = new Date() - error.config?.metadata?.startTime
    console.error(`API Error: ${error.config?.method?.toUpperCase()} ${error.config?.url} - ${duration}ms`, error.response?.data || error.message)
    
    // 统一错误处理
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || '请求失败'
    
    return Promise.reject({
      status: error.response?.status || 0,
      message: errorMessage,
      data: error.response?.data
    })
  }
)

/**
 * API服务类
 */
export class ApiService {
  // 健康检查
  static async healthCheck() {
    return api.get('/health')
  }

  static async detailedHealthCheck() {
    return api.get('/health/detailed')
  }

  // 文件管理
  static async uploadFile(file, onProgress = null) {
    const formData = new FormData()
    formData.append('file', file)
    
    return api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: progressEvent => {
        if (onProgress) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(percentCompleted)
        }
      }
    })
  }

  static async getFileInfo(fileId) {
    return api.get(`/files/${fileId}`)
  }

  static async deleteFile(fileId) {
    return api.delete(`/files/${fileId}`)
  }

  // 任务管理
  static async createTask(fileId, config = {}) {
    return api.post('/tasks', {
      file_id: fileId,
      config
    })
  }

  static async getTask(taskId) {
    return api.get(`/tasks/${taskId}`)
  }

  static async getTaskResult(taskId) {
    return api.get(`/tasks/${taskId}/result`)
  }

  static async cancelTask(taskId) {
    return api.delete(`/tasks/${taskId}`)
  }

  static async listTasks(limit = 50, offset = 0) {
    return api.get(`/tasks?limit=${limit}&offset=${offset}`)
  }

  // 图谱相关API
  static async getGraphData(taskId) {
    return api.get(`/graph/tasks/${taskId}/graph`)
  }

  static async searchGraphNodes(query, nodeType = null) {
    const params = { q: query }
    if (nodeType) {
      params.type = nodeType
    }
    return api.get('/graph/search', { params })
  }

  static async getNodeNeighbors(nodeId) {
    return api.get(`/graph/nodes/${nodeId}/neighbors`)
  }

  static async getGraphStats() {
    return api.get('/graph/stats')
  }

  static async exportGraph(taskId, format = 'json') {
    return api.get(`/graph/export/${taskId}`, { 
      params: { format }
    })
  }

  // WebSocket连接管理
  static createTaskWebSocket(taskId) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/api/v1/tasks/${taskId}/ws`
    return new WebSocket(wsUrl)
  }
}

export default api