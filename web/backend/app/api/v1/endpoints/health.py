"""
Health check endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import redis
import time
from typing import Dict, Any

from app.core.config import settings
from app.models.database import get_db

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.VERSION
    }


@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Detailed health check including dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.VERSION,
        "components": {}
    }
    
    # Check database
    try:
        db.execute("SELECT 1")
        health_status["components"]["database"] = {"status": "healthy"}
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy", 
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        health_status["components"]["redis"] = {"status": "healthy"}
    except Exception as e:
        health_status["components"]["redis"] = {
            "status": "unhealthy", 
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    return health_status