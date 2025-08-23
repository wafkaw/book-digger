# 📖 Kindle Assistant CLI 使用指南

完整的命令行工具使用指南，涵盖所有功能和最佳实践。

## 🚀 快速开始

### 安装和初始化
```bash
# 1. 初始化项目环境
./kindle-assistant init

# 2. 配置环境变量
cp cli/.env.example cli/.env
# 编辑 cli/.env 文件，添加你的API密钥

# 3. 检查系统状态
./kindle-assistant status
```

## 📋 完整命令列表

### 🔧 服务管理

#### 启动Web服务
```bash
./kindle-assistant start
```
- 启动完整的Web应用栈（FastAPI + Vue3 + Celery + Redis + PostgreSQL）
- 服务地址：
  - 前端: http://localhost:3000
  - 后端API: http://localhost:8000
  - API文档: http://localhost:8000/docs
  - Celery监控: http://localhost:5555

#### 停止Web服务
```bash
./kindle-assistant stop
```

#### 重启Web服务
```bash
./kindle-assistant restart
```

#### 查看系统状态
```bash
./kindle-assistant status
```
显示：
- Web服务运行状态
- 目录结构检查
- 输入文件统计
- 系统健康状况

### 🧠 分析处理

#### CLI分析（推荐）
```bash
# 分析所有输入文件
./kindle-assistant analyze

# 分析特定文件
./kindle-assistant analyze --file shared/inputs/book.html

# 调试模式分析
./kindle-assistant analyze --debug

# 组合使用
./kindle-assistant analyze --debug --file shared/inputs/specific-book.html
```

**处理流程**：
1. 解析Kindle HTML导出文件
2. LLM智能概念提取和分析
3. 构建知识图谱和关联关系
4. 生成Obsidian双向链接网络
5. 输出到 `shared/outputs/` 目录

#### Web API处理
```bash
./kindle-assistant process path/to/file.html
```
*注意：需要先启动Web服务*

### ⚙️ 配置管理

#### 环境初始化
```bash
./kindle-assistant init
```
自动执行：
- Python环境检查
- CLI依赖安装
- Docker环境检查
- 环境变量验证
- 目录结构创建

#### 配置查看
```bash
./kindle-assistant config list
```

#### 配置设置
```bash
./kindle-assistant config set KEY VALUE
```

### 🧹 维护工具

#### 清理临时文件
```bash
# 清理所有临时文件
./kindle-assistant clean

# 清理特定目录
./kindle-assistant clean cache     # 清理缓存
./kindle-assistant clean logs      # 清理日志
./kindle-assistant clean uploads   # 清理上传文件
./kindle-assistant clean outputs   # 清理输出文件
```

#### 查看日志
```bash
# 查看所有日志
./kindle-assistant logs

# 查看Web服务日志
./kindle-assistant logs web

# 查看CLI日志
./kindle-assistant logs cli

# 指定日志行数
./kindle-assistant logs web --lines 100
```

#### 健康检查
```bash
./kindle-assistant health
```
检查项目：
- Web API连通性
- 服务状态
- 磁盘使用情况
- 系统资源状态

#### 版本信息
```bash
./kindle-assistant version
```

## 🎯 使用场景和工作流

### 场景1：首次使用
```bash
# 1. 初始化环境
./kindle-assistant init

# 2. 配置API密钥
nano cli/.env

# 3. 添加Kindle导出文件
cp your-kindle-export.html shared/inputs/

# 4. 运行分析
./kindle-assistant analyze

# 5. 查看结果
ls shared/outputs/
```

### 场景2：Web服务开发
```bash
# 1. 启动Web服务
./kindle-assistant start

# 2. 查看状态
./kindle-assistant status

# 3. 监控日志
./kindle-assistant logs web

# 4. 健康检查
./kindle-assistant health

# 5. 停止服务
./kindle-assistant stop
```

### 场景3：大量文件批量处理
```bash
# 1. 放置多个HTML文件到inputs目录
cp *.html shared/inputs/

# 2. 清理旧缓存（可选）
./kindle-assistant clean cache

# 3. 批量分析
./kindle-assistant analyze --debug

# 4. 监控处理进度
./kindle-assistant logs cli

# 5. 检查输出结果
./kindle-assistant status
```

### 场景4：问题排查
```bash
# 1. 检查系统状态
./kindle-assistant status

# 2. 运行健康检查
./kindle-assistant health

# 3. 查看详细日志
./kindle-assistant logs --lines 200

# 4. 调试模式重新分析
./kindle-assistant analyze --debug --file problematic-file.html

# 5. 清理并重试
./kindle-assistant clean cache
./kindle-assistant analyze
```

## 🔧 高级技巧

### 快捷脚本使用
```bash
# 创建软链接到系统PATH
sudo ln -s $(pwd)/kindle-assistant /usr/local/bin/ka

# 现在可以在任意目录使用
ka status
ka analyze --debug
```

### 环境变量配置
```bash
# CLI配置 (cli/.env)
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
AI_BATCH_SIZE=5
ENABLE_CACHING=true
DEBUG_MODE=false

# Web配置 (web/.env)
DATABASE_URL=postgresql://user:pass@db:5432/kindle_web
REDIS_URL=redis://redis:6379/0
MAX_FILE_SIZE=10485760
```

### 性能优化建议
1. **启用缓存**: `ENABLE_CACHING=true` 避免重复分析
2. **调整批次大小**: `AI_BATCH_SIZE=3` 根据API限制调整
3. **监控资源**: 使用 `./kindle-assistant health` 监控
4. **定期清理**: 定期清理缓存和日志文件

### 故障排除

#### 常见问题

**问题1: CLI分析失败**
```bash
# 检查环境配置
./kindle-assistant config list

# 查看详细错误日志
./kindle-assistant analyze --debug

# 检查输入文件格式
file shared/inputs/*.html
```

**问题2: Web服务启动失败**
```bash
# 检查Docker状态
docker ps -a
docker-compose logs

# 清理并重新启动
./kindle-assistant stop
docker system prune -f
./kindle-assistant start
```

**问题3: 权限问题**
```bash
# 确保CLI可执行
chmod +x kindle-assistant

# 检查目录权限
ls -la shared/
```

## 📈 最佳实践

### 1. 文件组织
- 将Kindle HTML文件放入 `shared/inputs/` 
- 输出结果在 `shared/outputs/` 查看
- 定期清理 `shared/data/cache/` 缓存

### 2. 性能优化
- 启用智能缓存避免重复处理
- 使用调试模式排查问题
- 监控API使用量控制成本

### 3. 团队协作
- 使用Web版本进行团队共享
- 通过Git管理配置文件（不包含敏感信息）
- 使用Docker确保环境一致性

### 4. 安全考虑
- 不要将API密钥提交到版本控制
- 使用 `.env` 文件管理敏感配置
- 定期更新依赖包

---

## 🎉 总结

Kindle Assistant CLI提供了完整的项目管理功能：

- **🖥️ CLI分析**: 高性能本地处理
- **🌐 Web服务**: 多用户友好界面
- **⚙️ 统一管理**: 一个命令管理全部功能
- **🔧 维护工具**: 日志、清理、健康检查
- **📊 状态监控**: 实时系统状态显示

通过本指南，你可以充分利用所有功能，高效地将Kindle笔记转换为智能知识图谱！