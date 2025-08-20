# Kindle Reading Assistant

一个智能的 Kindle 阅读笔记处理工具，能够自动解析 Kindle 导出的 HTML 格式笔记，使用 AI 进行智能分析，并生成 Obsidian 兼容的知识图谱。

## 功能特性

### 🔍 智能解析
- 自动解析 Kindle HTML 格式的导出文件
- 提取书籍元数据（标题、作者、出版社等）
- 识别标注位置和类型
- 支持多种高亮颜色分类

### 🧠 AI 分析
- 智能提取核心概念和主题
- 识别情感色彩和人物关系
- 计算内容重要性评分
- 生成智能标签系统

### 🔗 知识图谱
- 构建概念关联网络
- 建立人物关系图谱
- 生成主题分类结构
- 支持跨书籍知识连接

### 📝 Obsidian 输出
- 生成标准 Markdown 格式文件
- 创建双向链接网络
- 自动组织文件结构
- 支持标签和元数据

## 安装和使用

### 环境要求
- Python 3.8+
- 4GB+ 内存
- 1GB+ 存储空间

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd book-digger
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 准备数据
将 Kindle 导出的 HTML 文件放入 `material/` 目录

4. 运行程序
```bash
python main.py
```

### 使用方法

#### 基本使用
```python
from src.data_collection.kindle_parser import KindleParser
from src.knowledge_graph.ai_analysis import AIAnalysisInterface
from src.output.obsidian_generator import ObsidianGenerator

# 初始化组件
parser = KindleParser()
ai_interface = AIAnalysisInterface(mock_mode=True)
generator = ObsidianGenerator()

# 解析 Kindle 文件
book = parser.parse_file("material/your_book.html")

# 分析内容
analysis_result = ai_interface.analyze_book(book)

# 生成 Obsidian 文件
generator.generate_book_files(book, analysis_result)
```

#### 批量处理
```python
import os
from pathlib import Path

# 处理 material 目录下的所有 HTML 文件
material_dir = Path("material")
for html_file in material_dir.glob("*.html"):
    book = parser.parse_file(str(html_file))
    analysis_result = ai_interface.analyze_book(book)
    generator.generate_book_files(book, analysis_result)
```

## 项目结构

```
book-digger/
├── src/
│   ├── data_collection/     # 数据采集模块
│   │   └── kindle_parser.py
│   ├── processing/          # 数据处理模块
│   ├── knowledge_graph/     # 知识图谱模块
│   │   └── ai_analysis.py
│   ├── relation_analysis/   # 关联分析模块
│   ├── output/             # 输出模块
│   │   └── obsidian_generator.py
│   ├── config/             # 配置管理
│   │   ├── models.py
│   │   └── settings.py
│   └── utils/              # 工具函数
│       └── helpers.py
├── material/               # Kindle 导出文件目录
├── obsidian_vault/         # 生成的 Obsidian 文件
├── tests/                  # 测试文件
├── main.py                 # 主程序入口
└── requirements.txt        # 依赖包
```

## 数据格式

### 输入格式
支持 Kindle 导出的 HTML 格式文件，包含：
- 书籍元数据
- 章节结构
- 标注内容
- 位置信息
- 高亮类型

### 输出格式
生成 Obsidian 兼容的 Markdown 文件：
```
obsidian_vault/
├── books/          # 书籍文件
├── concepts/       # 概念文件
├── people/         # 人物文件
├── themes/         # 主题文件
└── index.md        # 索引文件
```

## 核心功能详解

### 1. 智能解析
- **HTML 解析**：使用 BeautifulSoup 解析 Kindle HTML 文件
- **元数据提取**：自动识别书名、作者、出版社等信息
- **标注识别**：支持不同类型的高亮和笔记
- **位置追踪**：记录页码和位置信息

### 2. AI 分析
- **概念提取**：识别文本中的核心概念和术语
- **主题分类**：按主题对内容进行分类
- **情感分析**：分析文本的情感色彩
- **重要性评分**：计算内容的重要程度

### 3. 知识图谱
- **节点创建**：为概念、人物、主题创建节点
- **关系建立**：建立节点间的关联关系
- **权重计算**：计算关系的强度
- **网络可视化**：支持图谱可视化

### 4. Obsidian 输出
- **Markdown 生成**：生成标准 Markdown 文件
- **双向链接**：创建 Obsidian 双向链接
- **文件组织**：按类型组织文件结构
- **标签系统**：生成智能标签

## 配置选项

### AI 分析配置
```python
# 在 src/config/settings.py 中配置
AI_MOCK_MODE = True          # 使用模拟 AI 分析
AI_MAX_CONCEPTS = 5         # 最大概念数量
AI_MAX_THEMES = 3           # 最大主题数量
AI_MAX_EMOTIONS = 3         # 最大情感数量
```

### 输出配置
```python
OBSIDIAN_BOOKS_DIR = "books"      # 书籍文件目录
OBSIDIAN_CONCEPTS_DIR = "concepts" # 概念文件目录
OBSIDIAN_PEOPLE_DIR = "people"     # 人物文件目录
OBSIDIAN_THEMES_DIR = "themes"     # 主题文件目录
```

## 开发指南

### 运行测试
```bash
python -m pytest tests/
```

### 代码规范
- 使用 PEP 8 代码风格
- 添加类型注解
- 编写单元测试
- 使用 logging 记录日志

### 扩展功能
- 添加新的数据源支持
- 集成真实的 AI 服务
- 增加更多输出格式
- 优化知识图谱算法

## 常见问题

### Q: 如何获取 Kindle 导出文件？
A: 在 Kindle 设备上，选择"导出笔记"功能，或者通过亚马逊网站"我的内容"页面导出。

### Q: 支持中文内容吗？
A: 完全支持中文内容的解析和分析。

### Q: 如何自定义 AI 分析？
A: 可以修改 `ai_analysis.py` 中的 `_mock_analyze_highlight` 方法，或者集成真实的 AI 服务。

### Q: 生成的文件如何导入 Obsidian？
A: 将 `obsidian_vault` 目录设置为 Obsidian 的 vault 目录即可。

## 许可证

MIT License

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0
- 初始版本发布
- 支持 Kindle HTML 解析
- AI 分析功能
- Obsidian 输出
- 知识图谱生成