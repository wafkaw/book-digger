"""
Obsidian generator for creating markdown files from book analysis
"""
import os
import json
from typing import Dict, Any, List, Tuple
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
    
    def generate_book_files(self, book: Book, analysis_result: Dict[str, Any], aggregated_mode: bool = True):
        """Generate all files for a book with optional aggregation mode"""
        if aggregated_mode:
            # Generate aggregated book-level files (fewer, richer files)
            self._generate_aggregated_book_files(book, analysis_result)
        else:
            # Generate individual files for each concept/theme (original mode)
            self._generate_individual_files(book, analysis_result)
        
        # Always generate index file
        self._generate_index_file()
    
    def _generate_aggregated_book_files(self, book: Book, analysis_result: Dict[str, Any]):
        """Generate aggregated book-level files"""
        # Generate main book file with comprehensive analysis
        self._generate_comprehensive_book_file(book, analysis_result)
        
        # Generate aggregated concept overview file
        self._generate_concepts_overview_file(book, analysis_result)
        
        # Generate aggregated themes overview file  
        self._generate_themes_overview_file(book, analysis_result)
        
        # Generate people file (if any people mentioned)
        all_people = set()
        for result in analysis_result["analysis_results"]:
            all_people.update(result.get("people", []))
        
        if all_people:
            self._generate_people_overview_file(book, analysis_result, list(all_people))
    
    def _generate_individual_files(self, book: Book, analysis_result: Dict[str, Any]):
        """Generate individual files for each concept/theme (original mode)"""
        # Generate main book file
        self._generate_book_file(book, analysis_result)
        
        # Generate concept files
        self._generate_concept_files(book, analysis_result)
        
        # Generate people files
        self._generate_people_files(book, analysis_result)
        
        # Generate theme files
        self._generate_theme_files(book, analysis_result)
    
    def _generate_book_file(self, book: Book, analysis_result: Dict[str, Any]):
        """Generate main book file"""
        filename = self._sanitize_filename(book.metadata.title) + ".md"
        filepath = self.books_dir / filename
        
        content = self._generate_book_content(book, analysis_result)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info(f"Generated book file: {filepath}")
    
    def _generate_comprehensive_book_file(self, book: Book, analysis_result: Dict[str, Any]):
        """Generate comprehensive book file with full analysis"""
        filename = self._sanitize_filename(book.metadata.title) + "_全面分析.md"
        filepath = self.books_dir / filename
        
        content = self._generate_comprehensive_book_content(book, analysis_result)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info(f"Generated comprehensive book file: {filepath}")
    
    def _generate_comprehensive_book_content(self, book: Book, analysis_result: Dict[str, Any]) -> str:
        """Generate comprehensive book content"""
        sections = []
        
        # Title and metadata
        sections.append(f"# {book.metadata.title} - 全面分析")
        sections.append("")
        sections.append(f"**作者**: {book.metadata.author}")
        sections.append(f"**分析日期**: {datetime.now().strftime('%Y-%m-%d')}")
        sections.append(f"**标注数量**: {len(book.highlights)}")
        sections.append("")
        
        # Book summary
        if "book_summary" in analysis_result:
            sections.append("## 📚 书籍概述")
            sections.append("")
            sections.append(analysis_result["book_summary"])
            sections.append("")
        
        # Core concepts aggregation
        all_concepts = set()
        for result in analysis_result["analysis_results"]:
            all_concepts.update(result.get("concepts", []))
        
        if all_concepts:
            sections.append("## 💡 核心概念")
            sections.append("")
            for concept in sorted(all_concepts):
                related_highlights = self._get_highlights_for_concept(concept, analysis_result)
                sections.append(f"### {concept}")
                sections.append("")
                if related_highlights:
                    sections.append("相关标注:")
                    for highlight in related_highlights[:3]:  # Show top 3
                        sections.append(f"- {highlight[:100]}...")
                sections.append("")
        
        # Core themes aggregation  
        all_themes = set()
        for result in analysis_result["analysis_results"]:
            all_themes.update(result.get("themes", []))
        
        if all_themes:
            sections.append("## 🎭 主要主题")
            sections.append("")
            for theme in sorted(all_themes):
                related_highlights = self._get_highlights_for_theme(theme, analysis_result)
                sections.append(f"### {theme}")
                sections.append("")
                if related_highlights:
                    sections.append("相关标注:")
                    for highlight in related_highlights[:3]:
                        sections.append(f"- {highlight[:100]}...")
                sections.append("")
        
        # Important highlights by score
        important_highlights = []
        for i, result in enumerate(analysis_result["analysis_results"]):
            if result.get("importance_score", 0) >= 0.7:
                important_highlights.append((book.highlights[i], result))
        
        if important_highlights:
            sections.append("## ⭐ 重要标注")
            sections.append("")
            for highlight, result in sorted(important_highlights, key=lambda x: x[1].get("importance_score", 0), reverse=True):
                sections.append(f"### 重要性: {result.get('importance_score', 0):.1f}")
                sections.append("")
                sections.append(f"> {highlight.content}")
                sections.append("")
                if result.get("summary"):
                    sections.append(f"**分析**: {result['summary']}")
                    sections.append("")
        
        return "\n".join(sections)
    
    def _get_highlights_for_concept(self, concept: str, analysis_result: Dict[str, Any]) -> List[str]:
        """Get highlights related to a specific concept"""
        highlights = []
        for i, result in enumerate(analysis_result["analysis_results"]):
            if concept in result.get("concepts", []):
                highlights.append(analysis_result["book"]["highlights"][i]["content"])
        return highlights
    
    def _get_highlights_for_theme(self, theme: str, analysis_result: Dict[str, Any]) -> List[str]:
        """Get highlights related to a specific theme"""
        highlights = []
        for i, result in enumerate(analysis_result["analysis_results"]):
            if theme in result.get("themes", []):
                highlights.append(analysis_result["book"]["highlights"][i]["content"])
        return highlights
    
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
        """Generate content for concept file with enhanced linking"""
        sections = []
        
        sections.append(f"# {concept}")
        sections.append("")
        sections.append(f"**类型**: 概念")
        sections.append(f"**来源书籍**: [[{book.metadata.title}]]")
        sections.append("")
        
        # Add concept tags for Graph View clustering
        concept_type = self._classify_concept_type(concept)
        sections.append(f"**概念类型**: #{concept_type}")
        sections.append("")
        
        # Find related highlights with enhanced content
        related_highlights = []
        for result in analysis_result["analysis_results"]:
            if concept in result.get("concepts", []):
                related_highlights.append(result)
        
        if related_highlights:
            sections.append("## 📝 相关标注")
            sections.append("")
            
            for i, result in enumerate(related_highlights[:3]):  # Show top 3 with more detail
                importance = result.get("importance_score", 0.5)
                sections.append(f"### 标注 {i+1} (重要性: {importance:.1f})")
                
                # Add links to other concepts in the same highlight
                other_concepts = [c for c in result.get("concepts", []) if c != concept]
                if other_concepts:
                    concept_links = ", ".join([f"[[{c}]]" for c in other_concepts])
                    sections.append(f"**相关概念**: {concept_links}")
                
                # Add theme links
                themes = result.get("themes", [])
                if themes:
                    theme_links = ", ".join([f"[[{t}]]" for t in themes])
                    sections.append(f"**相关主题**: {theme_links}")
                
                # Add people links
                people = result.get("people", [])
                if people:
                    people_links = ", ".join([f"[[{p}]]" for p in people])
                    sections.append(f"**相关人物**: {people_links}")
                
                sections.append("")
                sections.append(f"> {result.get('summary', 'N/A')}")
                sections.append("")
        
        # Enhanced related concepts with semantic similarity
        related_concepts = self._find_enhanced_related_concepts(concept, analysis_result)
        if related_concepts:
            sections.append("## 🔗 相关概念")
            sections.append("")
            for related_concept, strength in related_concepts:
                sections.append(f"- [[{related_concept}]] (关联度: {strength:.2f})")
            sections.append("")
        
        # Add related themes
        related_themes = self._find_related_themes_for_concept(concept, analysis_result)
        if related_themes:
            sections.append("## 🎭 相关主题")
            sections.append("")
            for theme in related_themes:
                sections.append(f"- [[{theme}]]")
            sections.append("")
        
        # Add conceptual network section
        sections.append("## 🌐 概念网络")
        sections.append("")
        sections.append(f"此概念在 [[{book.metadata.title}]] 的知识网络中起到重要作用。")
        sections.append(f"通过 #概念图谱 标签可在Graph View中查看完整关联。")
        sections.append("")
        sections.append("### 探索建议")
        sections.append("- 点击相关概念深入理解概念群")
        sections.append("- 查看相关主题了解更广泛的思想背景") 
        sections.append("- 通过Graph View发现意想不到的概念联系")
        sections.append("")
        
        # Add tags for better Graph View organization
        all_tags = ["#概念", f"#{concept_type}", "#概念图谱"]
        sections.append(f"标签: {' '.join(all_tags)}")
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
        """Generate content for person file with enhanced linking"""
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
            sections.append("## 📝 相关内容")
            sections.append("")
            
            for i, result in enumerate(related_highlights[:3]):
                importance = result.get("importance_score", 0.5)
                sections.append(f"### 引用 {i+1} (重要性: {importance:.1f})")
                
                # Add concept links
                concepts = result.get("concepts", [])
                if concepts:
                    concept_links = ", ".join([f"[[{c}]]" for c in concepts])
                    sections.append(f"**相关概念**: {concept_links}")
                
                # Add theme links  
                themes = result.get("themes", [])
                if themes:
                    theme_links = ", ".join([f"[[{t}]]" for t in themes])
                    sections.append(f"**相关主题**: {theme_links}")
                
                sections.append("")
                sections.append(f"> {result.get('summary', 'N/A')}")
                sections.append("")
        
        # Find concepts associated with this person
        related_concepts = self._find_concepts_for_person(person, analysis_result)
        if related_concepts:
            sections.append("## 🧠 相关概念")
            sections.append("")
            for concept in related_concepts:
                sections.append(f"- [[{concept}]]")
            sections.append("")
        
        # Find themes associated with this person
        related_themes = self._find_themes_for_person(person, analysis_result)
        if related_themes:
            sections.append("## 🎭 相关主题")
            sections.append("")
            for theme in related_themes:
                sections.append(f"- [[{theme}]]")
            sections.append("")
        
        sections.append("## 🌐 人物网络")
        sections.append("")
        sections.append(f"{person} 在 [[{book.metadata.title}]] 中与多个哲学概念相关联。")
        sections.append("通过 #人物图谱 标签可在Graph View中查看人物关系。")
        sections.append("")
        
        # Add tags
        sections.append("标签: #人物 #人物图谱")
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
        """Generate content for theme file with enhanced linking"""
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
            
            for i, result in enumerate(related_highlights[:3]):
                importance = result.get("importance_score", 0.5)
                sections.append(f"### 标注 {i+1} (重要性: {importance:.1f})")
                
                # Add concept links
                concepts = result.get("concepts", [])
                if concepts:
                    concept_links = ", ".join([f"[[{c}]]" for c in concepts])
                    sections.append(f"**相关概念**: {concept_links}")
                
                # Add people links
                people = result.get("people", [])
                if people:
                    people_links = ", ".join([f"[[{p}]]" for p in people])
                    sections.append(f"**相关人物**: {people_links}")
                
                sections.append("")
                sections.append(f"> {result.get('summary', 'N/A')}")
                sections.append("")
        
        # Find related concepts for this theme
        related_concepts = self._find_concepts_for_theme(theme, analysis_result)
        if related_concepts:
            sections.append("## 🧠 核心概念")
            sections.append("")
            for concept in related_concepts:
                sections.append(f"- [[{concept}]]")
            sections.append("")
        
        # Find related themes
        related_themes = self._find_related_themes(theme, analysis_result)
        if related_themes:
            sections.append("## 🔗 相关主题")
            sections.append("")
            for related_theme in related_themes:
                sections.append(f"- [[{related_theme}]]")
            sections.append("")
        
        sections.append("## 🌐 主题网络")
        sections.append("")
        sections.append(f"此主题在 [[{book.metadata.title}]] 中贯穿多个重要概念。")
        sections.append("通过 #主题图谱 标签可在Graph View中查看主题关联。")
        sections.append("")
        
        # Add tags
        sections.append("标签: #主题 #主题图谱")
        sections.append("")
        
        return "\n".join(sections)
    
    def _generate_index_file(self):
        """Generate main index file"""
        filepath = self.output_dir / "index.md"
        
        content = self._generate_index_content()
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info(f"Generated index file: {filepath}")
    
    def _generate_concepts_overview_file(self, book: Book, analysis_result: Dict[str, Any]):
        """Generate aggregated concepts overview file"""
        filename = f"{self._sanitize_filename(book.metadata.title)}_概念总览.md"
        filepath = self.concepts_dir / filename
        
        content = self._generate_concepts_overview_content(book, analysis_result)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info(f"Generated concepts overview file: {filepath}")
    
    def _generate_concepts_overview_content(self, book: Book, analysis_result: Dict[str, Any]) -> str:
        """Generate concepts overview content"""
        sections = []
        
        sections.append(f"# {book.metadata.title} - 概念总览")
        sections.append("")
        sections.append(f"**作者**: {book.metadata.author}")
        sections.append(f"**类型**: 概念总览")
        sections.append(f"**来源书籍**: [[{book.metadata.title}]]")
        sections.append("")
        
        # Collect and organize concepts
        concept_highlights = {}
        for i, result in enumerate(analysis_result["analysis_results"]):
            highlight = book.highlights[i]
            for concept in result.get("concepts", []):
                if concept not in concept_highlights:
                    concept_highlights[concept] = []
                concept_highlights[concept].append({
                    'content': highlight.content,
                    'importance': result.get('importance_score', 0.5),
                    'summary': result.get('summary', '')
                })
        
        # Sort concepts by importance and frequency
        sorted_concepts = sorted(concept_highlights.items(), 
                               key=lambda x: (len(x[1]), max(h['importance'] for h in x[1])), 
                               reverse=True)
        
        sections.append("## 📊 概念统计")
        sections.append("")
        sections.append(f"- 总概念数: {len(sorted_concepts)}")
        sections.append(f"- 主要概念: {', '.join([c[0] for c in sorted_concepts[:5]])}")
        sections.append("")
        
        sections.append("## 💡 核心概念详解")
        sections.append("")
        
        for concept, highlights in sorted_concepts:
            sections.append(f"### {concept}")
            sections.append("")
            sections.append(f"**出现次数**: {len(highlights)}")
            
            # Show most important highlight for this concept
            best_highlight = max(highlights, key=lambda x: x['importance'])
            sections.append(f"**最重要标注** (重要性: {best_highlight['importance']:.1f}):")
            sections.append(f"> {best_highlight['content']}")
            sections.append("")
            
            if best_highlight['summary']:
                sections.append(f"**分析**: {best_highlight['summary']}")
                sections.append("")
            
            # Show other related highlights (up to 2 more)
            other_highlights = [h for h in highlights if h != best_highlight][:2]
            if other_highlights:
                sections.append("其他相关标注:")
                for h in other_highlights:
                    sections.append(f"- {h['content'][:80]}...")
                sections.append("")
        
        return "\n".join(sections)
    
    def _generate_themes_overview_file(self, book: Book, analysis_result: Dict[str, Any]):
        """Generate aggregated themes overview file"""
        filename = f"{self._sanitize_filename(book.metadata.title)}_主题总览.md"
        filepath = self.themes_dir / filename
        
        content = self._generate_themes_overview_content(book, analysis_result)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info(f"Generated themes overview file: {filepath}")
    
    def _generate_themes_overview_content(self, book: Book, analysis_result: Dict[str, Any]) -> str:
        """Generate themes overview content"""
        sections = []
        
        sections.append(f"# {book.metadata.title} - 主题总览")
        sections.append("")
        sections.append(f"**作者**: {book.metadata.author}")
        sections.append(f"**类型**: 主题总览")
        sections.append(f"**来源书籍**: [[{book.metadata.title}]]")
        sections.append("")
        
        # Collect and organize themes
        theme_highlights = {}
        for i, result in enumerate(analysis_result["analysis_results"]):
            highlight = book.highlights[i]
            for theme in result.get("themes", []):
                if theme not in theme_highlights:
                    theme_highlights[theme] = []
                theme_highlights[theme].append({
                    'content': highlight.content,
                    'importance': result.get('importance_score', 0.5),
                    'summary': result.get('summary', '')
                })
        
        # Sort themes by importance and frequency
        sorted_themes = sorted(theme_highlights.items(), 
                              key=lambda x: (len(x[1]), max(h['importance'] for h in x[1])), 
                              reverse=True)
        
        sections.append("## 📊 主题统计")
        sections.append("")
        sections.append(f"- 总主题数: {len(sorted_themes)}")
        sections.append(f"- 主要主题: {', '.join([t[0] for t in sorted_themes[:3]])}")
        sections.append("")
        
        sections.append("## 🎭 主题详解")
        sections.append("")
        
        for theme, highlights in sorted_themes:
            sections.append(f"### {theme}")
            sections.append("")
            sections.append(f"**涵盖标注**: {len(highlights)} 个")
            
            # Show most important highlights for this theme
            top_highlights = sorted(highlights, key=lambda x: x['importance'], reverse=True)[:3]
            sections.append("代表性标注:")
            for i, h in enumerate(top_highlights, 1):
                sections.append(f"{i}. {h['content'][:120]}... (重要性: {h['importance']:.1f})")
            sections.append("")
        
        return "\n".join(sections)
    
    def _generate_people_overview_file(self, book: Book, analysis_result: Dict[str, Any], all_people: List[str]):
        """Generate aggregated people overview file"""
        filename = f"{self._sanitize_filename(book.metadata.title)}_人物总览.md"
        filepath = self.people_dir / filename
        
        content = self._generate_people_overview_content(book, analysis_result, all_people)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info(f"Generated people overview file: {filepath}")
    
    def _generate_people_overview_content(self, book: Book, analysis_result: Dict[str, Any], all_people: List[str]) -> str:
        """Generate people overview content"""
        sections = []
        
        sections.append(f"# {book.metadata.title} - 人物总览")
        sections.append("")
        sections.append(f"**作者**: {book.metadata.author}")
        sections.append(f"**类型**: 人物总览")
        sections.append(f"**来源书籍**: [[{book.metadata.title}]]")
        sections.append("")
        
        sections.append("## 👥 涉及人物")
        sections.append("")
        
        # Collect mentions for each person
        person_mentions = {}
        for i, result in enumerate(analysis_result["analysis_results"]):
            highlight = book.highlights[i]
            for person in result.get("people", []):
                if person not in person_mentions:
                    person_mentions[person] = []
                person_mentions[person].append(highlight.content)
        
        for person in all_people:
            sections.append(f"### {person}")
            sections.append("")
            if person in person_mentions:
                sections.append(f"**提及次数**: {len(person_mentions[person])}")
                sections.append("相关标注:")
                for mention in person_mentions[person][:3]:  # Show top 3 mentions
                    sections.append(f"- {mention[:100]}...")
            sections.append("")
        
        return "\n".join(sections)
    
    def _generate_index_content(self) -> str:
        """Generate enhanced content for index file with graph navigation"""
        sections = []
        
        sections.append("# 📚 智能知识图谱 - Obsidian双向链接网络")
        sections.append("")
        sections.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sections.append("")
        
        sections.append("## 🌐 图谱导航")
        sections.append("")
        sections.append("### 📈 Graph View 使用指南")
        sections.append("1. 打开 **Graph View** (Ctrl/Cmd + G) 查看完整知识网络")
        sections.append("2. 使用以下标签过滤不同类型的节点:")
        sections.append("   - `#概念` - 查看所有概念及其关联")
        sections.append("   - `#主题` - 查看主题网络")
        sections.append("   - `#人物` - 查看人物关系")
        sections.append("   - `#概念图谱` - 专注于概念关系网络")
        sections.append("3. 点击任意节点深入探索相关内容")
        sections.append("4. 调整 **Link Distance** 和 **Repel Force** 优化图谱布局")
        sections.append("")
        
        sections.append("### 🎯 智能探索入口")
        sections.append("")
        
        # Books with enhanced linking
        if self.books_dir.exists():
            books = list(self.books_dir.glob("*.md"))
            if books:
                sections.append("## 📖 书籍分析")
                sections.append("")
                for book_file in sorted(books):
                    book_name = book_file.stem
                    sections.append(f"- [[{book_name}]] - 完整的概念与主题网络")
                sections.append("")
        
        # Concepts with categorization
        if self.concepts_dir.exists():
            concepts = list(self.concepts_dir.glob("*.md"))
            if concepts:
                sections.append(f"## 💡 核心概念 ({len(concepts)} 个)")
                sections.append("")
                sections.append("### 🔥 热门概念 (点击探索关联网络)")
                # Show first 10 as hot concepts
                for concept_file in sorted(concepts)[:10]:
                    concept_name = concept_file.stem
                    sections.append(f"- [[{concept_name}]] #热门概念")
                
                if len(concepts) > 10:
                    sections.append("")
                    sections.append("### 📋 完整概念列表")
                    sections.append("")
                    for concept_file in sorted(concepts)[10:]:
                        concept_name = concept_file.stem
                        sections.append(f"- [[{concept_name}]]")
                sections.append("")
        
        # Themes
        if self.themes_dir.exists():
            themes = list(self.themes_dir.glob("*.md"))
            if themes:
                sections.append(f"## 🎭 核心主题 ({len(themes)} 个)")
                sections.append("")
                for theme_file in sorted(themes):
                    theme_name = theme_file.stem
                    sections.append(f"- [[{theme_name}]]")
                sections.append("")
        
        # People
        if self.people_dir.exists():
            people = list(self.people_dir.glob("*.md"))
            if people:
                sections.append(f"## 👥 重要人物 ({len(people)} 个)")
                sections.append("")
                for person_file in sorted(people):
                    person_name = person_file.stem
                    sections.append(f"- [[{person_name}]]")
                sections.append("")
        
        # Navigation tips
        sections.append("## 🧭 知识探索建议")
        sections.append("")
        sections.append("### 🔍 发现新联系")
        sections.append("- **从概念开始**: 选择感兴趣的概念，查看其相关概念网络")
        sections.append("- **主题导航**: 通过主题页面了解某个思想领域的完整概念群")
        sections.append("- **人物视角**: 从重要人物出发，了解其相关的哲学思想")
        sections.append("- **Graph View漫游**: 在图谱中自由探索，发现意想不到的概念联系")
        sections.append("")
        
        sections.append("### 🎨 个性化探索")
        sections.append("- 使用 **Local Graph** 查看当前页面的局部关系")
        sections.append("- 通过 **Filter** 面板自定义显示内容")  
        sections.append("- 保存有趣的图谱视图截图作为思维导图")
        sections.append("")
        
        sections.append("---")
        sections.append("")
        sections.append("**🚀 开始探索**: 点击上方任意链接，开始你的知识发现之旅！")
        sections.append("")
        
        # Meta tags for graph organization
        sections.append("标签: #索引 #导航 #知识图谱")
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
    
    def _find_enhanced_related_concepts(self, concept: str, analysis_result: Dict[str, Any]) -> List[Tuple[str, float]]:
        """Find related concepts with semantic similarity scoring"""
        concept_scores = {}
        concept_total_importance = {}
        
        for result in analysis_result["analysis_results"]:
            concepts = result.get("concepts", [])
            importance = result.get("importance_score", 0.5)
            
            if concept in concepts:
                for other_concept in concepts:
                    if other_concept != concept:
                        # Weight by importance and co-occurrence
                        concept_scores[other_concept] = concept_scores.get(other_concept, 0) + importance
                        concept_total_importance[other_concept] = concept_total_importance.get(other_concept, 0) + 1
        
        # Calculate relationship strength (average importance * frequency factor)
        related_concepts = []
        for other_concept, total_importance in concept_scores.items():
            frequency = concept_total_importance[other_concept]
            # Relationship strength = average importance * log(frequency + 1)
            import math
            strength = (total_importance / frequency) * math.log(frequency + 1)
            related_concepts.append((other_concept, strength))
        
        # Sort by strength and return top 5
        related_concepts.sort(key=lambda x: x[1], reverse=True)
        return related_concepts[:5]
    
    def _find_related_themes_for_concept(self, concept: str, analysis_result: Dict[str, Any]) -> List[str]:
        """Find themes that are associated with this concept"""
        theme_counts = {}
        
        for result in analysis_result["analysis_results"]:
            concepts = result.get("concepts", [])
            themes = result.get("themes", [])
            
            if concept in concepts:
                for theme in themes:
                    theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        # Sort by frequency and return top 3
        sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
        return [theme for theme, count in sorted_themes[:3]]
    
    def _classify_concept_type(self, concept: str) -> str:
        """Classify concept type for better organization"""
        concept_lower = concept.lower()
        
        # 哲学概念
        if any(word in concept_lower for word in ['存在', '自由', '意志', '真理', '本质', '超越', '永恒', '虚无']):
            return "哲学概念"
        
        # 心理学概念  
        if any(word in concept_lower for word in ['焦虑', '恐惧', '欲望', '情感', '心理', '意识', '潜意识']):
            return "心理概念"
        
        # 人际关系
        if any(word in concept_lower for word in ['关系', '婚姻', '爱情', '友谊', '亲近', '孤独', '连接']):
            return "关系概念"
        
        # 价值观念
        if any(word in concept_lower for word in ['道德', '责任', '选择', '价值', '意义', '目标']):
            return "价值概念"
        
        # 生命哲学
        if any(word in concept_lower for word in ['生命', '死亡', '生活', '人生', '命运', '时间']):
            return "生命概念"
        
        # 默认
        return "核心概念"
    
    def _find_concepts_for_theme(self, theme: str, analysis_result: Dict[str, Any]) -> List[str]:
        """Find concepts that belong to this theme"""
        concept_counts = {}
        
        for result in analysis_result["analysis_results"]:
            themes = result.get("themes", [])
            concepts = result.get("concepts", [])
            
            if theme in themes:
                for concept in concepts:
                    concept_counts[concept] = concept_counts.get(concept, 0) + 1
        
        # Sort by frequency and return top 5
        sorted_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)
        return [concept for concept, count in sorted_concepts[:5]]
    
    def _find_related_themes(self, theme: str, analysis_result: Dict[str, Any]) -> List[str]:
        """Find themes that often appear together with this theme"""
        theme_cooccurrence = {}
        
        for result in analysis_result["analysis_results"]:
            themes = result.get("themes", [])
            if theme in themes:
                for other_theme in themes:
                    if other_theme != theme:
                        theme_cooccurrence[other_theme] = theme_cooccurrence.get(other_theme, 0) + 1
        
        # Sort by frequency and return top 3
        sorted_themes = sorted(theme_cooccurrence.items(), key=lambda x: x[1], reverse=True)
        return [theme for theme, count in sorted_themes[:3]]
    
    def _find_concepts_for_person(self, person: str, analysis_result: Dict[str, Any]) -> List[str]:
        """Find concepts associated with this person"""
        concept_counts = {}
        
        for result in analysis_result["analysis_results"]:
            people = result.get("people", [])
            concepts = result.get("concepts", [])
            
            if person in people:
                for concept in concepts:
                    concept_counts[concept] = concept_counts.get(concept, 0) + 1
        
        # Sort by frequency and return top 5
        sorted_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)
        return [concept for concept, count in sorted_concepts[:5]]
    
    def _find_themes_for_person(self, person: str, analysis_result: Dict[str, Any]) -> List[str]:
        """Find themes associated with this person"""
        theme_counts = {}
        
        for result in analysis_result["analysis_results"]:
            people = result.get("people", [])
            themes = result.get("themes", [])
            
            if person in people:
                for theme in themes:
                    theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        # Sort by frequency and return top 3
        sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
        return [theme for theme, count in sorted_themes[:3]]
    
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