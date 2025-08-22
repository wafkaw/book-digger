"""
图谱数据服务
处理知识图谱数据的转换和分析
"""

import os
import re
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class GraphService:
    """知识图谱数据处理服务"""
    
    def __init__(self, obsidian_vault_path: str = None):
        """初始化图谱服务
        
        Args:
            obsidian_vault_path: Obsidian vault 文件夹路径
        """
        # 使用绝对路径指向项目中的obsidian数据
        if obsidian_vault_path:
            self.vault_path = obsidian_vault_path
        else:
            # 默认路径指向项目根目录下的obsidian_vault
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(current_dir, "..", "..", "..", "..")
            self.vault_path = os.path.join(project_root, "obsidian_vault")
        
    def get_graph_data(self, task_id: str) -> Dict[str, Any]:
        """获取任务的图谱数据
        
        Args:
            task_id: 任务ID（如果提供，优先使用任务特定的vault路径）
            
        Returns:
            Cytoscape格式的图谱数据
        """
        try:
            # 确定vault路径
            vault_path = self.vault_path
            
            # 如果提供了task_id，尝试使用任务特定的输出目录
            if task_id:
                from app.core.config import settings
                from app.models.database import SessionLocal
                from app.models.models import Task
                
                try:
                    db = SessionLocal()
                    task = db.query(Task).filter(Task.id == task_id).first()
                    if task and task.output_directory:
                        task_vault_path = Path(task.output_directory)
                        if task_vault_path.exists():
                            vault_path = str(task_vault_path)
                            logger.info(f"Using task-specific vault: {vault_path}")
                    db.close()
                except Exception as e:
                    logger.warning(f"Could not load task-specific vault for {task_id}: {e}")
            
            # 解析Obsidian文件
            nodes = []
            edges = []
            
            # 解析书籍节点（如果有）
            books_path = Path(vault_path) / "books"
            if books_path.exists():
                book_nodes = self._parse_books(books_path)
                nodes.extend(book_nodes)
            
            # 解析概念节点
            concepts_path = Path(vault_path) / "concepts"
            if concepts_path.exists():
                concept_nodes, concept_edges = self._parse_concepts(concepts_path)
                nodes.extend(concept_nodes)
                edges.extend(concept_edges)
                
            # 解析主题节点
            themes_path = Path(vault_path) / "themes"
            if themes_path.exists():
                theme_nodes, theme_edges = self._parse_themes(themes_path)
                nodes.extend(theme_nodes)
                edges.extend(theme_edges)
                
            # 解析人物节点
            people_path = Path(vault_path) / "people"
            if people_path.exists():
                people_nodes, people_edges = self._parse_people(people_path)
                nodes.extend(people_nodes)
                edges.extend(people_edges)
            
            # 获取所有存在的节点ID
            node_ids = set(node["data"]["id"] for node in nodes)
            
            # 过滤掉指向不存在节点的边
            valid_edges = []
            invalid_edges = []
            for edge in edges:
                source_id = edge["data"]["source"]
                target_id = edge["data"]["target"]
                if source_id in node_ids and target_id in node_ids:
                    valid_edges.append(edge)
                else:
                    invalid_edges.append(edge)
                    if source_id not in node_ids:
                        logger.warning(f"过滤无效边: 源节点 '{source_id}' 不存在")
                    if target_id not in node_ids:
                        logger.warning(f"过滤无效边: 目标节点 '{target_id}' 不存在")
            
            if invalid_edges:
                logger.info(f"过滤了 {len(invalid_edges)} 条无效边，保留 {len(valid_edges)} 条有效边")
            
            # 构建Cytoscape数据格式
            cytoscape_data = {
                "elements": {
                    "nodes": nodes,
                    "edges": valid_edges
                },
                "layout": {
                    "name": "cose-bilkent",
                    "idealEdgeLength": 50,
                    "nodeOverlap": 10,
                    "refresh": 20,
                    "fit": True,
                    "padding": 30,
                    "randomize": False,
                    "componentSpacing": 40,
                    "nodeRepulsion": 400000,
                    "edgeElasticity": 100,
                    "nestingFactor": 5,
                    "gravity": 80,
                    "numIter": 2500,
                    "tile": True
                },
                "style": self._get_graph_styles()
            }
            
            logger.info(f"生成图谱数据: {len(nodes)} 个节点, {len(valid_edges)} 条边")
            
            return cytoscape_data
            
        except Exception as e:
            logger.error(f"获取图谱数据失败: {str(e)}")
            raise
    
    def _parse_books(self, books_path: Path) -> list:
        """解析书籍文件"""
        nodes = []
        
        for book_file in books_path.glob("*.md"):
            try:
                book_name = book_file.stem
                
                # 创建书籍节点
                node = {
                    "data": {
                        "id": book_name,
                        "label": book_name,
                        "type": "book",
                        "category": "书籍",
                        "importance": 0.8
                    }
                }
                nodes.append(node)
                
            except Exception as e:
                logger.warning(f"解析书籍文件失败 {book_file}: {str(e)}")
                
        return nodes
    
    def _parse_concepts(self, concepts_path: Path) -> tuple:
        """解析概念文件"""
        nodes = []
        edges = []
        
        for concept_file in concepts_path.glob("*.md"):
            try:
                content = concept_file.read_text(encoding='utf-8')
                concept_name = concept_file.stem
                
                # 创建概念节点
                node = {
                    "data": {
                        "id": concept_name,
                        "label": concept_name,
                        "type": "concept",
                        "category": "概念"
                    }
                }
                
                # 提取重要性和其他元数据
                importance_match = re.search(r'重要性:\s*(\d+\.?\d*)', content)
                if importance_match:
                    node["data"]["importance"] = float(importance_match.group(1))
                else:
                    node["data"]["importance"] = 0.5
                    
                # 提取概念类型
                if "#核心概念" in content:
                    node["data"]["conceptType"] = "core"
                elif "#热门概念" in content:
                    node["data"]["conceptType"] = "popular"
                else:
                    node["data"]["conceptType"] = "normal"
                
                nodes.append(node)
                
                # 提取关联概念链接
                concept_links = re.findall(r'\[\[([^\]]+)\]\]\s*\(关联度:\s*(\d+\.?\d*)\)', content)
                for link_name, weight in concept_links:
                    edge = {
                        "data": {
                            "id": f"{concept_name}-{link_name}",
                            "source": concept_name,
                            "target": link_name,
                            "weight": float(weight),
                            "type": "concept-relation"
                        }
                    }
                    edges.append(edge)
                    
                # 提取简单的关联链接（没有权重）
                simple_links = re.findall(r'- \[\[([^\]]+)\]\]', content)
                for link_name in simple_links:
                    if link_name != concept_name:  # 避免自环
                        edge = {
                            "data": {
                                "id": f"{concept_name}-{link_name}-simple",
                                "source": concept_name,
                                "target": link_name,
                                "weight": 0.3,
                                "type": "concept-relation"
                            }
                        }
                        edges.append(edge)
                        
            except Exception as e:
                logger.warning(f"解析概念文件失败 {concept_file}: {str(e)}")
                
        return nodes, edges
    
    def _parse_themes(self, themes_path: Path) -> tuple:
        """解析主题文件"""
        nodes = []
        edges = []
        
        for theme_file in themes_path.glob("*.md"):
            try:
                content = theme_file.read_text(encoding='utf-8')
                theme_name = theme_file.stem
                
                # 创建主题节点
                node = {
                    "data": {
                        "id": theme_name,
                        "label": theme_name,
                        "type": "theme",
                        "category": "主题",
                        "importance": 0.6
                    }
                }
                nodes.append(node)
                
                # 提取关联链接
                links = re.findall(r'\[\[([^\]]+)\]\]', content)
                for link_name in links:
                    if link_name != theme_name:  # 避免自环
                        edge = {
                            "data": {
                                "id": f"{theme_name}-{link_name}",
                                "source": theme_name,
                                "target": link_name,
                                "weight": 0.4,
                                "type": "theme-relation"
                            }
                        }
                        edges.append(edge)
                        
            except Exception as e:
                logger.warning(f"解析主题文件失败 {theme_file}: {str(e)}")
                
        return nodes, edges
    
    def _parse_people(self, people_path: Path) -> tuple:
        """解析人物文件"""
        nodes = []
        edges = []
        
        for people_file in people_path.glob("*.md"):
            try:
                content = people_file.read_text(encoding='utf-8')
                people_name = people_file.stem
                
                # 创建人物节点
                node = {
                    "data": {
                        "id": people_name,
                        "label": people_name,
                        "type": "person",
                        "category": "人物",
                        "importance": 0.7
                    }
                }
                nodes.append(node)
                
                # 提取关联链接
                links = re.findall(r'\[\[([^\]]+)\]\]', content)
                for link_name in links:
                    if link_name != people_name:  # 避免自环
                        edge = {
                            "data": {
                                "id": f"{people_name}-{link_name}",
                                "source": people_name,
                                "target": link_name,
                                "weight": 0.5,
                                "type": "person-relation"
                            }
                        }
                        edges.append(edge)
                        
            except Exception as e:
                logger.warning(f"解析人物文件失败 {people_file}: {str(e)}")
                
        return nodes, edges
    
    def _get_graph_styles(self) -> List[Dict[str, Any]]:
        """获取图谱样式配置"""
        return [
            # 书籍节点样式
            {
                "selector": "node[type='book']",
                "style": {
                    "background-color": "#6366f1",
                    "label": "data(label)",
                    "color": "#ffffff",
                    "text-valign": "center",
                    "text-halign": "center",
                    "font-size": "11px",
                    "font-weight": "500",
                    "width": "60px",
                    "height": "35px",
                    "border-width": "2px",
                    "border-color": "#4f46e5",
                    "shape": "rectangle"
                }
            },
            # 概念节点样式
            {
                "selector": "node[type='concept']",
                "style": {
                    "background-color": "#3b82f6",
                    "label": "data(label)",
                    "color": "#ffffff",
                    "text-valign": "center",
                    "text-halign": "center",
                    "font-size": "12px",
                    "font-weight": "600",
                    "width": "40px",
                    "height": "40px",
                    "border-width": "2px",
                    "border-color": "#1e40af"
                }
            },
            # 核心概念节点样式
            {
                "selector": "node[conceptType='core']",
                "style": {
                    "background-color": "#dc2626",
                    "border-color": "#991b1b",
                    "width": "50px",
                    "height": "50px",
                    "font-size": "14px"
                }
            },
            # 热门概念节点样式
            {
                "selector": "node[conceptType='popular']",
                "style": {
                    "background-color": "#f59e0b",
                    "border-color": "#d97706",
                    "width": "45px",
                    "height": "45px",
                    "font-size": "13px"
                }
            },
            # 主题节点样式
            {
                "selector": "node[type='theme']",
                "style": {
                    "background-color": "#10b981",
                    "label": "data(label)",
                    "color": "#ffffff",
                    "text-valign": "center",
                    "text-halign": "center",
                    "font-size": "11px",
                    "font-weight": "500",
                    "width": "35px",
                    "height": "35px",
                    "border-width": "2px",
                    "border-color": "#059669",
                    "shape": "diamond"
                }
            },
            # 人物节点样式
            {
                "selector": "node[type='person']",
                "style": {
                    "background-color": "#8b5cf6",
                    "label": "data(label)",
                    "color": "#ffffff",
                    "text-valign": "center",
                    "text-halign": "center",
                    "font-size": "11px",
                    "font-weight": "500",
                    "width": "45px",
                    "height": "45px",
                    "border-width": "2px",
                    "border-color": "#7c3aed",
                    "shape": "triangle"
                }
            },
            # 边样式
            {
                "selector": "edge",
                "style": {
                    "width": "mapData(weight, 0, 1, 1, 6)",
                    "line-color": "#e5e7eb",
                    "target-arrow-color": "#9ca3af",
                    "target-arrow-shape": "triangle",
                    "curve-style": "bezier",
                    "opacity": "mapData(weight, 0, 1, 0.3, 0.8)"
                }
            },
            # 概念关系边样式
            {
                "selector": "edge[type='concept-relation']",
                "style": {
                    "line-color": "#3b82f6",
                    "target-arrow-color": "#3b82f6"
                }
            },
            # 主题关系边样式
            {
                "selector": "edge[type='theme-relation']",
                "style": {
                    "line-color": "#10b981",
                    "target-arrow-color": "#10b981"
                }
            },
            # 人物关系边样式
            {
                "selector": "edge[type='person-relation']",
                "style": {
                    "line-color": "#8b5cf6",
                    "target-arrow-color": "#8b5cf6"
                }
            },
            # 选中状态
            {
                "selector": ":selected",
                "style": {
                    "background-blacken": "0.4",
                    "line-color": "#000",
                    "target-arrow-color": "#000",
                    "source-arrow-color": "#000",
                    "opacity": "1"
                }
            },
            # 悬浮状态
            {
                "selector": "node:active",
                "style": {
                    "overlay-color": "#000",
                    "overlay-padding": "10px"
                }
            }
        ]
    
    def search_nodes(self, query: str, node_type: str = None) -> List[Dict[str, Any]]:
        """搜索节点
        
        Args:
            query: 搜索关键词
            node_type: 节点类型过滤 (concept/theme/person)
            
        Returns:
            匹配的节点列表
        """
        try:
            graph_data = self.get_graph_data("")
            nodes = graph_data["elements"]["nodes"]
            
            results = []
            query_lower = query.lower()
            
            for node in nodes:
                node_data = node["data"]
                node_label = node_data.get("label", "").lower()
                
                # 类型过滤
                if node_type and node_data.get("type") != node_type:
                    continue
                    
                # 名称匹配
                if query_lower in node_label:
                    results.append({
                        "id": node_data["id"],
                        "label": node_data["label"],
                        "type": node_data["type"],
                        "category": node_data.get("category", ""),
                        "importance": node_data.get("importance", 0.5)
                    })
            
            # 按重要性排序
            results.sort(key=lambda x: x["importance"], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"搜索节点失败: {str(e)}")
            return []
    
    def get_node_neighbors(self, node_id: str) -> Dict[str, Any]:
        """获取节点的邻居节点
        
        Args:
            node_id: 节点ID
            
        Returns:
            节点及其邻居的子图数据
        """
        try:
            graph_data = self.get_graph_data("")
            all_nodes = {node["data"]["id"]: node for node in graph_data["elements"]["nodes"]}
            all_edges = graph_data["elements"]["edges"]
            
            # 找到目标节点
            if node_id not in all_nodes:
                return {"elements": {"nodes": [], "edges": []}}
            
            target_node = all_nodes[node_id]
            neighbor_nodes = [target_node]
            neighbor_edges = []
            neighbor_ids = {node_id}
            
            # 找到所有连接的边和邻居节点
            for edge in all_edges:
                edge_data = edge["data"]
                source_id = edge_data["source"]
                target_id = edge_data["target"]
                
                if source_id == node_id and target_id in all_nodes:
                    neighbor_nodes.append(all_nodes[target_id])
                    neighbor_edges.append(edge)
                    neighbor_ids.add(target_id)
                elif target_id == node_id and source_id in all_nodes:
                    neighbor_nodes.append(all_nodes[source_id])
                    neighbor_edges.append(edge)
                    neighbor_ids.add(source_id)
            
            # 去重
            unique_nodes = []
            seen_ids = set()
            for node in neighbor_nodes:
                node_id = node["data"]["id"]
                if node_id not in seen_ids:
                    unique_nodes.append(node)
                    seen_ids.add(node_id)
            
            return {
                "elements": {
                    "nodes": unique_nodes,
                    "edges": neighbor_edges
                },
                "layout": graph_data["layout"],
                "style": graph_data["style"]
            }
            
        except Exception as e:
            logger.error(f"获取邻居节点失败: {str(e)}")
            return {"elements": {"nodes": [], "edges": []}}