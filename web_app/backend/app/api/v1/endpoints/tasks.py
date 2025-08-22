"""
Task management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
import json
import asyncio
import logging

from app.models.database import get_db
from app.models.schemas import TaskCreate, TaskResponse, TaskResult
from app.services.task_service import task_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=TaskResponse)
async def create_task(
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
        return await task_service.create_task(task_data, db)
    except ValueError as e:
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


@router.websocket("/{task_id}/ws")
async def task_progress_websocket(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for real-time task progress updates
    
    - **task_id**: Unique task identifier
    
    Provides real-time updates on task progress, status, and stage
    """
    await websocket.accept()
    
    try:
        db = next(get_db())
        
        # Verify task exists
        task = task_service.get_task(task_id, db)
        if not task:
            await websocket.send_json({"error": "Task not found"})
            await websocket.close(code=1008)
            return
        
        # Send initial status
        await websocket.send_json({
            "type": "task_status",
            "task_id": task_id,
            "status": task.status.value,
            "stage": task.stage.value,
            "progress": task.progress,
            "timestamp": task.updated_at.isoformat()
        })
        
        # Monitor task progress
        last_progress = task.progress
        last_status = task.status.value
        
        while True:
            # Check for client messages (optional heartbeat)
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                # Handle heartbeat or other client messages if needed
                if message == "ping":
                    await websocket.send_json({"type": "pong"})
            except asyncio.TimeoutError:
                pass  # No message received, continue monitoring
            
            # Get updated task status
            current_task = task_service.get_task(task_id, db)
            if not current_task:
                break
            
            # Check if status or progress changed
            if (current_task.progress != last_progress or 
                current_task.status.value != last_status):
                
                await websocket.send_json({
                    "type": "progress_update",
                    "task_id": task_id,
                    "status": current_task.status.value,
                    "stage": current_task.stage.value,
                    "progress": current_task.progress,
                    "timestamp": current_task.updated_at.isoformat(),
                    "error_message": current_task.error_message
                })
                
                last_progress = current_task.progress
                last_status = current_task.status.value
            
            # Exit if task is completed
            if current_task.status.value in ["success", "failure", "cancelled"]:
                await websocket.send_json({
                    "type": "task_completed",
                    "task_id": task_id,
                    "status": current_task.status.value,
                    "final_progress": current_task.progress,
                    "timestamp": current_task.updated_at.isoformat(),
                    "error_message": current_task.error_message
                })
                break
            
            # Wait before next check
            await asyncio.sleep(2)  # Check every 2 seconds
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for task {task_id}")
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {str(e)}")
        try:
            await websocket.send_json({"error": f"Internal error: {str(e)}"})
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass