"""
AI analysis interface for processing highlights and extracting knowledge
"""
import random
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..config.models import (
    Highlight, Book, AIAnalysisResult, KnowledgeNode, KnowledgeEdge, KnowledgeGraph
)
from ..llm import create_llm_service


class AIAnalysisInterface:
    """AI interface for analyzing highlights and extracting knowledge"""
    
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM service (use real LLM by default)
        if not mock_mode:
            # Try to use Zhipu AI if available
            import os
            zhipu_key = os.getenv("ZHIPU_API_KEY")
            if zhipu_key:
                from ..llm.llm_service import LLMService
                self.llm_service = LLMService(
                    api_key=zhipu_key,
                    base_url="https://open.bigmodel.cn/api/paas/v4",
                    model="glm-4.5-air",
                    mock_mode=False
                )
                self.logger.info("Using Zhipu AI for LLM analysis")
            else:
                self.llm_service = create_llm_service(mock_mode=True)
                self.mock_mode = True
                self.logger.warning("No API key found, falling back to mock mode")
        else:
            self.llm_service = create_llm_service(mock_mode=mock_mode)
        
        # Mock data for simulation (fallback)
        self.concepts_database = [
            "权力意志", "存在焦虑", "死亡恐惧", "爱情哲学", "婚姻自由", 
            "自我实现", "选择责任", "孤独连接", "宗教信仰", "无神论",
            "精神分析", "心理学", "哲学治疗", "意识觉醒", "意义建构"
        ]
        
        self.themes_database = [
            "存在主义", "心理学", "哲学思辨", "人际关系", "自我认知",
            "情感分析", "生死观", "价值观", "道德伦理", "宗教哲学"
        ]
        
        self.emotions_database = [
            "焦虑", "困惑", "痛苦", "愤怒", "恐惧", "希望", "顿悟",
            "平静", "悲伤", "孤独", "渴望", "满足", "挣扎"
        ]
        
        self.people_database = [
            "尼采", "布雷尔", "弗洛伊德", "贝莎", "欧文·亚隆",
            "叔本华", "瓦格纳", "莎乐美", "耶稣", "上帝"
        ]
        
        self.relationships_database = [
            "相关概念", "对立观点", "支持论据", "批判对象", "影响关系",
            "同类主题", "因果关系", "条件关系", "包含关系", "交叉关系"
        ]
    
    def analyze_highlight(self, highlight: Highlight, book_id: str) -> AIAnalysisResult:
        """Analyze a single highlight and extract insights"""
        if self.mock_mode:
            return self._mock_analyze_highlight(highlight, book_id)
        else:
            return self._real_ai_analyze_highlight(highlight, book_id)
    
    def _mock_analyze_highlight(self, highlight: Highlight, book_id: str) -> AIAnalysisResult:
        """Mock AI analysis for testing purposes"""
        content = highlight.content
        
        # Simple keyword matching for simulation
        concepts = self._extract_mock_concepts(content)
        themes = self._extract_mock_themes(content)
        emotions = self._extract_mock_emotions(content)
        people = self._extract_mock_people(content)
        
        # Calculate importance based on content length and keywords
        importance_score = self._calculate_mock_importance(content)
        
        # Generate summary
        summary = self._generate_mock_summary(content)
        
        # Generate tags
        tags = self._generate_mock_tags(concepts, themes)
        
        return AIAnalysisResult(
            highlight_id=f"{book_id}_{highlight.location.page}_{highlight.location.position}",
            concepts=concepts,
            themes=themes,
            emotions=emotions,
            people=people,
            importance_score=importance_score,
            summary=summary,
            tags=tags
        )
    
    def _extract_mock_concepts(self, content: str) -> List[str]:
        """Extract concepts using simple keyword matching"""
        found_concepts = []
        content_lower = content.lower()
        
        concept_mapping = {
            "权力": "权力意志",
            "支配": "权力意志",
            "控制": "权力意志",
            "死亡": "死亡恐惧",
            "生命": "存在焦虑",
            "存在": "存在焦虑",
            "爱情": "爱情哲学",
            "欲望": "爱情哲学",
            "婚姻": "婚姻自由",
            "自由": "婚姻自由",
            "选择": "选择责任",
            "责任": "选择责任",
            "孤独": "孤独连接",
            "连接": "孤独连接",
            "宗教": "宗教信仰",
            "信仰": "宗教信仰",
            "神": "宗教信仰",
            "上帝": "宗教信仰",
            "无神": "无神论",
            "心理": "精神分析",
            "精神": "精神分析",
            "意识": "意识觉醒",
            "意义": "意义建构"
        }
        
        for keyword, concept in concept_mapping.items():
            if keyword in content_lower:
                found_concepts.append(concept)
        
        # Add some random concepts for variety
        additional_concepts = random.sample(
            [c for c in self.concepts_database if c not in found_concepts],
            min(2, len(self.concepts_database) - len(found_concepts))
        )
        found_concepts.extend(additional_concepts)
        
        return list(set(found_concepts))[:5]  # Return up to 5 concepts
    
    def _extract_mock_themes(self, content: str) -> List[str]:
        """Extract themes using simple keyword matching"""
        found_themes = []
        content_lower = content.lower()
        
        theme_mapping = {
            "哲学": "哲学思辨",
            "心理": "心理学",
            "治疗": "心理学",
            "关系": "人际关系",
            "自我": "自我认知",
            "认知": "自我认知",
            "情感": "情感分析",
            "生死": "生死观",
            "价值": "价值观",
            "道德": "道德伦理",
            "宗教": "宗教哲学",
            "存在": "存在主义"
        }
        
        for keyword, theme in theme_mapping.items():
            if keyword in content_lower:
                found_themes.append(theme)
        
        # Add random themes
        additional_themes = random.sample(
            [t for t in self.themes_database if t not in found_themes],
            min(1, len(self.themes_database) - len(found_themes))
        )
        found_themes.extend(additional_themes)
        
        return list(set(found_themes))[:3]  # Return up to 3 themes
    
    def _extract_mock_emotions(self, content: str) -> List[str]:
        """Extract emotions using simple keyword matching"""
        found_emotions = []
        content_lower = content.lower()
        
        emotion_mapping = {
            "焦虑": "焦虑",
            "紧张": "焦虑",
            "困惑": "困惑",
            "疑问": "困惑",
            "痛苦": "痛苦",
            "难过": "痛苦",
            "愤怒": "愤怒",
            "生气": "愤怒",
            "恐惧": "恐惧",
            "害怕": "恐惧",
            "希望": "希望",
            "期望": "希望",
            "平静": "平静",
            "安静": "平静",
            "悲伤": "悲伤",
            "伤心": "悲伤",
            "孤独": "孤独",
            "寂寞": "孤独",
            "渴望": "渴望",
            "向往": "渴望",
            "满足": "满足",
            "幸福": "满足",
            "挣扎": "挣扎",
            "矛盾": "挣扎"
        }
        
        for keyword, emotion in emotion_mapping.items():
            if keyword in content_lower:
                found_emotions.append(emotion)
        
        return list(set(found_emotions))[:3]  # Return up to 3 emotions
    
    def _extract_mock_people(self, content: str) -> List[str]:
        """Extract people mentioned in content"""
        found_people = []
        content_lower = content.lower()
        
        people_mapping = {
            "尼采": "尼采",
            "布雷尔": "布雷尔",
            "弗洛伊德": "弗洛伊德",
            "贝莎": "贝莎",
            "亚隆": "欧文·亚隆",
            "叔本华": "叔本华",
            "瓦格纳": "瓦格纳",
            "莎乐美": "莎乐美",
            "耶稣": "耶稣",
            "上帝": "上帝"
        }
        
        for keyword, person in people_mapping.items():
            if keyword in content_lower:
                found_people.append(person)
        
        return list(set(found_people))
    
    def _calculate_mock_importance(self, content: str) -> float:
        """Calculate importance score based on content"""
        # Base score on length
        length_score = min(len(content) / 200, 1.0) * 0.3
        
        # Score on philosophical keywords
        keywords = ["哲学", "心理", "存在", "生命", "死亡", "爱情", "自由", "选择", "责任", "意义"]
        keyword_score = sum(1 for keyword in keywords if keyword in content) / len(keywords) * 0.4
        
        # Score on punctuation (questions, exclamations indicate important content)
        punctuation_score = (content.count("?") + content.count("!")) / max(len(content), 1) * 0.3
        
        total_score = length_score + keyword_score + punctuation_score
        return min(max(total_score, 0.1), 1.0)  # Clamp between 0.1 and 1.0
    
    def _generate_mock_summary(self, content: str) -> str:
        """Generate a summary of the content"""
        if len(content) <= 100:
            return content
        
        # Simple extractive summary - take first and last sentences
        sentences = content.split("。")
        if len(sentences) >= 2:
            return sentences[0] + "。" + sentences[-1] + "。"
        else:
            return content[:100] + "..."
    
    def _generate_mock_tags(self, concepts: List[str], themes: List[str]) -> List[str]:
        """Generate tags based on concepts and themes"""
        tags = []
        
        # Add concept tags
        for concept in concepts:
            tags.append(f"#{concept}")
        
        # Add theme tags
        for theme in themes:
            tags.append(f"#{theme}")
        
        return tags
    
    def _real_ai_analyze_highlight(self, highlight: Highlight, book_id: str) -> AIAnalysisResult:
        """Real AI analysis using LLM service"""
        content = highlight.content
        
        try:
            # Extract concepts using LLM
            concepts = self._extract_llm_concepts(content)
            
            # Extract themes using LLM
            themes = self._extract_llm_themes(content)
            
            # Extract emotions using LLM
            emotions = self._extract_llm_emotions(content)
            
            # Extract people using LLM
            people = self._extract_llm_people(content)
            
            # Calculate importance using LLM
            importance_score = self._calculate_llm_importance(content)
            
            # Generate summary using LLM
            summary = self._generate_llm_summary(content)
            
            # Generate tags
            tags = self._generate_llm_tags(concepts, themes)
            
            return AIAnalysisResult(
                highlight_id=f"{book_id}_{highlight.location.page}_{highlight.location.position}",
                concepts=concepts,
                themes=themes,
                emotions=emotions,
                people=people,
                importance_score=importance_score,
                summary=summary,
                tags=tags
            )
            
        except Exception as e:
            self.logger.error(f"LLM analysis failed: {e}")
            # Fallback to mock analysis
            return self._mock_analyze_highlight(highlight, book_id)
    
    def _extract_llm_concepts(self, content: str) -> List[str]:
        """Extract concepts using LLM"""
        prompt = f"""
请从以下文本中提取核心概念和关键词，返回JSON格式的列表。

文本内容：
{content}

要求：
1. 提取最重要的5个核心概念
2. 概念应该简洁明了，通常为2-4个字
3. 返回格式：["概念1", "概念2", "概念3", "概念4", "概念5"]
4. 只返回JSON格式，不要其他解释
"""
        
        try:
            response = self.llm_service.generate_text(prompt)
            # Parse JSON response
            concepts = json.loads(response)
            return concepts[:5]  # Limit to 5 concepts
        except Exception as e:
            self.logger.warning(f"Concept extraction failed: {e}")
            return self._extract_mock_concepts(content)
    
    def _extract_llm_themes(self, content: str) -> List[str]:
        """Extract themes using LLM"""
        prompt = f"""
请从以下文本中识别主要主题，返回JSON格式的列表。

文本内容：
{content}

要求：
1. 识别最重要的3个主题
2. 主题应该概括文本的主要内容领域
3. 返回格式：["主题1", "主题2", "主题3"]
4. 只返回JSON格式，不要其他解释
"""
        
        try:
            response = self.llm_service.generate_text(prompt)
            themes = json.loads(response)
            return themes[:3]  # Limit to 3 themes
        except Exception as e:
            self.logger.warning(f"Theme extraction failed: {e}")
            return self._extract_mock_themes(content)
    
    def _extract_llm_emotions(self, content: str) -> List[str]:
        """Extract emotions using LLM"""
        prompt = f"""
请从以下文本中识别情感色彩，返回JSON格式的列表。

文本内容：
{content}

要求：
1. 识别文本中表达的主要情感
2. 最多识别3种情感
3. 返回格式：["情感1", "情感2", "情感3"]
4. 只返回JSON格式，不要其他解释
"""
        
        try:
            response = self.llm_service.generate_text(prompt)
            emotions = json.loads(response)
            return emotions[:3]  # Limit to 3 emotions
        except Exception as e:
            self.logger.warning(f"Emotion extraction failed: {e}")
            return self._extract_mock_emotions(content)
    
    def _extract_llm_people(self, content: str) -> List[str]:
        """Extract people using LLM"""
        prompt = f"""
请从以下文本中识别提到的人物，返回JSON格式的列表。

文本内容：
{content}

要求：
1. 识别文本中提到的所有人名
2. 包括真实人物和虚构人物
3. 返回格式：["人物1", "人物2", "人物3"]
4. 只返回JSON格式，不要其他解释
"""
        
        try:
            response = self.llm_service.generate_text(prompt)
            people = json.loads(response)
            return people
        except Exception as e:
            self.logger.warning(f"People extraction failed: {e}")
            return self._extract_mock_people(content)
    
    def _calculate_llm_importance(self, content: str) -> float:
        """Calculate importance score using LLM"""
        prompt = f"""
请评估以下文本的重要性，返回0.1到1.0之间的分数。

文本内容：
{content}

要求：
1. 0.1表示不重要，1.0表示非常重要
2. 考虑内容的深度、独特性和启发性
3. 返回格式：0.XX（只返回数字）
4. 只返回数字，不要其他解释
"""
        
        try:
            response = self.llm_service.generate_text(prompt)
            score = float(response.strip())
            return max(0.1, min(1.0, score))  # Clamp between 0.1 and 1.0
        except Exception as e:
            self.logger.warning(f"Importance calculation failed: {e}")
            return self._calculate_mock_importance(content)
    
    def _generate_llm_summary(self, content: str) -> str:
        """Generate summary using LLM"""
        prompt = f"""
请为以下文本生成简洁的总结。

文本内容：
{content}

要求：
1. 总结应该简洁明了，不超过100字
2. 抓住文本的核心观点
3. 保持原文的风格和语气
4. 只返回总结内容，不要其他解释
"""
        
        try:
            response = self.llm_service.generate_text(prompt)
            return response.strip()
        except Exception as e:
            self.logger.warning(f"Summary generation failed: {e}")
            return self._generate_mock_summary(content)
    
    def _generate_llm_tags(self, concepts: List[str], themes: List[str]) -> List[str]:
        """Generate tags using LLM"""
        tags = []
        
        # Add concept tags
        for concept in concepts:
            tags.append(f"#{concept}")
        
        # Add theme tags
        for theme in themes:
            tags.append(f"#{theme}")
        
        return tags
    
    def build_knowledge_graph(self, book: Book, analysis_results: List[AIAnalysisResult]) -> KnowledgeGraph:
        """Build knowledge graph from analysis results"""
        nodes = []
        edges = []
        
        # Add book node
        book_node = KnowledgeNode(
            id=f"book_{book.metadata.title}",
            label=book.metadata.title,
            type="book",
            description=f"《{book.metadata.title}》 - {book.metadata.author}",
            book_id=book.metadata.title
        )
        nodes.append(book_node)
        
        # Process each analysis result
        for result in analysis_results:
            # Add concept nodes
            for concept in result.concepts:
                concept_id = f"concept_{concept}"
                if not any(node.id == concept_id for node in nodes):
                    concept_node = KnowledgeNode(
                        id=concept_id,
                        label=concept,
                        type="concept",
                        description=f"概念：{concept}",
                        book_id=book.metadata.title
                    )
                    nodes.append(concept_node)
                
                # Connect book to concept
                edge = KnowledgeEdge(
                    source=book_node.id,
                    target=concept_id,
                    relationship="contains",
                    weight=1.0
                )
                edges.append(edge)
            
            # Add theme nodes
            for theme in result.themes:
                theme_id = f"theme_{theme}"
                if not any(node.id == theme_id for node in nodes):
                    theme_node = KnowledgeNode(
                        id=theme_id,
                        label=theme,
                        type="theme",
                        description=f"主题：{theme}",
                        book_id=book.metadata.title
                    )
                    nodes.append(theme_node)
                
                # Connect book to theme
                edge = KnowledgeEdge(
                    source=book_node.id,
                    target=theme_id,
                    relationship="explores",
                    weight=1.0
                )
                edges.append(edge)
            
            # Add people nodes
            for person in result.people:
                person_id = f"person_{person}"
                if not any(node.id == person_id for node in nodes):
                    person_node = KnowledgeNode(
                        id=person_id,
                        label=person,
                        type="person",
                        description=f"人物：{person}",
                        book_id=book.metadata.title
                    )
                    nodes.append(person_node)
                
                # Connect book to person
                edge = KnowledgeEdge(
                    source=book_node.id,
                    target=person_id,
                    relationship="mentions",
                    weight=1.0
                )
                edges.append(edge)
        
        # Add inter-concept relationships
        for i, result1 in enumerate(analysis_results):
            for result2 in analysis_results[i+1:]:
                # Find common concepts
                common_concepts = set(result1.concepts) & set(result2.concepts)
                if common_concepts:
                    for concept in common_concepts:
                        edge = KnowledgeEdge(
                            source=result1.highlight_id,
                            target=result2.highlight_id,
                            relationship="shares_concept",
                            weight=len(common_concepts) / max(len(result1.concepts), len(result2.concepts))
                        )
                        edges.append(edge)
        
        return KnowledgeGraph(nodes=nodes, edges=edges)
    
    def analyze_book(self, book: Book) -> Dict[str, Any]:
        """Analyze entire book and return comprehensive results"""
        analysis_results = []
        
        # Analyze each highlight
        for highlight in book.highlights:
            result = self.analyze_highlight(highlight, book.metadata.title)
            analysis_results.append(result)
        
        # Build knowledge graph
        knowledge_graph = self.build_knowledge_graph(book, analysis_results)
        
        # Generate book summary
        book_summary = self._generate_book_summary(book, analysis_results)
        
        return {
            "book": book.to_dict(),
            "analysis_results": [result.to_dict() for result in analysis_results],
            "knowledge_graph": knowledge_graph.to_dict(),
            "book_summary": book_summary,
            "statistics": self._generate_statistics(book, analysis_results)
        }
    
    def _generate_book_summary(self, book: Book, analysis_results: List[AIAnalysisResult]) -> str:
        """Generate a summary of the book analysis"""
        total_highlights = len(analysis_results)
        avg_importance = sum(r.importance_score for r in analysis_results) / total_highlights if total_highlights > 0 else 0
        
        all_concepts = []
        all_themes = []
        all_people = []
        
        for result in analysis_results:
            all_concepts.extend(result.concepts)
            all_themes.extend(result.themes)
            all_people.extend(result.people)
        
        unique_concepts = len(set(all_concepts))
        unique_themes = len(set(all_themes))
        unique_people = len(set(all_people))
        
        summary = f"""
《{book.metadata.title}》阅读分析报告：
- 总标注数：{total_highlights}
- 平均重要性：{avg_importance:.2f}
- 核心概念数：{unique_concepts}
- 主要主题数：{unique_themes}
- 涉及人物数：{unique_people}

主要概念：{', '.join(list(set(all_concepts))[:5])}
主要主题：{', '.join(list(set(all_themes))[:3])}
        """.strip()
        
        return summary
    
    def _generate_statistics(self, book: Book, analysis_results: List[AIAnalysisResult]) -> Dict[str, Any]:
        """Generate statistics for the book analysis"""
        if not analysis_results:
            return {}
        
        # Count by highlight type
        type_counts = {}
        for highlight in book.highlights:
            h_type = highlight.highlight_type.value
            type_counts[h_type] = type_counts.get(h_type, 0) + 1
        
        # Count by section
        section_counts = {}
        for highlight in book.highlights:
            section = highlight.section or "Unknown"
            section_counts[section] = section_counts.get(section, 0) + 1
        
        # Concept frequency
        concept_freq = {}
        for result in analysis_results:
            for concept in result.concepts:
                concept_freq[concept] = concept_freq.get(concept, 0) + 1
        
        # Theme frequency
        theme_freq = {}
        for result in analysis_results:
            for theme in result.themes:
                theme_freq[theme] = theme_freq.get(theme, 0) + 1
        
        # Sort by frequency
        top_concepts = sorted(concept_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        top_themes = sorted(theme_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_highlights": len(analysis_results),
            "type_distribution": type_counts,
            "section_distribution": section_counts,
            "top_concepts": top_concepts,
            "top_themes": top_themes,
            "average_importance": sum(r.importance_score for r in analysis_results) / len(analysis_results),
            "importance_distribution": {
                "high": len([r for r in analysis_results if r.importance_score > 0.7]),
                "medium": len([r for r in analysis_results if 0.3 <= r.importance_score <= 0.7]),
                "low": len([r for r in analysis_results if r.importance_score < 0.3])
            }
        }