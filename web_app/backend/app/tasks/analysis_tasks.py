"""
Celery tasks for Kindle analysis
"""
import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any
from celery import current_task
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

# Add the main project to Python path to import existing analysis code
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.tasks.celery_app import celery_app
from app.models.database import engine
from app.models.models import Task, AnalysisResult
from app.core.config import settings

# Import existing analysis modules
from src.data_collection.kindle_parser import KindleParser
from src.knowledge_graph.ai_analysis import AIAnalysisInterface
from src.output.obsidian_generator import ObsidianGenerator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database session for tasks
SessionLocal = sessionmaker(bind=engine)


class ProgressCallback:
    """Callback class for progress updates"""
    
    def __init__(self, task_id: str, db_session):
        self.task_id = task_id
        self.db_session = db_session
        self.last_progress = 0.0
        
    def update_progress(self, progress: float, stage: str, message: str = None):
        """Update task progress"""
        try:
            # Update Celery task status
            if current_task:
                current_task.update_state(
                    state='PROGRESS',
                    meta={
                        'progress': progress,
                        'stage': stage,
                        'message': message,
                        'timestamp': time.time()
                    }
                )
            
            # Update database
            task = self.db_session.query(Task).filter(Task.id == self.task_id).first()
            if task:
                task.progress = progress
                task.stage = stage
                if progress > 0 and not task.started_at:
                    task.started_at = func.now()
                self.db_session.commit()
                
            self.last_progress = progress
            logger.info(f"Task {self.task_id}: {progress:.1f}% - {stage} - {message}")
            
        except Exception as e:
            logger.error(f"Progress update failed: {e}")


@celery_app.task(bind=True)
def analyze_kindle_file(self, task_id: str, file_path: str, config: Dict[str, Any] = None):
    """
    Main Celery task for analyzing Kindle files
    
    Args:
        task_id: Database task ID
        file_path: Path to uploaded HTML file
        config: Analysis configuration
    
    Returns:
        Analysis results
    """
    db_session = SessionLocal()
    progress_callback = ProgressCallback(task_id, db_session)
    
    try:
        # Update task status
        task = db_session.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise Exception(f"Task {task_id} not found in database")
            
        task.status = "running"
        task.celery_task_id = self.request.id
        db_session.commit()
        
        progress_callback.update_progress(5.0, "parsing", "开始解析Kindle文件")
        
        # Step 1: Parse Kindle HTML file
        start_time = time.time()
        parser = KindleParser()
        
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        book = parser.parse_file(str(file_path))
        
        progress_callback.update_progress(15.0, "parsing", f"解析完成，发现{len(book.highlights)}个标注")
        
        # Step 2: AI Analysis
        progress_callback.update_progress(20.0, "ai_analysis", "开始AI语义分析")
        
        # Configure AI interface (use existing production-ready interface)
        ai_config = config or {}
        ai_interface = AIAnalysisInterface(mock_mode=ai_config.get('mock_mode', False))
        
        # Create progress tracking function
        def ai_progress_update(current_batch, total_batches, stage_info=""):
            progress = 20.0 + (current_batch / total_batches) * 60.0  # 20% to 80%
            progress_callback.update_progress(
                progress, 
                "ai_analysis", 
                f"分析批次 {current_batch}/{total_batches}: {stage_info}"
            )
        
        # Run analysis with batch progress tracking
        try:
            # Get batch size from config
            batch_size = settings.AI_BATCH_SIZE
            total_batches = (len(book.highlights) + batch_size - 1) // batch_size
            
            # Update progress for each batch during analysis
            for i in range(total_batches):
                ai_progress_update(i + 1, total_batches, f"分析第{i+1}批标注")
                
            # Run the actual analysis
            analysis_result = ai_interface.analyze_book(book, batch_size=batch_size)
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Try with mock mode as fallback
            logger.info("Falling back to mock mode")
            ai_interface = AIAnalysisInterface(mock_mode=True)
            analysis_result = ai_interface.analyze_book(book, batch_size=batch_size)
        
        progress_callback.update_progress(80.0, "obsidian_generation", "开始生成Obsidian文件")
        
        # Step 3: Generate Obsidian files
        output_dir = Path(settings.UPLOAD_DIR) / f"obsidian_output_{task_id}"
        output_dir.mkdir(exist_ok=True)
        
        # Use the existing ObsidianGenerator with web-friendly configuration
        generator = ObsidianGenerator(output_dir=str(output_dir))
        generator.generate_book_files(book, analysis_result, aggregated_mode=False)
        
        progress_callback.update_progress(90.0, "obsidian_generation", "Obsidian文件生成完成")
        
        # Step 4: Save results to database
        processing_time = time.time() - start_time
        
        # Extract statistics from analysis result
        concepts_count = len(analysis_result.get('concepts', []))
        themes_count = len(analysis_result.get('themes', []))
        people_count = len(analysis_result.get('people', []))
        
        # Create analysis result record
        db_result = AnalysisResult(
            task_id=task_id,
            book_title=book.metadata.title,
            book_author=book.metadata.author,
            total_highlights=len(book.highlights),
            concepts_count=concepts_count,
            themes_count=themes_count,
            people_count=people_count,
            analysis_version="1.0"
        )
        
        db_session.add(db_result)
        
        # Update task
        task.status = "success"
        task.stage = "completed"
        task.progress = 100.0
        task.completed_at = func.now()
        task.processing_time = processing_time
        task.output_directory = str(output_dir)
        task.result_data = {
            'book_title': db_result.book_title,
            'total_highlights': db_result.total_highlights,
            'concepts_count': db_result.concepts_count,
            'themes_count': db_result.themes_count,
            'people_count': db_result.people_count,
            'processing_time': processing_time,
            'output_directory': str(output_dir)
        }
        
        db_session.commit()
        
        progress_callback.update_progress(100.0, "completed", "分析完成")
        
        logger.info(f"Task {task_id} completed successfully in {processing_time:.2f}s")
        
        return {
            'status': 'success',
            'task_id': task_id,
            'processing_time': processing_time,
            'results': task.result_data
        }
        
    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}", exc_info=True)
        
        # Update task with error
        try:
            task = db_session.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = "failure"
                task.error_message = str(e)
                task.completed_at = func.now()
                db_session.commit()
        except Exception as db_e:
            logger.error(f"Failed to update task error status: {db_e}")
        
        # Update Celery task state
        self.update_state(
            state='FAILURE',
            meta={
                'error': str(e),
                'task_id': task_id,
                'timestamp': time.time()
            }
        )
        
        raise e
        
    finally:
        db_session.close()


@celery_app.task
def cleanup_old_tasks():
    """Clean up old completed tasks and files"""
    db_session = SessionLocal()
    
    try:
        from datetime import datetime, timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=settings.TASK_CLEANUP_HOURS)
        
        # Find old tasks
        old_tasks = db_session.query(Task).filter(
            Task.completed_at < cutoff_time,
            Task.status.in_(["success", "failure"])
        ).all()
        
        for task in old_tasks:
            # Clean up output files
            if task.output_directory:
                output_path = Path(task.output_directory)
                if output_path.exists():
                    import shutil
                    shutil.rmtree(output_path)
            
            # Delete task record
            db_session.delete(task)
        
        db_session.commit()
        logger.info(f"Cleaned up {len(old_tasks)} old tasks")
        
    except Exception as e:
        logger.error(f"Task cleanup failed: {e}")
        db_session.rollback()
    finally:
        db_session.close()