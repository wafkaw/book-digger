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
        """Real AI analysis using LLM service with single comprehensive call"""
        content = highlight.content
        
        try:
            # Use single comprehensive analysis instead of 6 separate calls
            analysis_result = self._comprehensive_llm_analysis(content)
            
            # Apply intelligent filtering
            filtered_concepts = self._filter_concepts(analysis_result.get('concepts', []))
            filtered_themes = self._filter_themes(analysis_result.get('themes', []))
            filtered_emotions = self._filter_emotions(analysis_result.get('emotions', []))
            
            return AIAnalysisResult(
                highlight_id=f"{book_id}_{highlight.location.page}_{highlight.location.position}",
                concepts=filtered_concepts[:5],  # Limit to 5 concepts after filtering
                themes=filtered_themes[:3],     # Limit to 3 themes after filtering
                emotions=filtered_emotions[:3], # Limit to 3 emotions after filtering
                people=analysis_result.get('people', []),
                importance_score=analysis_result.get('importance_score', 0.5),
                summary=analysis_result.get('summary', content[:100]),
                tags=self._generate_llm_tags(filtered_concepts, filtered_themes)
            )
            
        except Exception as e:
            self.logger.error(f"LLM analysis failed: {e}")
            # Fallback to mock analysis
            return self._mock_analyze_highlight(highlight, book_id)
    
    def _comprehensive_llm_analysis(self, content: str) -> Dict[str, Any]:
        """Comprehensive analysis using single LLM call with improved prompts"""
        prompt = f"""
请对以下文本进行精炼的哲学分析，返回JSON格式的结果。注重质量而非数量。

文本内容：
{content}

严格要求：
1. 核心概念（2-4个）：
   - 必须是深层哲学概念，如"存在焦虑"、"死亡意识"、"自我超越"
   - 禁止简单词汇："然而"、"此刻"、"时间"、"选择"等
   - 禁止过于宽泛的词："生活"、"人生"、"思考"
   - 优选复合概念："权力意志"、"永劫回归"、"超人理论"

2. 主题分类（1-2个）：
   - 必须是学术领域："存在主义哲学"、"精神分析学"、"伦理哲学"
   - 避免模糊分类："人际关系"、"个人成长"、"生活感悟"

3. 核心情感（1-2个）：
   - 深层情感状态："存在焦虑"、"虚无感"、"超越渴望"
   - 避免表面情感："开心"、"难过"、"生气"

4. 人物（仅明确提及的）：完整人名，如"弗里德里希·尼采"

5. 重要性评分（0.1-1.0）：基于哲学深度、思想独特性、启发价值

6. 精炼总结（15字以内）：抓住最核心的哲学洞察

返回格式：
{{
  "concepts": ["存在焦虑", "自我超越"],
  "themes": ["存在主义哲学"],
  "emotions": ["虚无感"],
  "people": ["尼采"],
  "importance_score": 0.8,
  "summary": "探讨个体面对虚无时的超越路径"
}}

只返回JSON，无其他文字。
"""
        
        try:
            response = self.llm_service.generate_text(prompt)
            # Parse JSON response
            result = json.loads(response)
            return result
        except Exception as e:
            self.logger.warning(f"Comprehensive analysis failed: {e}")
            # Return fallback result
            return {
                "concepts": self._extract_mock_concepts(content)[:3],
                "themes": self._extract_mock_themes(content)[:2],
                "emotions": self._extract_mock_emotions(content)[:2],
                "people": self._extract_mock_people(content),
                "importance_score": self._calculate_mock_importance(content),
                "summary": self._generate_mock_summary(content)
            }
    
    
    
    
    
    
    def _batch_analyze_highlights(self, highlights: List[Highlight], book_id: str) -> List[AIAnalysisResult]:
        """Batch analyze multiple highlights in single API call"""
        if self.mock_mode:
            # Use individual analysis for mock mode
            return [self.analyze_highlight(highlight, book_id) for highlight in highlights]
        
        try:
            # Combine all highlight contents
            batch_content = "\n\n===标注分隔===\n\n".join([h.content for h in highlights])
            
            # Use comprehensive batch analysis
            batch_results = self._comprehensive_batch_analysis(batch_content, len(highlights))
            
            # Create individual results
            analysis_results = []
            for i, highlight in enumerate(highlights):
                result_data = batch_results.get(f'highlight_{i}', {})
                
                # Apply intelligent filtering to batch results
                filtered_concepts = self._filter_concepts(result_data.get('concepts', []))
                filtered_themes = self._filter_themes(result_data.get('themes', []))
                filtered_emotions = self._filter_emotions(result_data.get('emotions', []))
                
                result = AIAnalysisResult(
                    highlight_id=f"{book_id}_{highlight.location.page}_{highlight.location.position}",
                    concepts=filtered_concepts[:5],
                    themes=filtered_themes[:3], 
                    emotions=filtered_emotions[:3],
                    people=result_data.get('people', []),
                    importance_score=result_data.get('importance_score', 0.5),
                    summary=result_data.get('summary', highlight.content[:100]),
                    tags=self._generate_llm_tags(filtered_concepts, filtered_themes)
                )
                analysis_results.append(result)
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Batch analysis failed: {e}")
            # Fallback to individual analysis
            return [self.analyze_highlight(highlight, book_id) for highlight in highlights]
    
    def _comprehensive_batch_analysis(self, batch_content: str, num_highlights: int) -> Dict[str, Any]:
        """Comprehensive batch analysis using single LLM call"""
        prompt = f"""请分析以下{num_highlights}个文本段落，返回JSON格式结果。

文本内容：
{batch_content}

请为每个段落提取：
1. concepts: 2-3个核心概念
2. themes: 1-2个主题分类  
3. emotions: 1个情感状态
4. people: 提到的人名
5. importance_score: 重要性分数(0.1-1.0)
6. summary: 简短总结

JSON格式：
{{
  "highlight_0": {{
    "concepts": ["概念1", "概念2"],
    "themes": ["主题1"],
    "emotions": ["情感1"],
    "people": ["人名1"],
    "importance_score": 0.8,
    "summary": "简短总结"
  }},
  "highlight_1": {{
    "concepts": ["概念3", "概念4"],
    "themes": ["主题2"],
    "emotions": ["情感2"],
    "people": [],
    "importance_score": 0.6,
    "summary": "简短总结"
  }}
}}

只返回JSON数据："""
        
        try:
            response = self.llm_service.generate_text(prompt)
            
            # 详细记录LLM响应信息用于调试
            self.logger.info(f"LLM response length: {len(response)} characters")
            self.logger.info(f"LLM response (full): {repr(response)}")
            self.logger.debug(f"LLM response preview: {response[:500]}...")
            
            # Clean the response - remove any non-JSON content
            response = response.strip()
            if not response:
                raise ValueError("LLM returned empty response")
                
            if not response.startswith('{'):
                self.logger.warning(f"Response doesn't start with '{{', trying to extract JSON...")
                # Try to find JSON in the response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    response = json_match.group(0)
                    self.logger.info(f"Extracted JSON from response: {response[:200]}...")
                else:
                    raise ValueError("No JSON found in response")
            
            result = json.loads(response)
            self.logger.info(f"Successfully parsed JSON with {len(result)} highlights")
            return result
            
        except Exception as e:
            self.logger.error(f"Batch comprehensive analysis failed: {e}")
            if 'response' in locals():
                self.logger.error(f"Complete failed response: {repr(response)}")
                self.logger.error(f"Response type: {type(response)}")
                self.logger.error(f"Response length: {len(response) if response else 'None'}")
            else:
                self.logger.error("No response received from LLM service")
                
            # Return basic fallback structure with minimal analysis
            self.logger.info(f"Returning fallback analysis for {num_highlights} highlights")
            fallback_results = {}
            for i in range(num_highlights):
                fallback_results[f'highlight_{i}'] = {
                    "concepts": ["哲学思考", "个人感悟"],
                    "themes": ["人生哲学"],
                    "emotions": ["思考"],
                    "people": [],
                    "importance_score": 0.5,
                    "summary": "重要思考片段"
                }
            return fallback_results
    
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
    
    def _filter_concepts(self, concepts: List[str]) -> List[str]:
        """Filter out low-value concepts"""
        # Define forbidden concepts (too simple or common)
        forbidden_concepts = {
            '然而', '此刻', '时间', '选择', '思考', '生活', '人生', '世界', '生命',
            '自己', '我们', '他们', '这个', '那个', '现在', '过去', '未来',
            '好的', '不好', '重要', '一般', '普通', '简单', '复杂', '问题',
            '答案', '方法', '方式', '内容', '事情', '东西', '情况', '状态',
            '过程', '结果', '原因', '条件', '环境', '背景', '历史', '文化'
        }
        
        # Define too-short concepts (configurable minimum length)
        from ..config.settings import Config
        min_concept_length = Config.AI_MIN_CONCEPT_LENGTH
        
        filtered = []
        for concept in concepts:
            concept = concept.strip()
            # Skip if forbidden, too short, or too generic
            if (concept not in forbidden_concepts and 
                len(concept) >= min_concept_length and
                not self._is_too_generic(concept)):
                filtered.append(concept)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_filtered = []
        for concept in filtered:
            if concept not in seen:
                seen.add(concept)
                unique_filtered.append(concept)
        
        return unique_filtered
    
    def _filter_themes(self, themes: List[str]) -> List[str]:
        """Filter out low-value themes"""
        # Define forbidden themes (too vague or non-academic)
        forbidden_themes = {
            '生活感悟', '个人成长', '人生体验', '日常思考', '一般讨论',
            '普通话题', '简单分析', '基础理解', '常见观点', '流行思想',
            '大众文化', '通俗理论', '生活哲学', '人际关系', '情感交流',
            '个人感受', '主观体验', '直觉判断', '常识理解', '表面现象'
        }
        
        # Define preferred academic themes
        academic_keywords = {
            '哲学', '心理学', '伦理学', '形而上学', '认识论', '本体论',
            '存在主义', '现象学', '分析哲学', '实用主义', '后现代主义',
            '精神分析', '行为主义', '认知科学', '社会学', '政治哲学'
        }
        
        filtered = []
        for theme in themes:
            theme = theme.strip()
            # Skip forbidden themes
            if theme not in forbidden_themes:
                # Prefer themes with academic keywords
                is_academic = any(keyword in theme for keyword in academic_keywords)
                if is_academic or len(theme) >= 4:  # Accept longer themes even if not explicitly academic
                    filtered.append(theme)
        
        # Remove duplicates
        return list(dict.fromkeys(filtered))
    
    def _filter_emotions(self, emotions: List[str]) -> List[str]:
        """Filter out low-value emotions"""
        # Define forbidden emotions (too simple or common)
        forbidden_emotions = {
            '开心', '难过', '生气', '高兴', '愤怒', '快乐', '悲伤',
            '普通', '一般', '正常', '平常', '简单', '复杂', '好奇',
            '疑惑', '不解', '明白', '理解', '知道', '感觉', '觉得'
        }
        
        # Define preferred deep emotions
        deep_emotions = {
            '存在焦虑', '虚无感', '超越渴望', '道德困顿', '精神痛苦',
            '哲学惊异', '形而上学恐惧', '本体论焦虑', '死亡焦虑',
            '自由恐惧', '选择焦虑', '责任重负', '孤独感', '异化感'
        }
        
        filtered = []
        for emotion in emotions:
            emotion = emotion.strip()
            # Prefer deep emotions or skip forbidden ones
            if emotion in deep_emotions or (emotion not in forbidden_emotions and len(emotion) >= 2):
                filtered.append(emotion)
        
        # Remove duplicates
        return list(dict.fromkeys(filtered))
    
    def _is_too_generic(self, concept: str) -> bool:
        """Check if concept is too generic"""
        generic_patterns = {
            '的', '了', '是', '有', '在', '和', '与', '或', '但', '而',
            '所以', '因为', '如果', '虽然', '不过', '可是', '只是', '就是',
            '什么', '怎么', '为什么', '哪里', '谁', '多少', '几个'
        }
        return concept in generic_patterns or len(concept) <= 1
    
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
    
    def analyze_book(self, book: Book, batch_size: int = 5) -> Dict[str, Any]:
        """Analyze entire book using batch processing for better performance"""
        analysis_results = []
        
        # Process highlights in batches
        highlights = book.highlights
        for i in range(0, len(highlights), batch_size):
            batch = highlights[i:i+batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1}/{(len(highlights) + batch_size - 1)//batch_size} with {len(batch)} highlights")
            
            # Batch process highlights
            batch_results = self._batch_analyze_highlights(batch, book.metadata.title)
            analysis_results.extend(batch_results)
        
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