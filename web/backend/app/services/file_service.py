"""
File handling service
"""
import os
import uuid
# import magic  # Temporarily disabled due to libmagic dependency issues
import aiofiles
from pathlib import Path
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.config import settings
from app.models.models import UploadedFile
from app.models.schemas import FileUploadResponse, FileInfo

logger = logging.getLogger(__name__)


class FileService:
    """Service for handling file uploads and management"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
    async def upload_file(self, file: UploadFile, db: Session) -> FileUploadResponse:
        """
        Upload and store a file
        
        Args:
            file: FastAPI uploaded file
            db: Database session
            
        Returns:
            FileUploadResponse with file details
        """
        # Validate file
        await self._validate_file(file)
        
        # Generate unique file ID and path
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename or "").suffix.lower()
        stored_filename = f"{file_id}{file_extension}"
        file_path = self.upload_dir / stored_filename
        
        try:
            # Save file to disk
            await self._save_file(file, file_path)
            
            # Detect content type
            content_type = await self._detect_content_type(file_path)
            
            # Create database record
            db_file = UploadedFile(
                id=file_id,
                filename=stored_filename,
                original_filename=file.filename or "unknown",
                file_path=str(file_path),
                file_size=file_path.stat().st_size,
                content_type=content_type
            )
            
            db.add(db_file)
            db.commit()
            db.refresh(db_file)
            
            logger.info(f"File uploaded successfully: {file_id} ({file.filename})")
            
            return FileUploadResponse(
                file_id=file_id,
                filename=file.filename or "unknown",
                size=db_file.file_size,
                content_type=content_type,
                upload_timestamp=db_file.upload_timestamp
            )
            
        except Exception as e:
            # Clean up file if database operation fails
            if file_path.exists():
                file_path.unlink()
            db.rollback()
            logger.error(f"File upload failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    
    async def get_file_info(self, file_id: str, db: Session) -> Optional[FileInfo]:
        """
        Get file information
        
        Args:
            file_id: File ID
            db: Database session
            
        Returns:
            FileInfo or None if not found
        """
        db_file = db.query(UploadedFile).filter(
            UploadedFile.id == file_id,
            UploadedFile.is_deleted == False
        ).first()
        
        if not db_file:
            return None
            
        return FileInfo(
            file_id=db_file.id,
            filename=db_file.original_filename,
            size=db_file.file_size,
            content_type=db_file.content_type,
            upload_timestamp=db_file.upload_timestamp,
            status="uploaded"
        )
    
    async def delete_file(self, file_id: str, db: Session) -> bool:
        """
        Mark file as deleted (soft delete)
        
        Args:
            file_id: File ID
            db: Database session
            
        Returns:
            True if successful, False if file not found
        """
        db_file = db.query(UploadedFile).filter(
            UploadedFile.id == file_id,
            UploadedFile.is_deleted == False
        ).first()
        
        if not db_file:
            return False
            
        db_file.is_deleted = True
        db.commit()
        
        # Also delete physical file (optional)
        try:
            file_path = Path(db_file.file_path)
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete physical file {db_file.file_path}: {str(e)}")
        
        logger.info(f"File deleted: {file_id}")
        return True
    
    async def get_file_path(self, file_id: str, db: Session) -> Optional[Path]:
        """
        Get file system path for a file
        
        Args:
            file_id: File ID
            db: Database session
            
        Returns:
            Path object or None if not found
        """
        db_file = db.query(UploadedFile).filter(
            UploadedFile.id == file_id,
            UploadedFile.is_deleted == False
        ).first()
        
        if not db_file:
            return None
            
        return Path(db_file.file_path)
    
    async def _validate_file(self, file: UploadFile):
        """Validate uploaded file"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Check file size
        if file.size and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
            )
    
    async def _save_file(self, file: UploadFile, file_path: Path):
        """Save uploaded file to disk"""
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
                
                # Additional size check after reading
                if len(content) > settings.MAX_FILE_SIZE:
                    file_path.unlink()  # Delete the file
                    raise HTTPException(
                        status_code=400,
                        detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
                    )
                    
        except Exception as e:
            if file_path.exists():
                file_path.unlink()
            raise e
        finally:
            # Reset file pointer for potential future reads
            await file.seek(0)
    
    async def _detect_content_type(self, file_path: Path) -> str:
        """Detect file content type using file extension (fallback)"""
        try:
            # Temporarily use file extension as fallback
            suffix = file_path.suffix.lower()
            if suffix == '.html' or suffix == '.htm':
                return 'text/html'
            elif suffix == '.txt':
                return 'text/plain'
            else:
                return 'application/octet-stream'
        except Exception as e:
            logger.warning(f"Could not detect content type for {file_path}: {str(e)}")
            return "application/octet-stream"


# Global service instance
file_service = FileService()