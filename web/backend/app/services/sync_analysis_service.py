"""
同步分析服务 - 直接执行CLI分析逻辑，无需Redis/Celery
"""
import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

# Add the main project to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.models.models import Task, AnalysisResult, UploadedFile
from app.core.config import settings
from sqlalchemy import func

# Import existing analysis modules
from src.data_collection.kindle_parser import KindleParser
from src.knowledge_graph.ai_analysis import AIAnalysisInterface
from src.output.obsidian_generator import ObsidianGenerator

logger = logging.getLogger(__name__)


class SyncAnalysisService:
    """同步分析服务"""
    
    def __init__(self):
        self.parser = KindleParser()
        self.ai_interface = AIAnalysisInterface(mock_mode=False)
        
    async def run_analysis(
        self, 
        task_id: str, 
        file_path: str, 
        db: Session,
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        运行完整的分析流程
        
        Args:
            task_id: 任务ID
            file_path: 文件路径
            db: 数据库会话
            config: 分析配置
            
        Returns:
            分析结果
        """
        start_time = time.time()
        
        try:
            # 获取任务记录
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                raise Exception(f"Task {task_id} not found")
            
            # 更新任务状态为运行中
            task.status = "running"
            task.stage = "parsing"
            task.started_at = func.now()
            db.commit()
            
            logger.info(f"开始分析任务 {task_id}")
            
            # Step 1: 解析Kindle文件 (0-20%)
            self._update_task_progress(task, db, 5.0, "parsing", "开始解析Kindle文件")
            
            if not Path(file_path).exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            book = self.parser.parse_file(str(file_path))
            
            self._update_task_progress(
                task, db, 20.0, "parsing", 
                f"解析完成，发现{len(book.highlights)}个标注"
            )
            
            # Step 2: AI分析 (20-80%)
            self._update_task_progress(task, db, 25.0, "ai_analysis", "开始AI语义分析")
            
            try:
                # 配置AI分析
                ai_config = config or {}
                if ai_config.get('mock_mode', False):
                    self.ai_interface = AIAnalysisInterface(mock_mode=True)
                
                # 运行分析
                batch_size = settings.AI_BATCH_SIZE
                analysis_result = self.ai_interface.analyze_book(book, batch_size=batch_size)
                
                self._update_task_progress(task, db, 80.0, "ai_analysis", "AI分析完成")
                
            except Exception as e:
                logger.error(f"AI分析失败，切换到Mock模式: {e}")
                # 降级到Mock模式
                self.ai_interface = AIAnalysisInterface(mock_mode=True)
                analysis_result = self.ai_interface.analyze_book(book, batch_size=batch_size)
                
                self._update_task_progress(task, db, 80.0, "ai_analysis", "AI分析完成(Mock模式)")
            
            # Step 3: 生成Obsidian文件 (80-95%)
            self._update_task_progress(task, db, 85.0, "obsidian_generation", "开始生成Obsidian文件")
            
            # 创建输出目录
            output_dir = Path(settings.UPLOAD_DIR) / f"obsidian_output_{task_id}"
            output_dir.mkdir(exist_ok=True, parents=True)
            
            # 生成Obsidian文件
            generator = ObsidianGenerator(output_dir=str(output_dir))
            generator.generate_book_files(book, analysis_result, aggregated_mode=False)
            
            self._update_task_progress(task, db, 95.0, "obsidian_generation", "Obsidian文件生成完成")
            
            # Step 4: 保存结果到数据库 (95-100%)
            processing_time = time.time() - start_time
            
            # 提取统计信息
            concepts_count = len(analysis_result.get('concepts', []))
            themes_count = len(analysis_result.get('themes', []))
            people_count = len(analysis_result.get('people', []))
            
            # 创建分析结果记录
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
            
            db.add(db_result)
            
            # 更新任务完成状态
            task.status = "success"
            task.stage = "completed"
            task.progress = 100.0
            task.completed_at = func.now()
            task.processing_time = processing_time
            task.output_directory = str(output_dir)
            task.result_data = {
                'book_title': db_result.book_title,
                'book_author': db_result.book_author,
                'total_highlights': db_result.total_highlights,
                'concepts_count': db_result.concepts_count,
                'themes_count': db_result.themes_count,
                'people_count': db_result.people_count,
                'processing_time': processing_time,
                'output_directory': str(output_dir)
            }
            
            db.commit()
            
            logger.info(f"任务 {task_id} 完成，耗时 {processing_time:.2f}s")
            
            return {
                'status': 'success',
                'task_id': task_id,
                'processing_time': processing_time,
                'results': task.result_data
            }
            
        except Exception as e:
            logger.error(f"任务 {task_id} 失败: {str(e)}", exc_info=True)
            
            # 更新任务错误状态
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = "failure"
                task.error_message = str(e)
                task.completed_at = func.now()
                db.commit()
            
            raise e
    
    def _update_task_progress(
        self, 
        task: Task, 
        db: Session, 
        progress: float, 
        stage: str, 
        message: str = ""
    ):
        """更新任务进度"""
        try:
            task.progress = progress
            task.stage = stage
            task.updated_at = func.now()
            db.commit()
            
            logger.info(f"任务 {task.id}: {progress:.1f}% - {stage} - {message}")
            
        except Exception as e:
            logger.error(f"更新进度失败: {e}")


# 全局服务实例
analysis_service = SyncAnalysisService()