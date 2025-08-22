"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from app.models.database import Base


class UploadedFile(Base):
    """Uploaded file model"""
    __tablename__ = "uploaded_files"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=False)
    upload_timestamp = Column(DateTime, default=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Relationship
    tasks = relationship("Task", back_populates="file", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<UploadedFile(id={self.id}, filename={self.filename})>"


class Task(Base):
    """Task model for processing jobs"""
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String, ForeignKey("uploaded_files.id"), nullable=False)
    celery_task_id = Column(String, nullable=True)  # Celery task ID
    
    # Status and progress
    status = Column(String(20), default="pending")  # pending, running, success, failure, cancelled
    stage = Column(String(30), default="uploaded")  # uploaded, parsing, ai_analysis, graph_generation, completed
    progress = Column(Float, default=0.0)
    
    # Configuration
    config = Column(JSON, default=lambda: {})
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Results
    result_data = Column(JSON, nullable=True)
    processing_time = Column(Float, nullable=True)
    
    # File references
    output_directory = Column(String(512), nullable=True)
    graph_data_path = Column(String(512), nullable=True)
    
    # Relationship
    file = relationship("UploadedFile", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task(id={self.id}, status={self.status}, stage={self.stage})>"


class TaskLog(Base):
    """Task execution logs"""
    __tablename__ = "task_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    timestamp = Column(DateTime, default=func.now())
    level = Column(String(10), nullable=False)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<TaskLog(task_id={self.task_id}, level={self.level})>"


class AnalysisResult(Base):
    """Analysis results storage"""
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    
    # Book metadata
    book_title = Column(String(500), nullable=False)
    book_author = Column(String(200), nullable=True)
    
    # Statistics  
    total_highlights = Column(Integer, nullable=False)
    concepts_count = Column(Integer, default=0)
    themes_count = Column(Integer, default=0)
    people_count = Column(Integer, default=0)
    
    # Analysis data
    concepts = Column(JSON, nullable=True)  # List of concepts
    themes = Column(JSON, nullable=True)    # List of themes  
    people = Column(JSON, nullable=True)    # List of people
    graph_nodes = Column(JSON, nullable=True)  # Graph nodes data
    graph_edges = Column(JSON, nullable=True)  # Graph edges data
    
    # Metadata
    analysis_version = Column(String(10), default="1.0")
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<AnalysisResult(task_id={self.task_id}, book_title={self.book_title})>"