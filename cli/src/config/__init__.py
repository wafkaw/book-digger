"""
Configuration module for Kindle Reading Assistant
"""

from .models import (
    Book, BookMetadata, Highlight, HighlightType, NoteType, Location,
    AIAnalysisResult, KnowledgeNode, KnowledgeEdge, KnowledgeGraph
)
from .settings import Config

__all__ = [
    'Book', 'BookMetadata', 'Highlight', 'HighlightType', 'NoteType', 'Location',
    'AIAnalysisResult', 'KnowledgeNode', 'KnowledgeEdge', 'KnowledgeGraph',
    'Config'
]