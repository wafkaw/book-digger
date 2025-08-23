# Kindle Reading Assistant - CLI Version

A command-line tool that transforms Kindle HTML exports into intelligent Obsidian knowledge graphs with AI-powered analysis.

## 🚀 Quick Start

### Installation

1. **Navigate to CLI directory**
   ```bash
   cd cli
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your LLM provider settings
   ```

4. **Run analysis**
   ```bash
   python main.py
   ```

## 📁 Input/Output

- **Input**: Place Kindle HTML exports in `../shared/inputs/`
- **Output**: Generated Obsidian vault appears in `../shared/outputs/`
- **Cache**: Processing cache stored in `../shared/data/cache/`

## 🔧 Configuration

Edit `.env` file with your preferred LLM provider:

```bash
# OpenAI
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# Zhipu AI
# OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
# OPENAI_MODEL=glm-4-air
```

## ✨ Features

- **Smart HTML Parsing**: Extract highlights and metadata from Kindle exports
- **AI-Powered Analysis**: LLM-based concept extraction and relationship analysis
- **Knowledge Graph**: Generate 125+ interconnected concept nodes
- **Obsidian Integration**: Complete vault with bidirectional links
- **Intelligent Caching**: Avoid redundant API calls
- **Batch Processing**: Optimize API usage with 3-5 annotations per batch

## 📊 Performance

- **Processing Time**: ~7 minutes for 30+ annotations
- **API Efficiency**: 94% reduction in API calls (12 vs 200+)
- **Cache Hit Rate**: Smart content-based caching
- **Output Quality**: 125+ nodes with filtered concepts

## 🧪 Testing

```bash
cd tests
python -m pytest
```

## 📖 Documentation

See `../CLAUDE.md` for complete project documentation.