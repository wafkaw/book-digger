"""
Configuration settings for Kindle Reading Assistant
"""
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the application"""
    
    # Directories
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    MATERIAL_DIR = PROJECT_ROOT / "material"
    OUTPUT_DIR = PROJECT_ROOT / "obsidian_vault"
    DATA_DIR = PROJECT_ROOT / "data"
    LOGS_DIR = PROJECT_ROOT / "logs"
    CACHE_DIR = PROJECT_ROOT / "data" / "cache"
    
    # File patterns
    KINDLE_HTML_PATTERN = "*.html"
    
    # AI Analysis settings
    AI_MOCK_MODE = os.getenv("AI_MOCK_MODE", "false").lower() == "true"
    AI_MAX_CONCEPTS = int(os.getenv("AI_MAX_CONCEPTS", "5"))
    AI_MAX_THEMES = int(os.getenv("AI_MAX_THEMES", "3"))
    AI_MAX_EMOTIONS = int(os.getenv("AI_MAX_EMOTIONS", "3"))
    AI_BATCH_SIZE = int(os.getenv("AI_BATCH_SIZE", "5"))  # 批量处理大小
    
    # Analysis quality settings
    AI_QUALITY_MODE = os.getenv("AI_QUALITY_MODE", "balanced")  # strict, balanced, permissive
    AI_MIN_CONCEPT_LENGTH = int(os.getenv("AI_MIN_CONCEPT_LENGTH", "3"))  # 概念最小长度
    AI_MIN_IMPORTANCE_THRESHOLD = float(os.getenv("AI_MIN_IMPORTANCE_THRESHOLD", "0.3"))  # 最低重要性阈值
    
    # Output settings
    OUTPUT_AGGREGATED_MODE = os.getenv("OUTPUT_AGGREGATED_MODE", "true").lower() == "true"  # 聚合输出模式
    OUTPUT_MAX_HIGHLIGHTS_PER_CONCEPT = int(os.getenv("OUTPUT_MAX_HIGHLIGHTS_PER_CONCEPT", "3"))  # 每个概念显示的最大标注数
    
    # LLM API settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  # Optional custom base URL for OpenAI-compatible APIs
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
    OPENAI_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "600"))  # 10分钟超时
    OPENAI_MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "3"))  # 最多重试3次
    
    # API cost control
    MAX_DAILY_API_COST = float(os.getenv("MAX_DAILY_API_COST", "10.0"))
    BATCH_PROCESSING_SIZE = int(os.getenv("BATCH_PROCESSING_SIZE", "5"))
    ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    CACHE_TTL_HOURS = int(os.getenv("CACHE_TTL_HOURS", "24"))
    
    # Local model settings (backup)
    OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "false").lower() == "true"
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:32b")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Redis cache settings
    REDIS_URL = os.getenv("REDIS_URL")
    
    # Obsidian settings
    OBSIDIAN_BOOKS_DIR = os.getenv("OBSIDIAN_BOOKS_DIR", "books")
    OBSIDIAN_CONCEPTS_DIR = os.getenv("OBSIDIAN_CONCEPTS_DIR", "concepts")
    OBSIDIAN_PEOPLE_DIR = os.getenv("OBSIDIAN_PEOPLE_DIR", "people")
    OBSIDIAN_THEMES_DIR = os.getenv("OBSIDIAN_THEMES_DIR", "themes")
    
    # Processing settings
    MIN_HIGHLIGHT_LENGTH = int(os.getenv("MIN_HIGHLIGHT_LENGTH", "10"))
    MAX_HIGHLIGHT_LENGTH = int(os.getenv("MAX_HIGHLIGHT_LENGTH", "2000"))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "kindle_assistant.log")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Knowledge graph settings
    MIN_RELATIONSHIP_WEIGHT = float(os.getenv("MIN_RELATIONSHIP_WEIGHT", "0.1"))
    MAX_NODES_PER_TYPE = int(os.getenv("MAX_NODES_PER_TYPE", "100"))
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        directories = [
            cls.MATERIAL_DIR,
            cls.OUTPUT_DIR,
            cls.DATA_DIR,
            cls.LOGS_DIR,
            cls.CACHE_DIR,
            cls.OUTPUT_DIR / cls.OBSIDIAN_BOOKS_DIR,
            cls.OUTPUT_DIR / cls.OBSIDIAN_CONCEPTS_DIR,
            cls.OUTPUT_DIR / cls.OBSIDIAN_PEOPLE_DIR,
            cls.OUTPUT_DIR / cls.OBSIDIAN_THEMES_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_kindle_files(cls) -> list:
        """Get list of Kindle HTML files"""
        if not cls.MATERIAL_DIR.exists():
            return []
        
        return list(cls.MATERIAL_DIR.glob(cls.KINDLE_HTML_PATTERN))
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "project_root": str(cls.PROJECT_ROOT),
            "material_dir": str(cls.MATERIAL_DIR),
            "output_dir": str(cls.OUTPUT_DIR),
            "ai_mock_mode": cls.AI_MOCK_MODE,
            "max_concepts": cls.AI_MAX_CONCEPTS,
            "max_themes": cls.AI_MAX_THEMES,
            "max_emotions": cls.AI_MAX_EMOTIONS,
            "min_highlight_length": cls.MIN_HIGHLIGHT_LENGTH,
            "max_highlight_length": cls.MAX_HIGHLIGHT_LENGTH,
            "batch_size": cls.BATCH_SIZE,
            "log_level": cls.LOG_LEVEL
        }


# Initialize directories
Config.create_directories()