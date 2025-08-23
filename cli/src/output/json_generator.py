"""
JSON格式输出生成器
将分析结果转换为结构化的JSON格式
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
from datetime import datetime

class JSONGenerator:
    """JSON格式输出生成器"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        
    def generate_json_from_obsidian(self, obsidian_vault_path: Path, output_file: Path = None) -> Dict[str, Any]:
        """
        从Obsidian vault生成JSON格式的知识图谱
        
        Args:
            obsidian_vault_path: Obsidian vault目录路径
            output_file: 输出JSON文件路径（可选）
            
        Returns:
            包含知识图谱数据的字典
        """
        vault_path = Path(obsidian_vault_path)
        
        if not vault_path.exists():
            raise FileNotFoundError(f"Obsidian vault not found: {vault_path}")
        
        # 构建JSON数据结构
        json_data = {
            "metadata": {
                "generator": "Kindle Reading Assistant",
                "version": "2.0.0",
                "generated_at": datetime.now().isoformat(),
                "source_vault": str(vault_path),
                "format": "json"
            },
            "books": [],
            "concepts": [],
            "themes": [],
            "people": [],
            "relationships": [],
            "statistics": {}
        }
        
        # 解析各个目录
        books_dir = vault_path / "books"
        concepts_dir = vault_path / "concepts" 
        themes_dir = vault_path / "themes"
        people_dir = vault_path / "people"
        
        # 解析书籍信息
        if books_dir.exists():
            json_data["books"] = self._parse_books(books_dir)
            
        # 解析概念
        if concepts_dir.exists():
            json_data["concepts"] = self._parse_concepts(concepts_dir)
            
        # 解析主题
        if themes_dir.exists():
            json_data["themes"] = self._parse_themes(themes_dir)
            
        # 解析人物
        if people_dir.exists():
            json_data["people"] = self._parse_people(people_dir)
            
        # 提取关系
        json_data["relationships"] = self._extract_relationships(json_data)
        
        # 生成统计信息
        json_data["statistics"] = self._generate_statistics(json_data)
        
        # 保存到文件
        if output_file:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        return json_data
    
    def _parse_books(self, books_dir: Path) -> List[Dict[str, Any]]:
        """解析书籍信息"""
        books = []
        
        for book_file in books_dir.glob("*.md"):
            book_data = {
                "title": book_file.stem,
                "file": str(book_file),
                "highlights": [],
                "metadata": {}
            }
            
            content = book_file.read_text(encoding='utf-8')
            
            # 提取元数据
            book_data["metadata"] = self._extract_metadata(content)
            
            # 提取标注
            book_data["highlights"] = self._extract_highlights(content)
            
            books.append(book_data)
        
        return books
    
    def _parse_concepts(self, concepts_dir: Path) -> List[Dict[str, Any]]:
        """解析概念信息"""
        concepts = []
        
        for concept_file in concepts_dir.glob("*.md"):
            concept_data = {
                "name": concept_file.stem,
                "file": str(concept_file),
                "type": "concept",
                "description": "",
                "importance": 0.0,
                "tags": [],
                "links": [],
                "related_highlights": []
            }
            
            content = concept_file.read_text(encoding='utf-8')
            
            # 提取描述（通常是第一段）
            lines = content.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('#') and not line.startswith('**'):
                    concept_data["description"] = line.strip()
                    break
            
            # 提取标签
            concept_data["tags"] = self._extract_tags(content)
            
            # 提取双向链接
            concept_data["links"] = self._extract_wikilinks(content)
            
            # 提取重要性评分（如果有的话）
            concept_data["importance"] = self._extract_importance(content)
            
            concepts.append(concept_data)
        
        return concepts
    
    def _parse_themes(self, themes_dir: Path) -> List[Dict[str, Any]]:
        """解析主题信息"""
        themes = []
        
        for theme_file in themes_dir.glob("*.md"):
            theme_data = {
                "name": theme_file.stem,
                "file": str(theme_file),
                "type": "theme",
                "description": "",
                "concepts": [],
                "tags": []
            }
            
            content = theme_file.read_text(encoding='utf-8')
            
            # 提取描述
            lines = content.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('#') and not line.startswith('**'):
                    theme_data["description"] = line.strip()
                    break
            
            # 提取关联的概念
            theme_data["concepts"] = self._extract_wikilinks(content)
            
            # 提取标签
            theme_data["tags"] = self._extract_tags(content)
            
            themes.append(theme_data)
        
        return themes
    
    def _parse_people(self, people_dir: Path) -> List[Dict[str, Any]]:
        """解析人物信息"""
        people = []
        
        for person_file in people_dir.glob("*.md"):
            person_data = {
                "name": person_file.stem,
                "file": str(person_file),
                "type": "person",
                "description": "",
                "related_concepts": [],
                "role": "",
                "tags": []
            }
            
            content = person_file.read_text(encoding='utf-8')
            
            # 提取描述
            lines = content.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('#') and not line.startswith('**'):
                    person_data["description"] = line.strip()
                    break
            
            # 提取关联概念
            person_data["related_concepts"] = self._extract_wikilinks(content)
            
            # 提取标签
            person_data["tags"] = self._extract_tags(content)
            
            people.append(person_data)
        
        return people
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """从内容中提取元数据"""
        metadata = {}
        
        # 提取YAML front matter（如果有的话）
        if content.startswith('---'):
            yaml_end = content.find('---', 3)
            if yaml_end != -1:
                yaml_content = content[3:yaml_end].strip()
                # 简单的YAML解析（仅支持key: value格式）
                for line in yaml_content.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
        
        return metadata
    
    def _extract_highlights(self, content: str) -> List[str]:
        """从内容中提取标注"""
        highlights = []
        
        # 查找引用块或标注标记
        lines = content.split('\n')
        current_highlight = ""
        
        for line in lines:
            if line.startswith('>'):
                current_highlight += line[1:].strip() + " "
            elif current_highlight:
                highlights.append(current_highlight.strip())
                current_highlight = ""
        
        # 处理最后一个标注
        if current_highlight:
            highlights.append(current_highlight.strip())
        
        return highlights
    
    def _extract_tags(self, content: str) -> List[str]:
        """提取标签"""
        # 查找 #tag 格式的标签
        tag_pattern = r'#([a-zA-Z0-9\u4e00-\u9fff_-]+)'
        tags = re.findall(tag_pattern, content)
        return list(set(tags))  # 去重
    
    def _extract_wikilinks(self, content: str) -> List[str]:
        """提取双向链接"""
        # 查找 [[link]] 格式的链接
        link_pattern = r'\[\[([^\]]+)\]\]'
        links = re.findall(link_pattern, content)
        return list(set(links))  # 去重
    
    def _extract_importance(self, content: str) -> float:
        """提取重要性评分"""
        # 查找重要性标记，如 "重要性: 0.8" 或 "Importance: 0.8"
        importance_pattern = r'(?:重要性|Importance)[:：]\s*([0-9.]+)'
        match = re.search(importance_pattern, content)
        
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        
        # 默认重要性
        return 0.5
    
    def _extract_relationships(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取节点间的关系"""
        relationships = []
        
        # 创建名称到节点类型的映射
        name_to_type = {}
        for concept in json_data["concepts"]:
            name_to_type[concept["name"]] = "concept"
        for theme in json_data["themes"]:
            name_to_type[theme["name"]] = "theme"
        for person in json_data["people"]:
            name_to_type[person["name"]] = "person"
        
        # 从概念的链接中提取关系
        for concept in json_data["concepts"]:
            source = concept["name"]
            for link in concept["links"]:
                if link in name_to_type:
                    relationship = {
                        "source": source,
                        "target": link,
                        "source_type": "concept",
                        "target_type": name_to_type[link],
                        "relation_type": "related_to",
                        "strength": 1.0
                    }
                    relationships.append(relationship)
        
        # 从主题的概念中提取关系
        for theme in json_data["themes"]:
            source = theme["name"]
            for concept in theme["concepts"]:
                if concept in name_to_type:
                    relationship = {
                        "source": source,
                        "target": concept,
                        "source_type": "theme",
                        "target_type": name_to_type[concept],
                        "relation_type": "contains",
                        "strength": 1.0
                    }
                    relationships.append(relationship)
        
        # 从人物的关联概念中提取关系
        for person in json_data["people"]:
            source = person["name"]
            for concept in person["related_concepts"]:
                if concept in name_to_type:
                    relationship = {
                        "source": source,
                        "target": concept,
                        "source_type": "person",
                        "target_type": name_to_type[concept],
                        "relation_type": "associated_with",
                        "strength": 1.0
                    }
                    relationships.append(relationship)
        
        return relationships
    
    def _generate_statistics(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成统计信息"""
        stats = {
            "total_books": len(json_data["books"]),
            "total_concepts": len(json_data["concepts"]),
            "total_themes": len(json_data["themes"]),
            "total_people": len(json_data["people"]),
            "total_relationships": len(json_data["relationships"]),
            "total_nodes": len(json_data["concepts"]) + len(json_data["themes"]) + len(json_data["people"])
        }
        
        # 计算平均重要性
        if json_data["concepts"]:
            avg_importance = sum(concept["importance"] for concept in json_data["concepts"]) / len(json_data["concepts"])
            stats["average_concept_importance"] = round(avg_importance, 2)
        
        # 计算网络密度
        total_nodes = stats["total_nodes"]
        if total_nodes > 1:
            max_relationships = total_nodes * (total_nodes - 1)
            density = stats["total_relationships"] / max_relationships
            stats["network_density"] = round(density, 4)
        
        return stats

def create_json_from_obsidian(vault_path: str, output_file: str = None) -> Dict[str, Any]:
    """
    便捷函数：从Obsidian vault创建JSON输出
    
    Args:
        vault_path: Obsidian vault目录路径
        output_file: 输出JSON文件路径（可选）
        
    Returns:
        包含知识图谱数据的字典
    """
    generator = JSONGenerator(Path(vault_path).parent)
    return generator.generate_json_from_obsidian(Path(vault_path), Path(output_file) if output_file else None)