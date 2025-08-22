"""
完整版FastAPI应用 - 包含所有功能
"""
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Kindle知识图谱API",
    version="1.0.0",
    debug=True,
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 基础路由
@app.get("/")
async def root():
    return {"message": "Kindle知识图谱API服务已启动"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "full-api"}

# 导入图谱API
from app.api.v1.endpoints.graph import router as graph_router
app.include_router(graph_router, prefix="/api/v1/graph", tags=["graph"])

# Mock文件上传API（简化版）
from fastapi import UploadFile, File, HTTPException
from typing import Dict, Any
import uuid
import os

@app.post("/api/v1/files/upload")
async def upload_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """简化版文件上传API"""
    
    # 验证文件类型
    if not file.filename.lower().endswith('.html'):
        raise HTTPException(
            status_code=400,
            detail="只支持HTML文件格式"
        )
    
    # 生成文件ID和任务ID
    file_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    
    # 模拟保存文件（实际项目中这里会保存到磁盘）
    file_size = 0
    if hasattr(file, 'size'):
        file_size = file.size
    else:
        # 读取文件内容获取大小
        content = await file.read()
        file_size = len(content)
        await file.seek(0)  # 重置文件指针
    
    return {
        "success": True,
        "message": "文件上传成功",
        "data": {
            "fileId": file_id,
            "taskId": task_id,
            "filename": file.filename,
            "size": file_size,
            "contentType": file.content_type or "text/html"
        }
    }

from pydantic import BaseModel
from typing import Optional

# 简单的内存存储来维护任务和文件的关系
task_file_mapping = {}

class CreateTaskRequest(BaseModel):
    fileId: str
    config: Optional[dict] = {}

@app.post("/api/v1/tasks")
async def create_analysis_task(request: CreateTaskRequest) -> Dict[str, Any]:
    """创建分析任务API"""
    
    if not request.fileId:
        raise HTTPException(
            status_code=400,
            detail="缺少文件ID"
        )
    
    task_id = str(uuid.uuid4())
    
    # 保存任务和文件的映射关系
    task_file_mapping[task_id] = request.fileId
    
    return {
        "success": True,
        "message": "分析任务创建成功",
        "data": {
            "taskId": task_id,
            "fileId": request.fileId,
            "status": "pending",
            "progress": 0.0,
            "createdAt": "2025-08-22T01:00:00Z"
        }
    }

@app.get("/api/v1/tasks")
async def list_tasks(
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """获取任务列表API"""
    
    # 模拟任务列表
    mock_tasks = [
        {
            "id": "task-1",
            "status": "success",
            "progress": 100.0,
            "fileId": "file-1",
            "createdAt": "2025-08-22T01:00:00Z",
            "completedAt": "2025-08-22T01:06:00Z"
        },
        {
            "id": "task-2", 
            "status": "running",
            "progress": 45.0,
            "fileId": "file-2",
            "createdAt": "2025-08-22T01:10:00Z"
        }
    ]
    
    return {
        "success": True,
        "message": "获取任务列表成功",
        "data": {
            "tasks": mock_tasks[offset:offset+limit],
            "total": len(mock_tasks),
            "limit": limit,
            "offset": offset
        }
    }

@app.get("/api/v1/tasks/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """获取任务状态API"""
    
    # 获取真实的文件ID
    file_id = task_file_mapping.get(task_id, "mock-file-id")
    
    # 模拟任务已完成
    return {
        "success": True,
        "message": "获取任务状态成功",
        "data": {
            "taskId": task_id,
            "status": "success",
            "progress": 100.0,
            "fileId": file_id,
            "result": {
                "totalNodes": 133,
                "totalEdges": 928,
                "processingTime": 350
            },
            "createdAt": "2025-08-22T01:00:00Z",
            "completedAt": "2025-08-22T01:06:00Z"
        }
    }

@app.get("/api/v1/tasks/{task_id}/result")
async def get_task_result(task_id: str) -> Dict[str, Any]:
    """获取任务结果API"""
    
    return {
        "success": True,
        "message": "获取任务结果成功", 
        "data": {
            "taskId": task_id,
            "result": {
                "totalHighlights": 34,
                "conceptsCount": 70,
                "themesCount": 38,
                "peopleCount": 17,
                "processingTime": 350,
                "downloadUrl": f"/api/v1/tasks/{task_id}/download"
            }
        }
    }

@app.get("/api/v1/files/{file_id}")
async def get_file_info(file_id: str) -> Dict[str, Any]:
    """获取文件信息API"""
    
    return {
        "success": True,
        "message": "获取文件信息成功",
        "data": {
            "fileId": file_id,
            "filename": "蒙田随笔 - Notebook.html",
            "size": 9581,
            "contentType": "text/html",
            "uploadTimestamp": "2025-08-22T02:35:00Z",
            "status": "uploaded"
        }
    }

@app.websocket("/api/v1/tasks/{task_id}/ws")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket端点用于任务进度更新"""
    await websocket.accept()
    
    try:
        # 模拟发送任务完成状态
        await asyncio.sleep(1)
        
        await websocket.send_text(json.dumps({
            "status": "success",
            "stage": "completed", 
            "progress": 100.0,
            "timestamp": "2025-08-22T02:45:00Z",
            "message": "任务已完成"
        }))
        
        # 保持连接一段时间
        await asyncio.sleep(5)
        
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for task {task_id}")
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {str(e)}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run("app.main_full:app", host="127.0.0.1", port=8000, reload=True)