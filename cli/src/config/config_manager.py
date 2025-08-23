"""
配置管理器
支持多层级配置：命令行参数 > 环境变量 > 配置文件 > 默认值
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class LLMConfig:
    """LLM配置"""
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    provider: str = "openai"

@dataclass
class ProcessingConfig:
    """处理配置"""
    batch_size: int = 5
    enable_caching: bool = True
    importance_threshold: float = 0.5
    max_concept_length: int = 50
    debug_mode: bool = False

@dataclass
class OutputConfig:
    """输出配置"""
    default_format: str = "obsidian"
    output_dir: str = ""
    json_pretty: bool = True
    obsidian_template: str = "default"

@dataclass
class AppConfig:
    """应用配置"""
    llm: LLMConfig
    processing: ProcessingConfig
    output: OutputConfig
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".kindle-assistant"
        self.config_file = self.config_dir / "config.yml"
        self.default_config = self._get_default_config()
        
        # 确保配置目录存在
        self.config_dir.mkdir(exist_ok=True)
    
    def _get_default_config(self) -> AppConfig:
        """获取默认配置"""
        return AppConfig(
            llm=LLMConfig(),
            processing=ProcessingConfig(),
            output=OutputConfig()
        )
    
    def load_config(self) -> AppConfig:
        """加载配置（按优先级合并）"""
        config = self.default_config
        
        # 1. 从配置文件加载
        if self.config_file.exists():
            file_config = self._load_from_file()
            config = self._merge_configs(config, file_config)
        
        # 2. 从环境变量加载
        env_config = self._load_from_env()
        config = self._merge_configs(config, env_config)
        
        return config
    
    def _load_from_file(self) -> AppConfig:
        """从配置文件加载"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                return self.default_config
            
            # 构建配置对象
            llm_data = data.get('llm', {})
            processing_data = data.get('processing', {})
            output_data = data.get('output', {})
            
            return AppConfig(
                llm=LLMConfig(**{k: v for k, v in llm_data.items() if v is not None}),
                processing=ProcessingConfig(**{k: v for k, v in processing_data.items() if v is not None}),
                output=OutputConfig(**{k: v for k, v in output_data.items() if v is not None})
            )
            
        except Exception:
            return self.default_config
    
    def _load_from_env(self) -> AppConfig:
        """从环境变量加载"""
        config = AppConfig(
            llm=LLMConfig(),
            processing=ProcessingConfig(), 
            output=OutputConfig()
        )
        
        # LLM配置
        if os.getenv('OPENAI_API_KEY'):
            config.llm.api_key = os.getenv('OPENAI_API_KEY')
        if os.getenv('OPENAI_BASE_URL'):
            config.llm.base_url = os.getenv('OPENAI_BASE_URL')
        if os.getenv('OPENAI_MODEL'):
            config.llm.model = os.getenv('OPENAI_MODEL')
        
        # 处理配置
        if os.getenv('AI_BATCH_SIZE'):
            try:
                config.processing.batch_size = int(os.getenv('AI_BATCH_SIZE'))
            except ValueError:
                pass
        
        if os.getenv('ENABLE_CACHING'):
            config.processing.enable_caching = os.getenv('ENABLE_CACHING').lower() in ['true', '1', 'yes']
        
        if os.getenv('IMPORTANCE_THRESHOLD'):
            try:
                config.processing.importance_threshold = float(os.getenv('IMPORTANCE_THRESHOLD'))
            except ValueError:
                pass
        
        if os.getenv('DEBUG_MODE'):
            config.processing.debug_mode = os.getenv('DEBUG_MODE').lower() in ['true', '1', 'yes']
        
        return config
    
    def _merge_configs(self, base: AppConfig, override: AppConfig) -> AppConfig:
        """合并配置（override优先）"""
        merged = AppConfig(
            llm=LLMConfig(),
            processing=ProcessingConfig(),
            output=OutputConfig()
        )
        
        # LLM配置
        merged.llm.api_key = override.llm.api_key or base.llm.api_key
        merged.llm.base_url = override.llm.base_url or base.llm.base_url
        merged.llm.model = override.llm.model or base.llm.model
        merged.llm.provider = override.llm.provider or base.llm.provider
        
        # 处理配置
        merged.processing.batch_size = override.processing.batch_size or base.processing.batch_size
        merged.processing.enable_caching = override.processing.enable_caching if override.processing.enable_caching is not None else base.processing.enable_caching
        merged.processing.importance_threshold = override.processing.importance_threshold or base.processing.importance_threshold
        merged.processing.max_concept_length = override.processing.max_concept_length or base.processing.max_concept_length
        merged.processing.debug_mode = override.processing.debug_mode if override.processing.debug_mode is not None else base.processing.debug_mode
        
        # 输出配置
        merged.output.default_format = override.output.default_format or base.output.default_format
        merged.output.output_dir = override.output.output_dir or base.output.output_dir
        merged.output.json_pretty = override.output.json_pretty if override.output.json_pretty is not None else base.output.json_pretty
        merged.output.obsidian_template = override.output.obsidian_template or base.output.obsidian_template
        
        return merged
    
    def apply_cli_args(self, config: AppConfig, **kwargs) -> AppConfig:
        """应用命令行参数（最高优先级）"""
        # LLM参数
        if kwargs.get('llm_key'):
            config.llm.api_key = kwargs['llm_key']
        if kwargs.get('llm_base_url'):
            config.llm.base_url = kwargs['llm_base_url']
        if kwargs.get('llm_model'):
            config.llm.model = kwargs['llm_model']
        
        # 处理参数
        if kwargs.get('debug') is not None:
            config.processing.debug_mode = kwargs['debug']
        
        # 输出参数
        if kwargs.get('format'):
            config.output.default_format = kwargs['format']
        if kwargs.get('output'):
            config.output.output_dir = kwargs['output']
        
        return config
    
    def save_config(self, config: AppConfig):
        """保存配置到文件"""
        config_data = {
            'llm': {
                'api_key': config.llm.api_key if config.llm.api_key else None,
                'base_url': config.llm.base_url,
                'model': config.llm.model,
                'provider': config.llm.provider
            },
            'processing': {
                'batch_size': config.processing.batch_size,
                'enable_caching': config.processing.enable_caching,
                'importance_threshold': config.processing.importance_threshold,
                'max_concept_length': config.processing.max_concept_length,
                'debug_mode': config.processing.debug_mode
            },
            'output': {
                'default_format': config.output.default_format,
                'output_dir': config.output.output_dir if config.output.output_dir else None,
                'json_pretty': config.output.json_pretty,
                'obsidian_template': config.output.obsidian_template
            }
        }
        
        # 移除空值
        config_data = self._remove_none_values(config_data)
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True, indent=2)
    
    def _remove_none_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """递归移除None值"""
        if isinstance(data, dict):
            return {k: self._remove_none_values(v) for k, v in data.items() if v is not None}
        elif isinstance(data, list):
            return [self._remove_none_values(item) for item in data if item is not None]
        else:
            return data
    
    def get_llm_providers(self) -> Dict[str, Dict[str, str]]:
        """获取预定义的LLM提供商配置"""
        return {
            'openai': {
                'base_url': 'https://api.openai.com/v1',
                'model': 'gpt-4o-mini',
                'description': 'OpenAI GPT models'
            },
            'zhipu': {
                'base_url': 'https://open.bigmodel.cn/api/paas/v4',
                'model': 'glm-4-air',
                'description': 'Zhipu AI GLM models'
            },
            'claude': {
                'base_url': 'https://api.anthropic.com/v1',
                'model': 'claude-3-sonnet',
                'description': 'Anthropic Claude models'
            }
        }
    
    def set_provider(self, provider_name: str, api_key: str) -> bool:
        """设置LLM提供商"""
        providers = self.get_llm_providers()
        if provider_name not in providers:
            return False
        
        config = self.load_config()
        provider_config = providers[provider_name]
        
        config.llm.provider = provider_name
        config.llm.api_key = api_key
        config.llm.base_url = provider_config['base_url']
        config.llm.model = provider_config['model']
        
        self.save_config(config)
        return True
    
    def test_llm_connection(self, config: AppConfig) -> bool:
        """测试LLM连接"""
        try:
            # 这里可以添加实际的连接测试逻辑
            # 暂时只检查必需的配置是否存在
            if not config.llm.api_key:
                return False
            if not config.llm.base_url:
                return False
            if not config.llm.model:
                return False
            return True
        except Exception:
            return False

# 全局配置管理器实例
config_manager = ConfigManager()