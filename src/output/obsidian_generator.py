"""
Obsidian generator for creating markdown files from book analysis
"""
import os
import json
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime
import logging

from ..config.models import Book, AIAnalysisResult, KnowledgeGraph


class ObsidianGenerator:
    """Generate Obsidian-compatible markdown files"""
    
    def __init__(self, output_dir: str = "obsidian_vault"):
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(__name__)
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.books_dir = self.output_dir / "books"
        self.concepts_dir = self.output_dir / "concepts"
        self.people_dir = self.output_dir / "people"
        self.themes_dir = self.output_dir / "themes"
        
        for directory in [self.books_dir, self.concepts_dir, self.people_dir, self.themes_dir]:
            directory.mkdir(exist_ok=True)
    
    def generate_book_files(self, book: Book, analysis_result: Dict[str, Any]):
        """Generate all files for a book"""
        # Generate main book file
        self._generate_book_file(book, analysis_result)
        
        # Generate concept files
        self._generate_concept_files(book, analysis_result)
        
        # Generate people files
        self._generate_people_files(book, analysis_result)
        
        # Generate theme files
        self._generate_theme_files(book, analysis_result)
        
        # Generate index file
        self._generate_index_file()
    
    def _generate_book_file(self, book: Book, analysis_result: Dict[str, Any]):
        """Generate main book file"""
        filename = self._sanitize_filename(book.metadata.title) + ".md"
        filepath = self.books_dir / filename
        
        content = self._generate_book_content(book, analysis_result)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info(f"Generated book file: {filepath}")
    
    def _generate_book_content(self, book: Book, analysis_result: Dict[str, Any]) -> str:
        """Generate content for book file"""
        metadata = book.metadata
        
        # Build content sections
        sections = []
        
        # Header
        sections.append(f"# {metadata.title}")
        sections.append("")
        sections.append(f"**作者**: {metadata.author}")
        if metadata.subtitle:
            sections.append(f"**副标题**: {metadata.subtitle}")
        if metadata.translator:
            sections.append(f"**译者**: {metadata.translator}")
        if metadata.publisher:
            sections.append(f"**出版社**: {metadata.publisher}")
        if metadata.year:
            sections.append(f"**出版年份**: {metadata.year}")
        sections.append(f"**标注总数**: {len(book.highlights)}")
        sections.append(f"**处理日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sections.append("")
        
        # Summary
        if "book_summary" in analysis_result:
            sections.append("## 📊 分析摘要")
            sections.append(analysis_result["book_summary"])
            sections.append("")
        
        # Statistics
        if "statistics" in analysis_result:
            stats = analysis_result["statistics"]
            sections.append("## 📈 统计信息")
            sections.append(f"- **总标注数**: {stats.get('total_highlights', 0)}")
            sections.append(f"- **平均重要性**: {stats.get('average_importance', 0):.2f}")
            sections.append("")
            
            # Top concepts
            if "top_concepts" in stats and stats["top_concepts"]:
                sections.append("### 🔥 核心概念")
                for concept, count in stats["top_concepts"][:5]:
                    sections.append(f"- [[{concept}]] ({count}次)")
                sections.append("")
            
            # Top themes
            if "top_themes" in stats and stats["top_themes"]:
                sections.append("### 🎯 主要主题")
                for theme, count in stats["top_themes"][:3]:
                    sections.append(f"- [[{theme}]] ({count}次)")
                sections.append("")
        
        # Highlights by section
        sections.append("## 📝 标注内容")
        highlights_by_section = book.get_highlights_by_section()
        
        for section, highlights in highlights_by_section.items():
            sections.append(f"### {section}")
            sections.append("")
            
            for highlight in highlights:
                # Find analysis result for this highlight
                highlight_analysis = self._find_highlight_analysis(highlight, analysis_result["analysis_results"])
                
                sections.append(f"#### 标注 - 第{highlight.location.page}页 (位置{highlight.location.position})")
                sections.append("")
                sections.append(f"> {highlight.content}")
                sections.append("")
                
                if highlight_analysis:
                    # Add analysis information
                    if highlight_analysis.get("concepts"):
                        concepts = [f"[[{c}]]" for c in highlight_analysis["concepts"]]
                        sections.append(f"**概念**: {', '.join(concepts)}")
                        sections.append("")
                    
                    if highlight_analysis.get("themes"):
                        themes = [f"[[{t}]]" for t in highlight_analysis["themes"]]
                        sections.append(f"**主题**: {', '.join(themes)}")
                        sections.append("")
                    
                    if highlight_analysis.get("people"):
                        people = [f"[[{p}]]" for p in highlight_analysis["people"]]
                        sections.append(f"**人物**: {', '.join(people)}")
                        sections.append("")
                    
                    if highlight_analysis.get("tags"):
                        sections.append(f"**标签**: {' '.join(highlight_analysis['tags'])}")
                        sections.append("")
                    
                    if highlight_analysis.get("summary"):
                        sections.append(f"**摘要**: {highlight_analysis['summary']}")
                        sections.append("")
                
                sections.append("---")
                sections.append("")
        
        return "\n".join(sections)
    
    def _generate_concept_files(self, book: Book, analysis_result: Dict[str, Any]):
        """Generate concept files"""
        concepts = set()
        
        for result in analysis_result["analysis_results"]:
            concepts.update(result.get("concepts", []))
        
        for concept in concepts:
            self._generate_concept_file(concept, book, analysis_result)
    
    def _generate_concept_file(self, concept: str, book: Book, analysis_result: Dict[str, Any]):
        """Generate a single concept file"""
        filename = self._sanitize_filename(concept) + ".md"
        filepath = self.concepts_dir / filename
        
        content = self._generate_concept_content(concept, book, analysis_result)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info(f"Generated concept file: {filepath}")
    
    def _generate_concept_content(self, concept: str, book: Book, analysis_result: Dict[str, Any]) -> str:
        """Generate content for concept file"""
        sections = []
        
        sections.append(f"# {concept}")
        sections.append("")
        sections.append(f"**类型**: 概念")
        sections.append(f"**来源书籍**: [[{book.metadata.title}]]")
        sections.append("")
        
        # Find related highlights
        related_highlights = []
        for result in analysis_result["analysis_results"]:
            if concept in result.get("concepts", []):
                related_highlights.append(result)
        
        if related_highlights:
            sections.append("## 📝 相关标注")
            sections.append("")
            
            for result in related_highlights[:5]:  # Show top 5
                sections.append(f"> {result.get('summary', 'N/A')}")
                sections.append("")
                if result.get("tags"):
                    sections.append(f"标签: {' '.join(result['tags'])}")
                sections.append("")
        
        # Add related concepts
        related_concepts = self._find_related_concepts(concept, analysis_result)
        if related_concepts:
            sections.append("## 🔗 相关概念")
            sections.append("")
            for related_concept in related_concepts:
                sections.append(f"- [[{related_concept}]]")
            sections.append("")
        
        return "\n".join(sections)
    
    def _generate_people_files(self, book: Book, analysis_result: Dict[str, Any]):
        """Generate people files"""
        people = set()
        
        for result in analysis_result["analysis_results"]:
            people.update(result.get("people", []))
        
        for person in people:
            self._generate_person_file(person, book, analysis_result)
    
    def _generate_person_file(self, person: str, book: Book, analysis_result: Dict[str, Any]):
        """Generate a single person file"""
        filename = self._sanitize_filename(person) + ".md"
        filepath = self.people_dir / filename
        
        content = self._generate_person_content(person, book, analysis_result)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info(f"Generated person file: {filepath}")
    
    def _generate_person_content(self, person: str, book: Book, analysis_result: Dict[str, Any]) -> str:
        """Generate content for person file"""
        sections = []
        
        sections.append(f"# {person}")
        sections.append("")
        sections.append(f"**类型**: 人物")
        sections.append(f"**来源书籍**: [[{book.metadata.title}]]")
        sections.append("")
        
        # Find related highlights
        related_highlights = []
        for result in analysis_result["analysis_results"]:
            if person in result.get("people", []):
                related_highlights.append(result)
        
        if related_highlights:
            sections.append("## 📝 相关标注")
            sections.append("")
            
            for result in related_highlights[:5]:  # Show top 5
                sections.append(f"> {result.get('summary', 'N/A')}")
                sections.append("")
        
        return "\n".join(sections)
    
    def _generate_theme_files(self, book: Book, analysis_result: Dict[str, Any]):
        """Generate theme files"""
        themes = set()
        
        for result in analysis_result["analysis_results"]:
            themes.update(result.get("themes", []))
        
        for theme in themes:
            self._generate_theme_file(theme, book, analysis_result)
    
    def _generate_theme_file(self, theme: str, book: Book, analysis_result: Dict[str, Any]):
        """Generate a single theme file"""
        filename = self._sanitize_filename(theme) + ".md"
        filepath = self.themes_dir / filename
        
        content = self._generate_theme_content(theme, book, analysis_result)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info(f"Generated theme file: {filepath}")
    
    def _generate_theme_content(self, theme: str, book: Book, analysis_result: Dict[str, Any]) -> str:
        """Generate content for theme file"""
        sections = []
        
        sections.append(f"# {theme}")
        sections.append("")
        sections.append(f"**类型**: 主题")
        sections.append(f"**来源书籍**: [[{book.metadata.title}]]")
        sections.append("")
        
        # Find related highlights
        related_highlights = []
        for result in analysis_result["analysis_results"]:
            if theme in result.get("themes", []):
                related_highlights.append(result)
        
        if related_highlights:
            sections.append("## 📝 相关标注")
            sections.append("")
            
            for result in related_highlights[:5]:  # Show top 5
                sections.append(f"> {result.get('summary', 'N/A')}")
                sections.append("")
        
        return "\n".join(sections)
    
    def _generate_index_file(self):
        """Generate main index file"""
        filepath = self.output_dir / "index.md"
        
        content = self._generate_index_content()
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info(f"Generated index file: {filepath}")
    
    def _generate_index_content(self) -> str:
        """Generate content for index file"""
        sections = []
        
        sections.append("# 📚 Kindle 阅读助手知识库")
        sections.append("")
        sections.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sections.append("")
        
        # Books
        if self.books_dir.exists():
            books = list(self.books_dir.glob("*.md"))
            if books:
                sections.append("## 📖 书籍")
                sections.append("")
                for book_file in sorted(books):
                    book_name = book_file.stem
                    sections.append(f"- [[books/{book_name}]]")
                sections.append("")
        
        # Concepts
        if self.concepts_dir.exists():
            concepts = list(self.concepts_dir.glob("*.md"))
            if concepts:
                sections.append("## 💡 概念")
                sections.append("")
                for concept_file in sorted(concepts):
                    concept_name = concept_file.stem
                    sections.append(f"- [[concepts/{concept_name}]]")
                sections.append("")
        
        # People
        if self.people_dir.exists():
            people = list(self.people_dir.glob("*.md"))
            if people:
                sections.append("## 👥 人物")
                sections.append("")
                for person_file in sorted(people):
                    person_name = person_file.stem
                    sections.append(f"- [[people/{person_name}]]")
                sections.append("")
        
        # Themes
        if self.themes_dir.exists():
            themes = list(self.themes_dir.glob("*.md"))
            if themes:
                sections.append("## 🎯 主题")
                sections.append("")
                for theme_file in sorted(themes):
                    theme_name = theme_file.stem
                    sections.append(f"- [[themes/{theme_name}]]")
                sections.append("")
        
        return "\n".join(sections)
    
    def _find_highlight_analysis(self, highlight, analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find analysis result for a specific highlight"""
        highlight_id = f"{highlight.location.page}_{highlight.location.position}"
        
        for result in analysis_results:
            if result.get("highlight_id") == highlight_id:
                return result
        
        return {}
    
    def _find_related_concepts(self, concept: str, analysis_result: Dict[str, Any]) -> List[str]:
        """Find concepts that often appear together"""
        concept_cooccurrence = {}
        
        for result in analysis_result["analysis_results"]:
            concepts = result.get("concepts", [])
            if concept in concepts:
                for other_concept in concepts:
                    if other_concept != concept:
                        concept_cooccurrence[other_concept] = concept_cooccurrence.get(other_concept, 0) + 1
        
        # Sort by frequency and return top 5
        sorted_concepts = sorted(concept_cooccurrence.items(), key=lambda x: x[1], reverse=True)
        return [concept for concept, count in sorted_concepts[:5]]
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for file system"""
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