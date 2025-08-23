"""
图谱API端点
提供知识图谱可视化相关的API接口
"""

import os
import zipfile
import tempfile
from urllib.parse import quote
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse

from app.services.graph_service import GraphService
from app.models.schemas import ApiResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# 初始化图谱服务
graph_service = GraphService()


@router.get("/tasks/{task_id}/graph", summary="获取任务的知识图谱数据")
async def get_task_graph(task_id: str) -> JSONResponse:
    """获取指定任务的知识图谱数据，用于Cytoscape.js渲染"""
    try:
        # 获取图谱数据
        graph_data = graph_service.get_graph_data(task_id)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "获取图谱数据成功",
                "data": graph_data
            }
        )
        
    except Exception as e:
        logger.error(f"获取图谱数据失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取图谱数据失败: {str(e)}"
        )


@router.get("/search", summary="搜索图谱节点")
async def search_graph_nodes(
    q: str = Query(..., description="搜索关键词"),
    type: Optional[str] = Query(None, description="节点类型过滤 (concept/theme/person)"),
    limit: int = Query(20, description="返回结果数量限制")
) -> JSONResponse:
    """搜索图谱中的节点"""
    try:
        # 搜索节点
        results = graph_service.search_nodes(query=q, node_type=type)
        
        # 限制返回数量
        if limit and len(results) > limit:
            results = results[:limit]
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"找到 {len(results)} 个匹配的节点",
                "data": {
                    "query": q,
                    "type": type,
                    "results": results,
                    "total": len(results)
                }
            }
        )
        
    except Exception as e:
        logger.error(f"搜索节点失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"搜索失败: {str(e)}"
        )


@router.get("/nodes/{node_id}/neighbors", summary="获取节点邻居")
async def get_node_neighbors(node_id: str) -> JSONResponse:
    """获取指定节点及其邻居的子图数据"""
    try:
        # 获取邻居节点数据
        subgraph_data = graph_service.get_node_neighbors(node_id)
        
        if not subgraph_data["elements"]["nodes"]:
            raise HTTPException(
                status_code=404,
                detail=f"节点 '{node_id}' 未找到"
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"获取节点 '{node_id}' 的邻居数据成功",
                "data": {
                    "nodeId": node_id,
                    "subgraph": subgraph_data,
                    "neighborCount": len(subgraph_data["elements"]["nodes"]) - 1  # 减去中心节点
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取邻居节点失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取邻居节点失败: {str(e)}"
        )


@router.get("/stats", summary="获取图谱统计信息")
async def get_graph_stats() -> JSONResponse:
    """获取知识图谱的统计信息"""
    try:
        # 获取完整图谱数据
        graph_data = graph_service.get_graph_data("")
        nodes = graph_data["elements"]["nodes"]
        edges = graph_data["elements"]["edges"]
        
        # 统计不同类型的节点数量
        stats = {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "node_types": {},
            "edge_types": {},
            "average_connections": 0
        }
        
        # 统计节点类型
        for node in nodes:
            node_type = node["data"].get("type", "unknown")
            stats["node_types"][node_type] = stats["node_types"].get(node_type, 0) + 1
        
        # 统计边类型
        for edge in edges:
            edge_type = edge["data"].get("type", "unknown")
            stats["edge_types"][edge_type] = stats["edge_types"].get(edge_type, 0) + 1
        
        # 计算平均连接数
        if len(nodes) > 0:
            stats["average_connections"] = round(len(edges) * 2 / len(nodes), 2)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "获取图谱统计信息成功",
                "data": stats
            }
        )
        
    except Exception as e:
        logger.error(f"获取图谱统计信息失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取统计信息失败: {str(e)}"
        )


@router.get("/export/{task_id}", summary="导出图谱数据")
async def export_graph_data(
    task_id: str,
    format: str = Query("json", description="导出格式 (json/graphml/gexf/obsidian)")
) -> JSONResponse:
    """导出图谱数据为指定格式"""
    try:
        if format not in ["json", "graphml", "gexf", "obsidian"]:
            raise HTTPException(
                status_code=400,
                detail="不支持的导出格式，支持的格式: json, graphml, gexf, obsidian"
            )
        
        # 获取图谱数据
        graph_data = graph_service.get_graph_data(task_id)
        
        if format == "obsidian":
            # 生成 Obsidian vault ZIP文件
            return await _export_obsidian_vault(task_id, graph_service)
        else:
            # 获取原始文件名用于JSON导出
            original_filename = _get_original_filename(task_id)
            json_filename = f"{original_filename}_脑图.{format}"
            # URL编码中文文件名
            encoded_json_filename = quote(json_filename.encode('utf-8'))
            
            # 返回JSON格式或其他格式
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": f"导出图谱数据成功 (格式: {format})",
                    "data": {
                        "format": format,
                        "taskId": task_id,
                        "originalFilename": original_filename,
                        "graphData": graph_data,
                        "exportTime": "2025-08-21T10:00:00Z"
                    }
                },
                headers={
                    "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_json_filename}"
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出图谱数据失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"导出失败: {str(e)}"
        )


async def _export_obsidian_vault(task_id: str, graph_service: GraphService) -> FileResponse:
    """生成并导出 Obsidian vault ZIP文件"""
    try:
        # 获取任务对应的 Obsidian vault 路径
        vault_path = graph_service._get_task_vault_path(task_id)
        
        if not os.path.exists(vault_path):
            raise HTTPException(
                status_code=404,
                detail=f"任务 {task_id} 的 Obsidian vault 不存在"
            )
        
        # 获取原始文件名
        original_filename = _get_original_filename(task_id)
        
        # 创建临时ZIP文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        temp_file.close()
        
        try:
            # 创建ZIP压缩包
            with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 遍历vault目录中的所有文件
                for root, dirs, files in os.walk(vault_path):
                    for file in files:
                        if file.endswith('.md'):  # 只包含markdown文件
                            file_path = os.path.join(root, file)
                            # 计算相对路径
                            arcname = os.path.relpath(file_path, vault_path)
                            zipf.write(file_path, arcname)
            
            logger.info(f"成功创建 Obsidian vault ZIP文件: {temp_file.name}")
            
            # 生成文件名
            filename = f"{original_filename}_脑图.zip"
            # URL编码中文文件名
            encoded_filename = quote(filename.encode('utf-8'))
            
            # 返回文件响应
            return FileResponse(
                path=temp_file.name,
                filename=filename,
                media_type="application/zip",
                headers={
                    "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
                }
            )
            
        except Exception as e:
            # 清理临时文件
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            raise e
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成 Obsidian vault 失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"生成 Obsidian vault 失败: {str(e)}"
        )


def _get_original_filename(task_id: str) -> str:
    """获取任务关联的原始文件名（去掉扩展名）"""
    try:
        from app.models.database import SessionLocal
        from app.models.models import Task, UploadedFile
        
        db = SessionLocal()
        
        # 查询任务和关联的文件信息
        task = db.query(Task).filter(Task.id == task_id).first()
        if task and task.file:
            original_filename = task.file.original_filename
            # 去掉文件扩展名
            if '.' in original_filename:
                filename_without_ext = '.'.join(original_filename.split('.')[:-1])
            else:
                filename_without_ext = original_filename
            
            db.close()
            return filename_without_ext
        
        db.close()
        logger.warning(f"无法找到任务 {task_id} 的原始文件名，使用默认名称")
        return f"knowledge_graph_{task_id}"
        
    except Exception as e:
        logger.error(f"获取原始文件名失败: {str(e)}")
        return f"knowledge_graph_{task_id}"