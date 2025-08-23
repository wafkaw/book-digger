"""
Pydantic models for request/response serialization
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Base response model
class ApiResponse(BaseModel):
    """Standard API response format"""
    success: bool
    message: str
    data: Optional[Any] = None


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running" 
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"


class TaskStage(str, Enum):
    """Task processing stage"""
    UPLOADED = "uploaded"
    PARSING = "parsing"
    AI_ANALYSIS = "ai_analysis" 
    GRAPH_GENERATION = "graph_generation"
    COMPLETED = "completed"


# File Models
class FileUploadResponse(BaseModel):
    """Response for file upload"""
    file_id: str
    filename: str
    size: int
    content_type: str
    upload_timestamp: datetime


class FileInfo(BaseModel):
    """File information"""
    file_id: str
    filename: str
    size: int
    content_type: str
    upload_timestamp: datetime
    status: str


# Task Models
class TaskCreate(BaseModel):
    """Create task request"""
    file_id: str
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    """Task response"""
    task_id: str
    file_id: str
    status: TaskStatus
    stage: TaskStage
    progress: float = Field(ge=0.0, le=100.0)
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
    estimated_remaining: Optional[int] = None  # seconds


class TaskProgress(BaseModel):
    """Task progress update"""
    task_id: str
    status: TaskStatus
    stage: TaskStage
    progress: float
    message: Optional[str] = None
    estimated_remaining: Optional[int] = None
    details: Optional[Dict[str, Any]] = None


class TaskResult(BaseModel):
    """Task analysis result"""
    task_id: str
    book_title: str
    total_highlights: int
    concepts_count: int
    themes_count: int
    people_count: int
    processing_time: float
    graph_data: Optional[Dict[str, Any]] = None
    download_url: Optional[str] = None


# Graph Models
class GraphNode(BaseModel):
    """Graph node representation"""
    id: str
    label: str
    type: str  # concept, theme, person
    importance: float
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """Graph edge representation"""
    source: str
    target: str
    weight: float
    type: str = "related"
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphData(BaseModel):
    """Complete graph data"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Error Models
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)