"""
Task management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request
from sqlalchemy.orm import Session
from typing import List
import json
import asyncio
import logging
from pydantic import ValidationError

from app.models.database import get_db
from app.models.schemas import TaskCreate, TaskResponse, TaskResult
from app.services.task_service import task_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=TaskResponse)
async def create_task(
    request: Request,
    task_data: TaskCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new analysis task
    
    - **file_id**: ID of uploaded file to analyze
    - **config**: Optional analysis configuration
    
    Returns task information including task_id for tracking
    """
    try:
        # 获取原始请求体进行调试
        body = await request.body()
        logger.info(f"Raw request body: {body.decode()}")
        logger.info(f"Parsed task data: {task_data}")
        
        return await task_service.create_task(task_data, db)
    except ValidationError as e:
        logger.error(f"Pydantic validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        logger.error(f"Task creation validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Task creation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during task creation")


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    Get task status and progress
    
    - **task_id**: Unique task identifier
    
    Returns current task status, progress, and stage
    """
    task = task_service.get_task(task_id, db)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.get("/{task_id}/result", response_model=TaskResult)
def get_task_result(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    Get task analysis results
    
    - **task_id**: Unique task identifier
    
    Returns analysis results including graph data and statistics
    Only available for successfully completed tasks
    """
    result = task_service.get_task_result(task_id, db)
    
    if not result:
        raise HTTPException(
            status_code=404, 
            detail="Task result not found or task not completed successfully"
        )
    
    return result


@router.delete("/{task_id}")
def cancel_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    Cancel a running task
    
    - **task_id**: Unique task identifier
    
    Cancels the task if it's still running
    """
    success = task_service.cancel_task(task_id, db)
    
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": "Task cancelled successfully", "task_id": task_id}


@router.get("", response_model=List[TaskResponse])
def list_tasks(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List user tasks
    
    - **limit**: Maximum number of tasks to return (default: 50)
    - **offset**: Number of tasks to skip (default: 0)
    
    Returns list of tasks ordered by creation time (newest first)
    """
    return task_service.get_user_tasks(db, limit=limit, offset=offset)


# WebSocket endpoint removed in sync mode - frontend will use polling instead