"""
Task management service
"""
import uuid
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import datetime

from app.models.models import Task
from app.models.schemas import TaskCreate, TaskResponse, TaskResult, TaskStatus, TaskStage
# from app.tasks.analysis_tasks import analyze_kindle_file  # Removed Celery dependency
from app.services.file_service import file_service

logger = logging.getLogger(__name__)


class TaskService:
    """Service for managing analysis tasks"""
    
    async def create_task(self, task_data: TaskCreate, db: Session) -> TaskResponse:
        """
        Create a new analysis task
        
        Args:
            task_data: Task creation data
            db: Database session
            
        Returns:
            TaskResponse with task details
        """
        # Verify file exists
        file_info = await file_service.get_file_info(task_data.file_id, db)
        if not file_info:
            raise ValueError(f"File not found: {task_data.file_id}")
        
        # Get file path
        file_path = await file_service.get_file_path(task_data.file_id, db)
        if not file_path or not file_path.exists():
            raise ValueError(f"File not accessible: {task_data.file_id}")
        
        # Create task record
        task_id = str(uuid.uuid4())
        db_task = Task(
            id=task_id,
            file_id=task_data.file_id,
            config=task_data.config,
            status="pending",
            stage="uploaded"
        )
        
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        # Start analysis directly (no Celery)
        try:
            from app.services.sync_analysis_service import analysis_service
            import asyncio
            
            # Run analysis in background task
            async def run_in_background():
                try:
                    # Create a new database session for the background task
                    from app.models.database import SessionLocal
                    bg_db = SessionLocal()
                    try:
                        await analysis_service.run_analysis(
                            task_id, str(file_path), bg_db, task_data.config or {}
                        )
                    finally:
                        bg_db.close()
                except Exception as e:
                    logger.error(f"Background analysis failed: {e}")
            
            # Start background task
            asyncio.create_task(run_in_background())
            
            logger.info(f"Task created and started: {task_id}")
            
        except Exception as e:
            # Clean up if task creation fails
            db.delete(db_task)
            db.commit()
            logger.error(f"Failed to start analysis task: {e}")
            raise ValueError(f"Failed to start analysis task: {str(e)}")
        
        return TaskResponse(
            task_id=task_id,
            file_id=task_data.file_id,
            status=TaskStatus.PENDING,
            stage=TaskStage.UPLOADED,
            progress=0.0,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at
        )
    
    def get_task(self, task_id: str, db: Session) -> Optional[TaskResponse]:
        """
        Get task information
        
        Args:
            task_id: Task ID
            db: Database session
            
        Returns:
            TaskResponse or None if not found
        """
        db_task = db.query(Task).filter(Task.id == task_id).first()
        
        if not db_task:
            return None
        
        # Map database status to enum
        status = TaskStatus(db_task.status)
        stage = TaskStage(db_task.stage)
        
        return TaskResponse(
            task_id=db_task.id,
            file_id=db_task.file_id,
            status=status,
            stage=stage,
            progress=db_task.progress,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at,
            error_message=db_task.error_message
        )
    
    def get_task_result(self, task_id: str, db: Session) -> Optional[TaskResult]:
        """
        Get task analysis result
        
        Args:
            task_id: Task ID
            db: Database session
            
        Returns:
            TaskResult or None if not found/completed
        """
        db_task = db.query(Task).filter(Task.id == task_id).first()
        
        if not db_task or db_task.status != "success":
            return None
        
        result_data = db_task.result_data or {}
        
        return TaskResult(
            task_id=task_id,
            book_title=result_data.get('book_title', 'Unknown'),
            total_highlights=result_data.get('total_highlights', 0),
            concepts_count=result_data.get('concepts_count', 0),
            themes_count=result_data.get('themes_count', 0),
            people_count=result_data.get('people_count', 0),
            processing_time=result_data.get('processing_time', 0.0),
            download_url=f"/api/v1/tasks/{task_id}/download" if db_task.output_directory else None
        )
    
    def cancel_task(self, task_id: str, db: Session) -> bool:
        """
        Cancel a running task
        
        Args:
            task_id: Task ID
            db: Database session
            
        Returns:
            True if cancelled successfully
        """
        db_task = db.query(Task).filter(Task.id == task_id).first()
        
        if not db_task:
            return False
        
        if db_task.status in ["success", "failure", "cancelled"]:
            return True  # Already finished
        
        # Note: In sync mode, tasks cannot be cancelled once started
        # This is a limitation of the simplified architecture
        
        # Update task status
        db_task.status = "cancelled"
        db_task.completed_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Task cancelled: {task_id}")
        return True
    
    def get_user_tasks(self, db: Session, limit: int = 50, offset: int = 0) -> List[TaskResponse]:
        """
        Get list of tasks (for future user management)
        
        Args:
            db: Database session
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip
            
        Returns:
            List of TaskResponse objects
        """
        db_tasks = db.query(Task).order_by(Task.created_at.desc()).offset(offset).limit(limit).all()
        
        return [
            TaskResponse(
                task_id=task.id,
                file_id=task.file_id,
                status=TaskStatus(task.status),
                stage=TaskStage(task.stage),
                progress=task.progress,
                created_at=task.created_at,
                updated_at=task.updated_at,
                error_message=task.error_message
            )
            for task in db_tasks
        ]
    
    def get_output_directory(self, task_id: str, db: Session) -> Optional[Path]:
        """
        Get output directory path for a completed task
        
        Args:
            task_id: Task ID
            db: Database session
            
        Returns:
            Path to output directory or None
        """
        db_task = db.query(Task).filter(Task.id == task_id).first()
        
        if not db_task or not db_task.output_directory:
            return None
        
        output_path = Path(db_task.output_directory)
        if not output_path.exists():
            return None
            
        return output_path


# Global service instance
task_service = TaskService()