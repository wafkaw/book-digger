# Kindle Knowledge Graph Web Application

A modern web interface for the Kindle Reading Assistant that generates interactive knowledge graphs from Kindle HTML exports.

## Features

- 📤 **Drag & Drop File Upload**: Intuitive HTML file upload interface
- ⚡ **Real-time Progress**: WebSocket-powered progress tracking
- 🧠 **AI-Powered Analysis**: LLM-based semantic concept extraction
- 🕸️ **Interactive Knowledge Graph**: Web-based visualization of 125+ interconnected nodes
- 📊 **Detailed Analytics**: Statistics on concepts, themes, and people
- 📁 **Obsidian Export**: Download complete knowledge vault files

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key (or compatible provider)

### Development Setup

1. **Clone and navigate to web app directory**
   ```bash
   cd web_app
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Initialize database**
   ```bash
   docker-compose exec backend python -c "
   from app.models.database import create_tables
   create_tables()
   "
   ```

5. **Access the application**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Celery Monitoring: http://localhost:5555

### API Usage

#### 1. Upload File
```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your-kindle-export.html"
```

#### 2. Create Analysis Task
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Content-Type: application/json" \
  -d '{"file_id": "your-file-id", "config": {}}'
```

#### 3. Monitor Progress (WebSocket)
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/tasks/{task_id}/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress:', data.progress, '%');
};
```

#### 4. Get Results
```bash
curl "http://localhost:8000/api/v1/tasks/{task_id}/result"
```

## Architecture

### Backend Stack
- **FastAPI**: Modern async web framework
- **Celery**: Distributed task queue for AI processing  
- **Redis**: Message broker and caching
- **SQLAlchemy**: Database ORM
- **PostgreSQL**: Production database

### Services
- `backend`: FastAPI web server (port 8000)
- `celery_worker`: Background task processor
- `celery_flower`: Task monitoring (port 5555)
- `redis`: Message broker and cache
- `db`: PostgreSQL database

### Data Flow
1. **File Upload** → Store in uploads directory + database
2. **Task Creation** → Queue analysis job in Celery
3. **Background Processing** → Run AI analysis with progress updates
4. **Result Storage** → Save graph data and generate Obsidian files
5. **Client Updates** → Real-time progress via WebSocket

## Configuration

### Environment Variables

```bash
# API Configuration
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# Database
DATABASE_URL=postgresql://user:pass@db:5432/kindle_web

# Redis
REDIS_URL=redis://redis:6379/0

# File Uploads
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR=/app/uploads

# Tasks
TASK_TIMEOUT=1800  # 30 minutes
AI_BATCH_SIZE=5
ENABLE_CACHING=true
```

### Supported AI Providers

**OpenAI**
```bash
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

**Zhipu AI**
```bash
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
OPENAI_MODEL=glm-4.5-air
```

## Development

### Project Structure
```
web_app/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── tasks/          # Celery tasks
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # Vue.js frontend (coming soon)
├── docker-compose.yml
└── .env.example
```

### Running Components Separately

**Backend only**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Celery worker**
```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

### Testing

```bash
# Run tests (when implemented)
docker-compose exec backend pytest

# Check API health
curl http://localhost:8000/health
```

## Monitoring

- **API Health**: `GET /health` and `GET /api/v1/health/detailed`
- **Celery Tasks**: http://localhost:5555 (Flower dashboard)
- **Database**: Standard PostgreSQL monitoring tools
- **Logs**: `docker-compose logs -f [service-name]`

## Next Steps

1. **Frontend Development**: Vue.js application with Cytoscape.js
2. **Graph Visualization**: Interactive knowledge graph rendering
3. **User Authentication**: Multi-user support
4. **Production Deployment**: Kubernetes/cloud deployment configs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

MIT License - see main project for details