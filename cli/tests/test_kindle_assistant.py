"""
Test cases for Kindle Reading Assistant
"""
import unittest
import json
from pathlib import Path
from datetime import datetime

from src.config.models import BookMetadata, Highlight, HighlightType, NoteType, Location
from src.data_collection.kindle_parser import KindleParser
from src.knowledge_graph.ai_analysis import AIAnalysisInterface


class TestKindleParser(unittest.TestCase):
    """Test cases for Kindle parser"""
    
    def setUp(self):
        self.parser = KindleParser()
        self.sample_html = """
        <html>
        <head><meta charset="UTF-8"></head>
        <body>
            <div class="bodyContainer">
                <div class="notebookFor">Notebook Export</div>
                <div class="bookTitle">当尼采哭泣 = When Nietzsche wept -- 欧文·亚隆(irvin D_yalom) & 侯维之 -- 1, US, 2017 -- 机械工业出版社</div>
                <div class="authors">欧文·亚隆(irvin D.yalom)</div>
                <div class="citation"></div>
                <hr />
                <div class="sectionHeading">第二章</div>
                <div class="noteHeading">Highlight(<span class="highlight_yellow">yellow</span>) - Page 29 · Location 364</div>
                <div class="noteText">测试内容</div>
                <div class="sectionHeading">第三章</div>
                <div class="noteHeading">Highlight(<span class="highlight_yellow">yellow</span>) - Page 50 · Location 500</div>
                <div class="noteText">另一个测试内容</div>
            </div>
        </body>
        </html>
        """
    
    def test_extract_metadata(self):
        """Test metadata extraction"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(self.sample_html, 'html.parser')
        
        metadata = self.parser._extract_metadata(soup)
        
        self.assertEqual(metadata.title, "当尼采哭泣")
        self.assertEqual(metadata.author, "欧文·亚隆(irvin D.yalom)")
        self.assertEqual(metadata.subtitle, "When Nietzsche wept")
        self.assertEqual(metadata.year, 2017)
        self.assertEqual(metadata.publisher, "机械工业出版社")
    
    def test_extract_location(self):
        """Test location extraction"""
        heading_text = "Highlight(yellow) - Page 29 · Location 364"
        location = self.parser._extract_location(heading_text)
        
        self.assertIsNotNone(location)
        self.assertEqual(location.page, 29)
        self.assertEqual(location.position, 364)
    
    def test_extract_highlight_type(self):
        """Test highlight type extraction"""
        heading_text = "Highlight(<span class=\"highlight_yellow\">yellow</span>) - Page 29 · Location 364"
        highlight_type = self.parser._extract_highlight_type(heading_text)
        
        self.assertEqual(highlight_type, HighlightType.YELLOW)
    
    def test_parse_html_content(self):
        """Test complete HTML parsing"""
        book = self.parser.parse_html_content(self.sample_html)
        
        self.assertEqual(book.metadata.title, "当尼采哭泣")
        self.assertEqual(len(book.highlights), 2)
        self.assertEqual(book.highlights[0].content, "测试内容")
        self.assertEqual(book.highlights[0].location.page, 29)
        self.assertEqual(book.highlights[1].content, "另一个测试内容")
        self.assertEqual(book.highlights[1].location.page, 50)


class TestAIAnalysis(unittest.TestCase):
    """Test cases for AI analysis"""
    
    def setUp(self):
        self.ai_interface = AIAnalysisInterface(mock_mode=True)
        self.sample_highlight = Highlight(
            content="尼采对权力的话题极其敏感。任何让他感到可能把他的权力拱手让人的程序，他都拒绝参与。",
            location=Location(page=29, position=364),
            highlight_type=HighlightType.YELLOW,
            section="第二章"
        )
    
    def test_analyze_highlight(self):
        """Test highlight analysis"""
        result = self.ai_interface.analyze_highlight(self.sample_highlight, "test_book")
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result.concepts, list)
        self.assertIsInstance(result.themes, list)
        self.assertIsInstance(result.emotions, list)
        self.assertIsInstance(result.people, list)
        self.assertIsInstance(result.importance_score, float)
        self.assertIsInstance(result.summary, str)
        self.assertIsInstance(result.tags, list)
        
        # Check that concepts are extracted
        self.assertIn("权力意志", result.concepts)
        
        # Check that importance score is between 0 and 1
        self.assertGreaterEqual(result.importance_score, 0.0)
        self.assertLessEqual(result.importance_score, 1.0)
    
    def test_extract_mock_concepts(self):
        """Test concept extraction"""
        content = "尼采对权力的话题极其敏感"
        concepts = self.ai_interface._extract_mock_concepts(content)
        
        self.assertIn("权力意志", concepts)
    
    def test_extract_mock_themes(self):
        """Test theme extraction"""
        content = "这是关于哲学思辨的内容"
        themes = self.ai_interface._extract_mock_themes(content)
        
        self.assertIn("哲学思辨", themes)
    
    def test_extract_mock_emotions(self):
        """Test emotion extraction"""
        content = "他感到焦虑和困惑"
        emotions = self.ai_interface._extract_mock_emotions(content)
        
        self.assertIn("焦虑", emotions)
        self.assertIn("困惑", emotions)
    
    def test_calculate_mock_importance(self):
        """Test importance calculation"""
        short_content = "短内容"
        long_content = "这是一个很长的内容，包含很多重要的哲学概念，比如权力、存在、死亡、爱情、自由、选择、责任、意义等深刻的思考。"
        
        short_score = self.ai_interface._calculate_mock_importance(short_content)
        long_score = self.ai_interface._calculate_mock_importance(long_content)
        
        self.assertGreater(long_score, short_score)


class TestBookMetadata(unittest.TestCase):
    """Test cases for book metadata"""
    
    def test_from_title_string(self):
        """Test metadata parsing from title string"""
        title_string = "当尼采哭泣 = When Nietzsche wept -- 欧文·亚隆(irvin D_yalom) & 侯维之 -- 1, US, 2017 -- 机械工业出版社"
        
        metadata = BookMetadata.from_title_string(title_string)
        
        self.assertEqual(metadata.title, "当尼采哭泣")
        self.assertEqual(metadata.subtitle, "When Nietzsche wept")
        self.assertEqual(metadata.author, "欧文·亚隆(irvin D_yalom)")
        self.assertEqual(metadata.year, 2017)
        self.assertEqual(metadata.country, "US")
        self.assertEqual(metadata.edition, "1")
        self.assertEqual(metadata.publisher, "机械工业出版社")
    
    def test_simple_title_string(self):
        """Test simple title string parsing"""
        title_string = "简单书名 -- 作者名"
        
        metadata = BookMetadata.from_title_string(title_string)
        
        self.assertEqual(metadata.title, "简单书名")
        self.assertEqual(metadata.author, "作者名")
        self.assertIsNone(metadata.subtitle)
        self.assertIsNone(metadata.year)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_end_to_end_processing(self):
        """Test complete processing pipeline"""
        # Create sample HTML file
        sample_html = """
        <html>
        <head><meta charset="UTF-8"></head>
        <body>
            <div class="bodyContainer">
                <div class="notebookFor">Notebook Export</div>
                <div class="bookTitle">测试书籍 = Test Book -- 测试作者 -- 1, US, 2023 -- 测试出版社</div>
                <div class="authors">测试作者</div>
                <div class="citation"></div>
                <hr />
                <div class="sectionHeading">第一章</div>
                <div class="noteHeading">Highlight(<span class="highlight_yellow">yellow</span>) - Page 10 · Location 100</div>
                <div class="noteText">这是一个关于权力和自由的哲学思考。</div>
                <div class="noteHeading">Highlight(<span class="highlight_yellow">yellow</span>) - Page 15 · Location 150</div>
                <div class="noteText">人生的意义是什么？这是一个深刻的哲学问题。</div>
            </div>
        </body>
        </html>
        """
        
        # Parse HTML
        parser = KindleParser()
        book = parser.parse_html_content(sample_html)
        
        # Analyze with AI
        ai_interface = AIAnalysisInterface(mock_mode=True)
        analysis_result = ai_interface.analyze_book(book)
        
        # Verify results
        self.assertEqual(book.metadata.title, "测试书籍")
        self.assertEqual(len(book.highlights), 2)
        self.assertEqual(len(analysis_result["analysis_results"]), 2)
        
        # Check that analysis contains expected fields
        for result in analysis_result["analysis_results"]:
            self.assertIn("concepts", result)
            self.assertIn("themes", result)
            self.assertIn("emotions", result)
            self.assertIn("people", result)
            self.assertIn("importance_score", result)
            self.assertIn("summary", result)
            self.assertIn("tags", result)


if __name__ == "__main__":
    unittest.main()