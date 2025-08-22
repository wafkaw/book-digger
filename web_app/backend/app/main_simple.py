"""
简化版FastAPI应用 - 专注图谱功能
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 创建FastAPI应用
app = FastAPI(
    title="Kindle知识图谱API",
    version="1.0.0",
    debug=True,
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入图谱API
from app.api.v1.endpoints.graph import router as graph_router

# 注册路由
app.include_router(graph_router, prefix="/api/v1/graph", tags=["graph"])

@app.get("/")
async def root():
    return {"message": "Kindle知识图谱API服务已启动"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "graph-api"}

if __name__ == "__main__":
    uvicorn.run("app.main_simple:app", host="127.0.0.1", port=8000, reload=True)