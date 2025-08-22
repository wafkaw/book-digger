"""
API v1 Router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import files, tasks, health, graph

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])