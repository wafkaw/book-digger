"""
LLM Service Integration for Kindle Reading Assistant
Provides OpenAI GPT-4 API integration with cost control and caching
"""
import os
import json
import time
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path

import openai
from openai import OpenAI
import tiktoken
import redis
from ..config.settings import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class APICostTracker:
    """Tracks API usage and costs"""
    total_cost: float = 0.0
    daily_cost: float = 0.0
    request_count: int = 0
    daily_request_count: int = 0
    last_reset: datetime = None
    
    def __post_init__(self):
        if self.last_reset is None:
            self.last_reset = datetime.now()
    
    def add_cost(self, cost: float, is_new_day: bool = False):
        """Add cost to tracker"""
        self.total_cost += cost
        self.request_count += 1
        
        if is_new_day:
            self.daily_cost = cost
            self.daily_request_count = 1
            self.last_reset = datetime.now()
        else:
            self.daily_cost += cost
            self.daily_request_count += 1
    
    def is_daily_limit_exceeded(self, max_daily_cost: float) -> bool:
        """Check if daily cost limit is exceeded"""
        return self.daily_cost >= max_daily_cost
    
    def reset_daily(self):
        """Reset daily counters"""
        self.daily_cost = 0.0
        self.daily_request_count = 0
        self.last_reset = datetime.now()


class CacheManager:
    """Manages caching for LLM responses"""
    
    def __init__(self, redis_url: Optional[str] = None, use_file_cache: bool = True):
        self.redis_client = None
        self.use_file_cache = use_file_cache
        self.cache_dir = Path(Config.DATA_DIR) / "cache"
        
        # Try Redis first
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}, falling back to file cache")
                self.use_file_cache = True
        
        # Initialize file cache
        if self.use_file_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("File cache initialized")
    
    def _get_cache_key(self, prompt: str, model: str) -> str:
        """Generate cache key from prompt and model"""
        import hashlib
        content = f"{prompt}_{model}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, model: str) -> Optional[str]:
        """Get cached response"""
        cache_key = self._get_cache_key(prompt, model)
        
        if self.redis_client:
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")
        
        if self.use_file_cache:
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Check TTL
                        if time.time() - data.get('timestamp', 0) < Config.CACHE_TTL_HOURS * 3600:
                            return data.get('response')
                except Exception as e:
                    logger.warning(f"File cache get failed: {e}")
        
        return None
    
    def set(self, prompt: str, model: str, response: str):
        """Set cached response"""
        cache_key = self._get_cache_key(prompt, model)
        
        cache_data = {
            'response': response,
            'timestamp': time.time(),
            'model': model
        }
        
        if self.redis_client:
            try:
                self.redis_client.setex(
                    cache_key, 
                    Config.CACHE_TTL_HOURS * 3600, 
                    json.dumps(cache_data, ensure_ascii=False)
                )
                return
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")
        
        if self.use_file_cache:
            cache_file = self.cache_dir / f"{cache_key}.json"
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.warning(f"File cache set failed: {e}")


class LLMService:
    """Main LLM service class for OpenAI integration"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, 
                 model: Optional[str] = None, mock_mode: bool = False):
        """
        Initialize LLM Service
        
        Args:
            api_key: API key for the service
            base_url: Base URL for OpenAI-compatible API (e.g., for other providers)
            model: Model name to use
            mock_mode: Whether to run in mock mode for testing
        """
        self.mock_mode = mock_mode
        self.cost_tracker = APICostTracker()
        self.cache_manager = CacheManager()
        
        # Initialize OpenAI client
        if not mock_mode:
            # Use provided parameters or fall back to config
            api_key = api_key or Config.OPENAI_API_KEY
            base_url = base_url or Config.OPENAI_BASE_URL
            model = model or Config.OPENAI_MODEL
            
            if not api_key:
                raise ValueError("API key is required when not in mock mode")
            
            # Initialize client with optional base URL for OpenAI-compatible APIs
            client_kwargs = {"api_key": api_key}
            if base_url:
                client_kwargs["base_url"] = base_url
                logger.info(f"Using custom base URL: {base_url}")
            
            self.client = OpenAI(**client_kwargs)
            self.model = model
            self.base_url = base_url
            self.embedding_model = Config.OPENAI_EMBEDDING_MODEL
            self.max_tokens = Config.OPENAI_MAX_TOKENS
            self.temperature = Config.OPENAI_TEMPERATURE
            
            # Initialize tokenizer (fallback for non-OpenAI models)
            try:
                if not base_url or "api.openai.com" in base_url:
                    # Official OpenAI API
                    self.tokenizer = tiktoken.encoding_for_model(self.model)
                else:
                    # Other providers - use a default tokenizer
                    self.tokenizer = tiktoken.get_encoding("cl100k_base")
                    logger.info(f"Using default tokenizer for custom API: {base_url}")
            except Exception as e:
                logger.warning(f"Could not initialize tokenizer: {e}, using default")
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        logger.info(f"LLM Service initialized (mock_mode={mock_mode}, model={model if not mock_mode else 'mock'})")
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if hasattr(self, 'tokenizer'):
            return len(self.tokenizer.encode(text))
        else:
            # Rough estimate for mock mode
            return len(text) // 4
    
    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate API cost"""
        # GPT-4o-mini pricing (as of 2024)
        input_cost_per_1k = 0.00015  # $0.00015 per 1K input tokens
        output_cost_per_1k = 0.0006  # $0.0006 per 1K output tokens
        
        input_cost = (input_tokens / 1000) * input_cost_per_1k
        output_cost = (output_tokens / 1000) * output_cost_per_1k
        
        return input_cost + output_cost
    
    def _check_daily_limit(self):
        """Check if daily cost limit is exceeded"""
        if self.cost_tracker.is_daily_limit_exceeded(Config.MAX_DAILY_API_COST):
            raise Exception(f"Daily API cost limit exceeded (${self.cost_tracker.daily_cost:.2f})")
    
    def _reset_daily_if_needed(self):
        """Reset daily counters if it's a new day"""
        now = datetime.now()
        if (now - self.cost_tracker.last_reset).days >= 1:
            self.cost_tracker.reset_daily()
    
    def _get_cached_response(self, prompt: str) -> Optional[str]:
        """Get response from cache"""
        if Config.ENABLE_CACHING:
            return self.cache_manager.get(prompt, self.model)
        return None
    
    def _cache_response(self, prompt: str, response: str):
        """Cache response"""
        if Config.ENABLE_CACHING:
            self.cache_manager.set(prompt, self.model, response)
    
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using OpenAI API"""
        if self.mock_mode:
            return self._mock_generate_text(prompt, system_prompt)
        
        # Check cache first
        cached_response = self._get_cached_response(prompt)
        if cached_response:
            logger.info("Using cached response")
            return cached_response
        
        # Check daily limit
        self._check_daily_limit()
        self._reset_daily_if_needed()
        
        try:
            # Count input tokens
            input_text = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            input_tokens = self._count_tokens(input_text)
            
            # Make API call
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Extract response
            generated_text = response.choices[0].message.content
            
            # Count output tokens and calculate cost
            output_tokens = self._count_tokens(generated_text)
            cost = self._estimate_cost(input_tokens, output_tokens)
            
            # Update cost tracker
            self.cost_tracker.add_cost(cost)
            
            # Cache response
            self._cache_response(prompt, generated_text)
            
            logger.info(f"Generated text: {input_tokens} input tokens, {output_tokens} output tokens, ${cost:.4f}")
            
            return generated_text
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise Exception(f"LLM generation failed: {e}")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        if self.mock_mode:
            return self._mock_generate_embeddings(texts)
        
        try:
            # Check daily limit
            self._check_daily_limit()
            self._reset_daily_if_needed()
            
            # Batch process texts
            all_embeddings = []
            for i in range(0, len(texts), Config.BATCH_PROCESSING_SIZE):
                batch = texts[i:i + Config.BATCH_PROCESSING_SIZE]
                
                response = self.client.embeddings.create(
                    model=self.embedding_model,
                    input=batch
                )
                
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)
                
                # Estimate cost (rough calculation)
                total_tokens = sum(len(text.split()) for text in batch)
                cost = total_tokens * 0.0000001  # Rough estimate for embeddings
                self.cost_tracker.add_cost(cost)
                
                logger.info(f"Generated embeddings for {len(batch)} texts, ${cost:.4f}")
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            raise Exception(f"Embedding generation failed: {e}")
    
    def _mock_generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Mock text generation for testing"""
        # Simulate processing delay
        time.sleep(0.1)
        
        # Generate mock response based on prompt keywords
        prompt_lower = prompt.lower()
        
        if "概念" in prompt or "concept" in prompt_lower:
            return "['权力意志', '存在焦虑', '自我实现', '意义建构', '选择责任']"
        elif "主题" in prompt or "theme" in prompt_lower:
            return "['存在主义', '哲学思辨', '心理学', '自我认知', '价值观']"
        elif "情感" in prompt or "emotion" in prompt_lower:
            return "['焦虑', '困惑', '希望', '挣扎', '顿悟']"
        elif "人物" in prompt or "person" in prompt_lower:
            return "['尼采', '布雷尔', '弗洛伊德', '贝莎', '欧文·亚隆']"
        elif "总结" in prompt or "summary" in prompt_lower:
            return "这是一个关于存在主义哲学和心理治疗的深度探讨，通过尼采和布雷尔的对话，展现了人类面对生命意义时的挣扎与觉醒。"
        else:
            return "这是一个模拟的AI分析结果，用于测试和演示目的。"
    
    def _mock_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Mock embedding generation for testing"""
        # Generate random embeddings
        import random
        return [[random.random() for _ in range(1536)] for _ in texts]
    
    def get_cost_stats(self) -> Dict[str, Any]:
        """Get cost tracking statistics"""
        return {
            "total_cost": self.cost_tracker.total_cost,
            "daily_cost": self.cost_tracker.daily_cost,
            "total_requests": self.cost_tracker.request_count,
            "daily_requests": self.cost_tracker.daily_request_count,
            "last_reset": self.cost_tracker.last_reset.isoformat(),
            "daily_limit": Config.MAX_DAILY_API_COST,
            "remaining_daily_budget": max(0, Config.MAX_DAILY_API_COST - self.cost_tracker.daily_cost)
        }


class OllamaService:
    """Local Ollama service as backup"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5:32b"):
        self.base_url = base_url
        self.model = model
        
        try:
            import requests
            self.session = requests.Session()
            # Check if Ollama is running
            response = self.session.get(f"{base_url}/api/tags")
            logger.info(f"Ollama service initialized with model: {model}")
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            self.available = False
        else:
            self.available = True
    
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Ollama"""
        if not self.available:
            raise Exception("Ollama service not available")
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = self.session.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise Exception(f"Ollama generation failed: {e}")


# Service factory
def create_llm_service(
    use_ollama: bool = False, 
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    mock_mode: Optional[bool] = None
) -> Union[LLMService, OllamaService]:
    """
    Create LLM service based on configuration
    
    Args:
        use_ollama: Whether to use Ollama instead of OpenAI-compatible service
        api_key: API key override
        base_url: Base URL override for OpenAI-compatible APIs
        model: Model name override
        mock_mode: Mock mode override
    
    Returns:
        Configured LLM service instance
    """
    if use_ollama and Config.OLLAMA_ENABLED:
        return OllamaService(
            base_url=base_url or Config.OLLAMA_BASE_URL, 
            model=model or Config.OLLAMA_MODEL
        )
    else:
        return LLMService(
            api_key=api_key,
            base_url=base_url,
            model=model,
            mock_mode=mock_mode if mock_mode is not None else Config.AI_MOCK_MODE
        )