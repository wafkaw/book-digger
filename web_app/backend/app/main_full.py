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

# 导入文件和任务API（真实实现）
from app.api.v1.endpoints.files import router as files_router
from app.api.v1.endpoints.tasks import router as tasks_router

app.include_router(files_router, prefix="/api/v1/files", tags=["files"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])

# 初始化数据库
from app.models.database import init_db

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_db()

# WebSocket removed in sync mode - use polling instead

if __name__ == "__main__":
    uvicorn.run("app.main_full:app", host="127.0.0.1", port=8000, reload=True)