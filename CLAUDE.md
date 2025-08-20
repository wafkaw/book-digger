# Kindle Reading Assistant - 项目计划与进度

## 项目概述

**项目目标**: 创建一个智能的 Kindle 阅读笔记处理工具，能够自动解析 Kindle 导出的 HTML 格式笔记，使用 AI 进行智能分析，并生成 Obsidian 兼容的知识图谱。

**核心功能**:
- 解析 Kindle HTML 导出文件
- AI 智能分析标注内容
- 构建知识图谱和关联网络
- 生成 Obsidian 兼容的 Markdown 文件

## 详细产品计划

### 1. 技术架构

#### 1.1 核心模块
- **数据采集模块** (`src/data_collection/`): 负责解析 Kindle HTML 文件
- **数据处理模块** (`src/processing/`): 数据清洗和预处理
- **知识图谱模块** (`src/knowledge_graph/`): AI 分析和知识图谱构建
- **关联分析模块** (`src/relation_analysis/`): 概念关联和关系挖掘
- **输出模块** (`src/output/`): 生成 Obsidian 格式文件

#### 1.2 技术栈
- **HTML 解析**: BeautifulSoup4 + lxml
- **AI 分析**: scikit-learn + NLTK + spaCy
- **知识图谱**: NetworkX
- **数据格式**: Python dataclasses + JSON
- **输出格式**: Markdown + Obsidian 双向链接

### 2. 数据模型设计

#### 2.1 核心数据结构
```python
@dataclass
class Book:
    title: str
    author: str
    highlights: List[Highlight]
    metadata: BookMetadata
    
@dataclass
class Highlight:
    content: str
    location: str
    page: int
    chapter: str
    highlight_type: str
    
@dataclass
class AIAnalysisResult:
    concepts: List[Concept]
    themes: List[Theme]
    emotions: List[Emotion]
    people: List[Person]
    knowledge_graph: KnowledgeGraph
```

#### 2.2 知识图谱结构
- **概念节点**: 提取的核心概念和术语
- **人物节点**: 识别的重要人物
- **主题节点**: 主要主题分类
- **关系边**: 概念间的关联关系

### 3. 开发路线图

#### 第一阶段: 基础解析和数据处理
- [x] 分析 Kindle HTML 文档结构
- [x] 实现 HTML 解析器
- [x] 设计数据模型
- [x] 提取书籍元数据和标注内容

#### 第二阶段: LLM智能分析升级 (当前进行中)
- [x] 实现 AI 分析模拟接口 (基础版本)
- [x] 概念提取和分类 (关键词匹配版本)  
- [x] 主题识别和情感分析 (规则版本)
- [x] 知识图谱构建 (基础版本)
- [ ] 🔄 **LLM服务集成**
  - [ ] OpenAI GPT-4 API集成
  - [ ] 文本嵌入(Embedding)API集成
  - [ ] 成本控制和缓存机制
  - [ ] 本地模型备选(Ollama + Qwen2.5)
- [ ] **智能分析引擎升级**
  - [ ] 语义概念提取(替代关键词匹配)
  - [ ] 复杂关系识别(因果、对比、支持等)
  - [ ] 论证结构分析(观点-论据-结论)
  - [ ] 语义重要性评分优化
- [ ] **知识图谱智能化**
  - [ ] 多维度语义相似度算法
  - [ ] 概念层次关系识别
  - [ ] 知识桥接和路径推理引擎
  - [ ] 主题聚类和知识缺口识别
- [ ] **质量保证体系**
  - [ ] 关联准确性评估算法
  - [ ] 知识完整性检查
  - [ ] 冗余关系清理机制

#### 第三阶段: 输出和集成
- [x] Obsidian 格式生成器
- [x] 双向链接网络构建
- [x] 文件组织结构
- [x] 测试和优化

## 当前实现状态

### 已完成功能 ✅

#### 1. 核心架构实现
- **项目结构**: 完整的模块化架构
- **数据模型**: `src/config/models.py` - 完整的数据结构定义
- **配置管理**: `src/config/settings.py` - 系统配置和常量

#### 2. 数据采集模块
- **HTML 解析器**: `src/data_collection/kindle_parser.py`
  - 支持 Kindle HTML 格式解析
  - 自动提取书籍元数据（标题、作者等）
  - 标注内容提取和位置信息记录
  - 章节结构识别

#### 3. AI 分析模块
- **AI 分析接口**: `src/knowledge_graph/ai_analysis.py`
  - 智能概念提取和分类
  - 主题识别和情感分析
  - 人物关系识别
  - 重要性评分系统
  - 知识图谱构建

#### 4. 输出模块
- **Obsidian 生成器**: `src/output/obsidian_generator.py`
  - 生成标准 Markdown 格式文件
  - 创建双向链接网络
  - 自动文件组织
  - 标签系统生成

#### 5. 主程序和工具
- **主程序**: `main.py` - 完整的数据处理流程
- **工具函数**: `src/utils/helpers.py` - 辅助功能
- **依赖管理**: `requirements.txt` - 完整的依赖包列表
- **文档**: `README.md` - 详细的使用说明

### 测试和验证 ✅

#### 1. 测试用例
- **HTML 解析测试**: `tests/test_kindle_parser.py`
- **AI 分析测试**: `tests/test_ai_analysis.py`
- **Obsidian 生成测试**: `tests/test_obsidian_generator.py`

#### 2. 实际运行验证
- **输入文件**: `material/当尼采哭泣 = When Nietzsche wept -- 欧文·亚隆.html`
- **处理结果**: 成功解析 34 个标注
- **输出文件**: 生成了完整的 Obsidian vault，包含 44 个文件

### 生成的知识库内容 📚

#### 统计信息
- **书籍数量**: 1 本
- **标注总数**: 34 个
- **概念数量**: 15 个
- **人物数量**: 8 个
- **主题数量**: 10 个

#### 核心概念提取
- 权力意志、存在焦虑、自我实现、宗教信仰
- 意义建构、选择责任、无神论、爱情哲学
- 死亡恐惧、精神分析、孤独连接等

#### 主要主题分类
- 存在主义、宗教哲学、哲学思辨
- 心理学、情感分析、道德伦理
- 生死观、自我认知、价值观等

#### 人物关系
- 尼采、布雷尔、弗洛伊德、瓦格纳
- 莎乐美、贝莎、叔本华、上帝

### 文件组织结构 📁

```
book-digger/
├── src/                        # 源代码
│   ├── config/                 # 配置和数据模型
│   ├── data_collection/        # 数据采集
│   ├── knowledge_graph/        # 知识图谱
│   ├── output/                 # 输出模块
│   └── utils/                  # 工具函数
├── material/                   # Kindle 导出文件
├── obsidian_vault/             # 生成的知识库
│   ├── books/                  # 书籍文件
│   ├── concepts/               # 概念文件
│   ├── people/                 # 人物文件
│   ├── themes/                 # 主题文件
│   └── index.md                # 主索引
├── tests/                      # 测试文件
├── plan/                       # 产品计划文档
├── main.py                     # 主程序
├── requirements.txt            # 依赖包
└── README.md                  # 使用说明
```

## 技术特点和优势

### 1. 智能解析能力
- **HTML 结构理解**: 深度理解 Kindle HTML 的复杂结构
- **元数据提取**: 智能识别书名、作者、出版社等信息
- **标注分类**: 支持多种类型的高亮和笔记

### 2. AI 分析能力
- **概念提取**: 智能识别文本中的核心概念
- **主题分类**: 自动将内容分类到不同主题
- **情感分析**: 分析文本的情感色彩
- **重要性评分**: 计算内容的重要程度

### 3. 知识图谱构建
- **节点创建**: 为概念、人物、主题创建节点
- **关系建立**: 建立节点间的关联关系
- **权重计算**: 计算关系的强度和重要性

### 4. Obsidian 集成
- **双向链接**: 创建完整的双向链接网络
- **文件组织**: 按类型自动组织文件结构
- **标签系统**: 生成智能标签便于检索

## 扩展计划

### 短期扩展
1. **批量处理**: 支持处理多个 Kindle 文件
2. **增量更新**: 只处理新增的标注内容
3. **配置化**: 允许用户自定义 AI 分析参数

### 中期扩展 (正在实施)
1. **🔄 LLM智能分析升级**: 正在集成OpenAI GPT-4和嵌入服务
   - 语义概念提取替代关键词匹配
   - 复杂关系识别(因果、对比、支持等)
   - 论证结构分析和知识桥接
2. **多语言支持**: 支持英文、中文等多语言内容
3. **可视化**: 增加知识图谱的可视化展示

### 长期扩展
1. **Web 界面**: 开发 Web 版本的管理界面
2. **云服务**: 支持云端数据处理和存储
3. **移动端**: 开发移动端应用

## 使用指南

### 基本使用
1. 将 Kindle 导出的 HTML 文件放入 `material/` 目录
2. 运行 `python main.py`
3. 在 `obsidian_vault/` 目录中查看生成的知识库

### 高级使用
- 修改 `src/config/settings.py` 中的配置参数
- 自定义 `src/knowledge_graph/ai_analysis.py` 中的 AI 分析逻辑
- 扩展 `src/output/obsidian_generator.py` 中的输出格式

## 技术债务和优化点

### 当前限制与正在解决的问题
1. **🔄 AI 分析升级中**: 正在从模拟接口升级为真实LLM服务
   - ✅ 已完成配置框架设计
   - 🔄 正在实施OpenAI API集成
   - 📋 计划添加成本控制和缓存机制
2. **性能优化**: 大量数据时需要优化处理速度
3. **错误处理**: 需要更完善的错误处理机制

### 优化方案 (实施中)
1. **🔄 智能缓存机制**: 正在实现LLM结果缓存系统
2. **批处理优化**: 实现智能批量处理减少API调用
3. **成本控制**: 添加每日API成本限制和监控
4. **本地备选**: 集成Ollama作为离线处理方案

## 总结

当前项目已经完成了基础版本的开发，成功实现了从 Kindle HTML 文件到 Obsidian 知识库的完整流程。系统能够智能解析、分析标注内容，并构建完整的知识图谱。生成的知识库包含了丰富的概念关联和双向链接，为用户的知识管理提供了强大的支持。

项目具有良好的扩展性，可以根据需要进一步集成真实的 AI 服务、增加更多功能模块，并优化性能和用户体验。