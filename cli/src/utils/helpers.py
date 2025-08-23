"""
Utility functions for Kindle Reading Assistant
"""
import re
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime


def setup_logging(log_level: str = "INFO", log_file: str = "kindle_assistant.log"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for file system compatibility"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove excessive whitespace
    filename = ' '.join(filename.split())
    
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text"""
    # Simple keyword extraction - remove common words and return unique words
    common_words = {
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '个',
        '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看',
        '好', '自己', '这', '那', '他', '她', '它', '们', '的', 'the', 'and', 'or',
        'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
        'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can'
    }
    
    # Extract Chinese and English words
    words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text.lower())
    
    # Filter common words and short words
    keywords = [word for word in words if len(word) > 1 and word not in common_words]
    
    # Return unique keywords
    unique_keywords = list(set(keywords))
    
    return unique_keywords[:max_keywords]


def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts"""
    # Simple Jaccard similarity
    words1 = set(extract_keywords(text1, max_keywords=50))
    words2 = set(extract_keywords(text2, max_keywords=50))
    
    if not words1 and not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0


def save_json(data: Dict[str, Any], filepath: str, indent: int = 2):
    """Save data to JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def load_json(filepath: str) -> Optional[Dict[str, Any]]:
    """Load data from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON file {filepath}: {e}")
        return None


def get_file_stats(filepath: str) -> Dict[str, Any]:
    """Get file statistics"""
    path = Path(filepath)
    if not path.exists():
        return {}
    
    stat = path.stat()
    return {
        "size": stat.st_size,
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "extension": path.suffix,
        "filename": path.name
    }


def validate_html_structure(content: str) -> bool:
    """Validate HTML structure for Kindle export"""
    required_elements = [
        'bookTitle',
        'authors',
        'sectionHeading',
        'noteHeading',
        'noteText'
    ]
    
    for element in required_elements:
        if f'class="{element}"' not in content:
            return False
    
    return True


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Chunk text into smaller pieces"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundaries
        if end < len(text):
            # Look for sentence ending
            for i in range(end, max(start, end - 200), -1):
                if text[i] in '。！？.!?':
                    end = i + 1
                    break
        
        chunk = text[start:end]
        chunks.append(chunk)
        
        start = end - overlap
        
        if start >= len(text):
            break
    
    return chunks


def merge_analysis_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge multiple analysis results"""
    if not results:
        return {}
    
    merged = {
        "concepts": [],
        "themes": [],
        "emotions": [],
        "people": [],
        "tags": [],
        "importance_score": 0.0,
        "highlights_analyzed": len(results)
    }
    
    # Collect all unique items
    for result in results:
        merged["concepts"].extend(result.get("concepts", []))
        merged["themes"].extend(result.get("themes", []))
        merged["emotions"].extend(result.get("emotions", []))
        merged["people"].extend(result.get("people", []))
        merged["tags"].extend(result.get("tags", []))
        merged["importance_score"] += result.get("importance_score", 0.0)
    
    # Remove duplicates and calculate averages
    merged["concepts"] = list(set(merged["concepts"]))
    merged["themes"] = list(set(merged["themes"]))
    merged["emotions"] = list(set(merged["emotions"]))
    merged["people"] = list(set(merged["people"]))
    merged["tags"] = list(set(merged["tags"]))
    merged["importance_score"] /= len(results) if results else 1.0
    
    return merged


def create_backup(filepath: str, backup_dir: str = "backups") -> str:
    """Create backup of a file"""
    source = Path(filepath)
    if not source.exists():
        return ""
    
    backup_path = Path(backup_dir)
    backup_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{source.stem}_{timestamp}{source.suffix}"
    backup_filepath = backup_path / backup_filename
    
    # Copy file
    backup_filepath.write_text(source.read_text(encoding='utf-8'), encoding='utf-8')
    
    return str(backup_filepath)


def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and normalizing"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    return text


def find_files_by_pattern(directory: str, pattern: str) -> List[str]:
    """Find files matching pattern in directory"""
    path = Path(directory)
    if not path.exists():
        return []
    
    return [str(f) for f in path.glob(pattern)]


def get_progress_percentage(current: int, total: int) -> float:
    """Calculate progress percentage"""
    if total == 0:
        return 0.0
    
    return (current / total) * 100


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


class Timer:
    """Simple timer for performance measurement"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start timer"""
        self.start_time = datetime.now()
    
    def stop(self):
        """Stop timer"""
        self.end_time = datetime.now()
    
    def elapsed(self) -> float:
        """Get elapsed time in seconds"""
        if self.start_time is None:
            return 0.0
        
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def safe_read_file(filepath: str, encoding: str = 'utf-8') -> Optional[str]:
    """Safely read file content"""
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logging.error(f"Error reading file {filepath}: {e}")
        return None


def safe_write_file(filepath: str, content: str, encoding: str = 'utf-8') -> bool:
    """Safely write content to file"""
    try:
        # Create directory if it doesn't exist
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
        
        return True
    except Exception as e:
        logging.error(f"Error writing file {filepath}: {e}")
        return False