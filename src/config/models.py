"""
Data models for Kindle reading assistant
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum


class HighlightType(Enum):
    YELLOW = "yellow"
    BLUE = "blue"
    ORANGE = "orange"
    PINK = "pink"


class NoteType(Enum):
    HIGHLIGHT = "highlight"
    NOTE = "note"
    BOOKMARK = "bookmark"


@dataclass
class Location:
    page: int
    position: int
    
    def __str__(self):
        return f"Page {self.page} · Location {self.position}"


@dataclass
class BookMetadata:
    title: str
    author: str
    subtitle: Optional[str] = None
    translator: Optional[str] = None
    publisher: Optional[str] = None
    year: Optional[int] = None
    edition: Optional[str] = None
    country: Optional[str] = None
    
    @classmethod
    def from_title_string(cls, title_string: str):
        """Parse metadata from Kindle title string format"""
        parts = title_string.split(" -- ")
        
        title_part = parts[0]
        author_part = parts[1] if len(parts) > 1 else ""
        
        # Parse title and subtitle
        if " = " in title_part:
            title, subtitle = title_part.split(" = ", 1)
        else:
            title, subtitle = title_part, None
            
        # Parse author and additional info
        author_info = author_part.split("(")
        author = author_info[0].strip()
        
        # Extract additional metadata
        translator = None
        publisher = None
        year = None
        edition = None
        country = None
        
        if len(author_info) > 1:
            additional_info = author_info[1].replace(")", "")
            info_parts = additional_info.split(",")
            
            for part in info_parts:
                part = part.strip()
                if "译" in part or "翻译" in part:
                    translator = part
                elif any(char.isdigit() for char in part):
                    # Try to extract year
                    year_str = ''.join(filter(str.isdigit, part))
                    if year_str and len(year_str) == 4:
                        year = int(year_str)
                elif "出版社" in part:
                    publisher = part
                elif "US" in part or "CN" in part or "UK" in part:
                    country = part
                elif "版" in part:
                    edition = part
        
        return cls(
            title=title,
            author=author,
            subtitle=subtitle,
            translator=translator,
            publisher=publisher,
            year=year,
            edition=edition,
            country=country
        )


@dataclass
class Highlight:
    content: str
    location: Location
    highlight_type: HighlightType
    section: Optional[str] = None
    note_type: NoteType = NoteType.HIGHLIGHT
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "location": str(self.location),
            "page": self.location.page,
            "position": self.location.position,
            "highlight_type": self.highlight_type.value,
            "section": self.section,
            "note_type": self.note_type.value
        }


@dataclass
class Book:
    metadata: BookMetadata
    highlights: List[Highlight]
    export_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": {
                "title": self.metadata.title,
                "author": self.metadata.author,
                "subtitle": self.metadata.subtitle,
                "translator": self.metadata.translator,
                "publisher": self.metadata.publisher,
                "year": self.metadata.year,
                "edition": self.metadata.edition,
                "country": self.metadata.country
            },
            "highlights": [highlight.to_dict() for highlight in self.highlights],
            "export_date": self.export_date.isoformat() if self.export_date else None,
            "total_highlights": len(self.highlights)
        }
    
    def get_highlights_by_section(self) -> Dict[str, List[Highlight]]:
        """Group highlights by section"""
        sections = {}
        for highlight in self.highlights:
            section = highlight.section or "Unknown"
            if section not in sections:
                sections[section] = []
            sections[section].append(highlight)
        return sections
    
    def get_highlights_by_type(self) -> Dict[HighlightType, List[Highlight]]:
        """Group highlights by type"""
        types = {}
        for highlight in self.highlights:
            h_type = highlight.highlight_type
            if h_type not in types:
                types[h_type] = []
            types[h_type].append(highlight)
        return types


@dataclass
class AIAnalysisResult:
    """AI analysis result for a highlight"""
    highlight_id: str
    concepts: List[str]
    themes: List[str]
    emotions: List[str]
    people: List[str]
    importance_score: float
    summary: str
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "highlight_id": self.highlight_id,
            "concepts": self.concepts,
            "themes": self.themes,
            "emotions": self.emotions,
            "people": self.people,
            "importance_score": self.importance_score,
            "summary": self.summary,
            "tags": self.tags
        }


class SummaryLayer(Enum):
    """Progressive summary layers"""
    L1_RAW = "raw"                    # 原始内容
    L2_HIGHLIGHTED = "highlighted"     # 重点高亮
    L3_SUMMARIZED = "summarized"       # 简洁总结
    L4_UNDERSTOOD = "understood"       # 个人理解
    L5_APPLIED = "applied"             # 应用场景


@dataclass
class ProgressiveSummary:
    """Progressive summary for knowledge internalization"""
    highlight_id: str
    layer: SummaryLayer
    content: str
    key_points: List[str]
    personal_insights: List[str]
    application_scenarios: List[str]
    created_at: datetime
    last_reviewed: Optional[datetime] = None
    review_count: int = 0
    mastery_level: float = 0.0  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "highlight_id": self.highlight_id,
            "layer": self.layer.value,
            "content": self.content,
            "key_points": self.key_points,
            "personal_insights": self.personal_insights,
            "application_scenarios": self.application_scenarios,
            "created_at": self.created_at.isoformat(),
            "last_reviewed": self.last_reviewed.isoformat() if self.last_reviewed else None,
            "review_count": self.review_count,
            "mastery_level": self.mastery_level
        }


@dataclass
class ReviewQuestion:
    """Question for spaced repetition"""
    id: str
    highlight_id: str
    question: str
    answer: str
    question_type: str  # "multiple_choice", "short_answer", "true_false"
    options: Optional[List[str]] = None
    difficulty: float = 0.5  # 0.0 to 1.0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class ReviewSession:
    """Spaced repetition review session"""
    id: str
    user_id: str
    questions: List[ReviewQuestion]
    start_time: datetime
    end_time: Optional[datetime] = None
    score: float = 0.0
    completed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "questions": [q.id for q in self.questions],
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "score": self.score,
            "completed": self.completed
        }


@dataclass
class LearningProgress:
    """Track learning progress for knowledge internalization"""
    user_id: str
    book_id: str
    highlight_id: str
    mastery_level: float = 0.0
    review_count: int = 0
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None
    difficulty_level: float = 0.5
    consecutive_correct: int = 0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def update_progress(self, correct: bool):
        """Update progress based on review performance"""
        self.review_count += 1
        self.last_reviewed = datetime.now()
        
        if correct:
            self.consecutive_correct += 1
            self.mastery_level = min(1.0, self.mastery_level + 0.1)
        else:
            self.consecutive_correct = 0
            self.mastery_level = max(0.0, self.mastery_level - 0.05)
        
        # Calculate next review time using spaced repetition
        self.next_review = self._calculate_next_review()
    
    def _calculate_next_review(self) -> datetime:
        """Calculate next review time using spaced repetition algorithm"""
        base_interval = 1  # day
        if self.consecutive_correct == 0:
            interval = base_interval
        elif self.consecutive_correct == 1:
            interval = base_interval * 3
        elif self.consecutive_correct == 2:
            interval = base_interval * 7
        else:
            interval = base_interval * (2 ** (self.consecutive_correct - 2))
        
        return datetime.now() + timedelta(days=interval)


@dataclass
class KnowledgeNode:
    """Knowledge graph node"""
    id: str
    label: str
    type: str  # "concept", "person", "theme", "book"
    description: Optional[str] = None
    book_id: Optional[str] = None
    highlights: List[str] = None  # highlight IDs
    
    def __post_init__(self):
        if self.highlights is None:
            self.highlights = []


@dataclass
class KnowledgeEdge:
    """Knowledge graph edge"""
    source: str
    target: str
    relationship: str
    weight: float
    evidence: Optional[str] = None


@dataclass
class KnowledgeGraph:
    """Knowledge graph structure"""
    nodes: List[KnowledgeNode]
    edges: List[KnowledgeEdge]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [
                {
                    "id": node.id,
                    "label": node.label,
                    "type": node.type,
                    "description": node.description,
                    "book_id": node.book_id,
                    "highlights": node.highlights
                }
                for node in self.nodes
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "relationship": edge.relationship,
                    "weight": edge.weight,
                    "evidence": edge.evidence
                }
                for edge in self.edges
            ]
        }