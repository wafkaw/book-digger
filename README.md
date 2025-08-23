# 📚 Kindle Reading Assistant

Transform your Kindle highlights into intelligent, interconnected knowledge graphs with AI-powered analysis.

## 🌟 Project Overview

A complete solution for processing Kindle HTML exports into rich Obsidian knowledge vaults, featuring:

- **🖥️ CLI Tool**: High-performance local processing for power users
- **🌐 Web Application**: User-friendly browser interface for everyone
- **🤖 AI Analysis**: LLM-powered concept extraction and relationship mapping  
- **🕸️ Knowledge Graphs**: 125+ interconnected nodes with bidirectional links
- **📊 Graph Visualization**: Interactive web-based knowledge exploration

## 🚀 Quick Start

### 🎯 Unified CLI Tool (Recommended)
```bash
# Initialize project environment
./kindle-assistant init

# Quick CLI analysis
./kindle-assistant analyze

# Or start Web services
./kindle-assistant start

# Check system status
./kindle-assistant status
```

### Choose Your Interface

#### 🖥️ CLI Version (For developers)
```bash
cd cli
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key
python main.py
```

#### 🌐 Web Version (For general users)
```bash
cd web
docker-compose up -d
# Access: http://localhost:8000
```

## 📁 Project Structure

```
book-digger/
├── cli/                    # 🖥️ CLI Application
│   ├── src/               # Core analysis engine
│   ├── tests/             # CLI tests  
│   ├── main.py            # CLI entry point
│   └── README.md          # CLI documentation
├── web/                   # 🌐 Web Application
│   ├── backend/           # FastAPI + Celery
│   ├── frontend/          # Vue 3 + TailwindCSS
│   ├── docker-compose.yml # Full-stack deployment
│   └── README.md          # Web documentation  
├── shared/                # 🤝 Shared Resources
│   ├── inputs/            # Kindle HTML files
│   ├── outputs/           # Generated Obsidian vaults
│   └── data/              # Cache and processing data
├── docs/                  # 📚 Documentation
│   └── guides/            # Usage guides
└── scripts/               # 🔧 Development Tools
    ├── dev/               # Development scripts
    ├── test/              # Testing utilities
    └── deploy/            # Deployment scripts
```

## ✨ Key Features

### 🎯 Unified CLI Management
- **Service Control**: `start`, `stop`, `restart` web services with one command
- **Analysis Processing**: `analyze` with debug mode and file selection
- **System Monitoring**: `status`, `health`, `logs` for comprehensive oversight
- **Maintenance Tools**: `clean`, `init`, `config` for easy maintenance

### 🧠 AI-Powered Analysis
- **Smart Concept Extraction**: LLM identifies key concepts, themes, and entities
- **Relationship Mapping**: Intelligent linking based on semantic similarity
- **Quality Filtering**: Automatic removal of low-value concepts
- **Batch Processing**: Optimized API usage (94% call reduction)

### 🕸️ Knowledge Graph Generation  
- **125+ Node Networks**: Dense interconnection of concepts, themes, people
- **Bidirectional Links**: True Obsidian-compatible `[[wikilinks]]`
- **Graph View Optimization**: Tags and clustering for visual exploration
- **Multi-dimensional Navigation**: Concept → Theme → Person pathways

### ⚡ Performance & Scalability
- **CLI**: 7-minute processing, local execution
- **Web**: Multi-user concurrent processing, real-time progress
- **Smart Caching**: Content-based deduplication
- **Error Recovery**: Robust fallback mechanisms

## 🎯 Use Cases

- **📖 Academic Research**: Transform reading notes into explorable knowledge maps
- **✍️ Content Creation**: Discover unexpected connections between ideas  
- **🎓 Learning**: Enhance retention through visual knowledge networks
- **👥 Team Knowledge**: Share and collaborate on knowledge graphs

## 🛠️ Technical Stack

### CLI Version
- **Python 3.8+** - Core processing engine
- **BeautifulSoup** - HTML parsing
- **OpenAI/Zhipu APIs** - AI analysis
- **NetworkX** - Graph algorithms

### Web Version  
- **Backend**: FastAPI, Celery, Redis, PostgreSQL
- **Frontend**: Vue 3, TailwindCSS, Cytoscape.js
- **Deployment**: Docker, docker-compose

## 📊 Performance Metrics

| Metric | CLI Version | Web Version |
|--------|-------------|-------------|
| **Processing Time** | ~7 minutes | ~5-6 minutes |
| **API Efficiency** | 94% call reduction | Same optimization |
| **Concurrent Users** | 1 | Multiple |
| **Setup Complexity** | Python env | Docker only |
| **Output Format** | Local files | Web view + download |

## 🚀 Getting Started

1. **Initialize environment**: `./kindle-assistant init`
2. **Place Kindle HTML exports** in `shared/inputs/`
3. **Run analysis**: `./kindle-assistant analyze`
4. **Or start web interface**: `./kindle-assistant start`

## 🛠️ CLI Commands Reference

```bash
# Service Management
./kindle-assistant start          # Start web services
./kindle-assistant stop           # Stop web services  
./kindle-assistant restart        # Restart web services
./kindle-assistant status         # Show system status

# Analysis & Processing
./kindle-assistant analyze        # Run CLI analysis
./kindle-assistant analyze --debug --file book.html
./kindle-assistant process file.html  # Process via Web API

# Configuration & Maintenance  
./kindle-assistant init           # Initialize environment
./kindle-assistant config list    # Show configuration
./kindle-assistant clean cache    # Clean temporary files
./kindle-assistant logs web       # View service logs
./kindle-assistant health         # System health check
./kindle-assistant version        # Show version info
```

## 📚 Documentation

- **Complete Guide**: [`docs/CLAUDE.md`](docs/CLAUDE.md) - Full project documentation
- **CLI Usage Guide**: [`docs/guides/CLI-Usage-Guide.md`](docs/guides/CLI-Usage-Guide.md) - Detailed CLI reference
- **CLI Code**: [`cli/README.md`](cli/README.md) - Command-line usage
- **Web Guide**: [`web/README.md`](web/README.md) - Web application setup
- **API Docs**: Available at `http://localhost:8000/docs` when web app is running

## 🤝 Contributing

1. Fork the repository
2. Choose your area: CLI (`cli/`) or Web (`web/`)
3. Create feature branch
4. Add tests in respective `tests/` directory  
5. Submit pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

**🌟 Transform your reading highlights into intelligent knowledge networks that enhance learning, discovery, and retention.**