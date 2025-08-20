"""
Kindle Reading Assistant - 解释器模块

This module provides the main interface for parsing and analyzing Kindle reading notes.
"""

from .data_collection.kindle_parser import KindleParser
from .knowledge_graph.ai_analysis import AIAnalysisInterface
from .output.obsidian_generator import ObsidianGenerator

__version__ = "1.0.0"
__author__ = "Kindle Reading Assistant Team"

__all__ = [
    'KindleParser',
    'AIAnalysisInterface', 
    'ObsidianGenerator'
]