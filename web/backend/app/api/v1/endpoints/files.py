"""
File upload and management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.models.database import get_db
from app.models.schemas import FileUploadResponse, FileInfo, ErrorResponse
from app.services.file_service import file_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a Kindle HTML file
    
    - **file**: HTML file to upload (max 10MB)
    
    Returns file information including file_id for further processing
    """
    try:
        return await file_service.upload_file(file, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during file upload")


@router.get("/{file_id}", response_model=FileInfo)
async def get_file_info(
    file_id: str,
    db: Session = Depends(get_db)
):
    """
    Get information about an uploaded file
    
    - **file_id**: Unique file identifier
    
    Returns file metadata and status
    """
    file_info = await file_service.get_file_info(file_id, db)
    
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    return file_info


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete an uploaded file
    
    - **file_id**: Unique file identifier
    
    Returns success status
    """
    success = await file_service.delete_file(file_id, db)
    
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {"message": "File deleted successfully", "file_id": file_id}