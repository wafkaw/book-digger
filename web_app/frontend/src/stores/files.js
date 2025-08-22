/**
 * 文件管理状态存储
 */
import { defineStore } from 'pinia'
import { ApiService } from '@/services/api'

export const useFilesStore = defineStore('files', {
  state: () => ({
    // 已上传的文件列表
    uploadedFiles: new Map(),
    
    // 上传状态
    uploadProgress: {},
    isUploading: false,
    
    // 错误状态
    uploadError: null
  }),

  getters: {
    // 获取文件列表
    filesList: (state) => Array.from(state.uploadedFiles.values()),
    
    // 获取特定文件
    getFileById: (state) => (fileId) => state.uploadedFiles.get(fileId),
    
    // 获取上传进度
    getUploadProgress: (state) => (fileId) => state.uploadProgress[fileId] || 0
  },

  actions: {
    /**
     * 上传文件
     */
    async uploadFile(file) {
      this.isUploading = true
      this.uploadError = null
      
      try {
        // 创建临时ID用于跟踪进度
        const tempId = Date.now().toString()
        this.uploadProgress[tempId] = 0
        
        const result = await ApiService.uploadFile(file, (progress) => {
          this.uploadProgress[tempId] = progress
        })
        
        // 保存文件信息
        this.uploadedFiles.set(result.fileId, {
          id: result.fileId,
          filename: result.filename,
          size: result.size,
          contentType: result.contentType,
          uploadTimestamp: result.uploadTimestamp,
          status: 'uploaded'
        })
        
        // 清理临时进度
        delete this.uploadProgress[tempId]
        
        return result
        
      } catch (error) {
        this.uploadError = error.message
        throw error
      } finally {
        this.isUploading = false
      }
    },

    /**
     * 获取文件信息
     */
    async fetchFileInfo(fileId) {
      try {
        const fileInfo = await ApiService.getFileInfo(fileId)
        
        this.uploadedFiles.set(fileId, {
          id: fileInfo.fileId,
          filename: fileInfo.filename,
          size: fileInfo.size,
          contentType: fileInfo.contentType,
          uploadTimestamp: fileInfo.uploadTimestamp,
          status: fileInfo.status
        })
        
        return fileInfo
      } catch (error) {
        console.error('Failed to fetch file info:', error)
        throw error
      }
    },

    /**
     * 删除文件
     */
    async deleteFile(fileId) {
      try {
        await ApiService.deleteFile(fileId)
        this.uploadedFiles.delete(fileId)
        return true
      } catch (error) {
        console.error('Failed to delete file:', error)
        throw error
      }
    },

    /**
     * 清理错误状态
     */
    clearError() {
      this.uploadError = null
    },

    /**
     * 验证文件
     */
    validateFile(file) {
      const errors = []
      
      // 文件类型检查
      const allowedTypes = ['.html', '.htm']
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
      if (!allowedTypes.includes(fileExtension)) {
        errors.push(`不支持的文件类型，仅支持: ${allowedTypes.join(', ')}`)
      }
      
      // 文件大小检查 (10MB)
      const maxSize = 10 * 1024 * 1024
      if (file.size > maxSize) {
        errors.push(`文件过大，最大支持 10MB`)
      }
      
      // 文件名检查
      if (file.name.length > 255) {
        errors.push('文件名过长')
      }
      
      return errors
    }
  }
})