"""
Settings and configuration management for ROMA research agent.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import logging

from ..utils.config_utils import load_config, get_default_config, validate_config, get_config_schema

logger = logging.getLogger(__name__)


@dataclass
class WorkflowSettings:
    """Workflow-specific settings."""
    max_concurrent_files: int = 10
    max_concurrent_analysis: int = 5
    research_depth: str = "medium"
    max_results: int = 50


@dataclass
class LoggingSettings:
    """Logging settings."""
    level: str = "INFO"
    log_file: Optional[str] = None
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class FileProcessingSettings:
    """File processing settings."""
    max_file_size_mb: int = 100
    supported_extensions: List[str] = field(default_factory=lambda: [
        '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml',
        '.yaml', '.yml', '.csv', '.log', '.rst', '.tex', '.sql',
        '.pdf', '.docx', '.xlsx'
    ])
    exclude_patterns: List[str] = field(default_factory=lambda: [
        '*.pyc', '*.pyo', '*.pyd', '__pycache__/*', '.git/*',
        'node_modules/*', '*.log', '*.tmp', '.DS_Store'
    ])


@dataclass
class AnalysisSettings:
    """Analysis settings."""
    min_keyword_length: int = 3
    max_keywords_per_file: int = 20
    min_content_length: int = 10
    chunk_size: int = 1000
    chunk_overlap: int = 100


@dataclass
class ResearchSettings:
    """Research settings."""
    min_confidence_threshold: float = 0.1
    max_findings_per_category: int = 10
    enable_entity_extraction: bool = True
    enable_relationship_extraction: bool = True


class Settings:
    """Main settings class for ROMA research agent."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize settings.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        self._config_dict = {}
        self._load_configuration()
        self._setup_settings()
    
    def _load_configuration(self):
        """Load configuration from file or use defaults."""
        default_config = get_default_config()
        
        if self.config_path:
            config_file = Path(self.config_path)
            if config_file.exists():
                self._config_dict = load_config(config_file, default_config)
            else:
                logger.warning(f"Config file {config_file} not found, using defaults")
                self._config_dict = default_config
        else:
            # Try to load from standard locations
            possible_config_paths = [
                Path.cwd() / "roma_config.yaml",
                Path.cwd() / "roma_config.yml", 
                Path.cwd() / "roma_config.json",
                Path.cwd() / "config" / "roma_config.yaml",
                Path(__file__).parent / "default_config.yaml"
            ]
            
            config_loaded = False
            for config_path in possible_config_paths:
                if config_path.exists():
                    try:
                        self._config_dict = load_config(config_path, default_config)
                        logger.info(f"Loaded configuration from {config_path}")
                        config_loaded = True
                        break
                    except Exception as e:
                        logger.warning(f"Failed to load config from {config_path}: {e}")
            
            if not config_loaded:
                logger.info("No configuration file found, using default settings")
                self._config_dict = default_config
        
        # Validate configuration
        schema = get_config_schema()
        if not validate_config(self._config_dict, schema):
            logger.warning("Configuration validation failed, some settings may be invalid")
    
    def _setup_settings(self):
        """Set up individual setting objects."""
        workflow_config = self._config_dict.get('workflow', {})
        self.workflow = WorkflowSettings(
            max_concurrent_files=workflow_config.get('max_concurrent_files', 10),
            max_concurrent_analysis=workflow_config.get('max_concurrent_analysis', 5),
            research_depth=workflow_config.get('research_depth', 'medium'),
            max_results=workflow_config.get('max_results', 50)
        )
        
        logging_config = self._config_dict.get('logging', {})
        self.logging = LoggingSettings(
            level=logging_config.get('level', 'INFO'),
            log_file=logging_config.get('log_file'),
            format=logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        file_config = self._config_dict.get('file_processing', {})
        self.file_processing = FileProcessingSettings(
            max_file_size_mb=file_config.get('max_file_size_mb', 100),
            supported_extensions=file_config.get('supported_extensions', FileProcessingSettings().supported_extensions),
            exclude_patterns=file_config.get('exclude_patterns', FileProcessingSettings().exclude_patterns)
        )
        
        analysis_config = self._config_dict.get('analysis', {})
        self.analysis = AnalysisSettings(
            min_keyword_length=analysis_config.get('min_keyword_length', 3),
            max_keywords_per_file=analysis_config.get('max_keywords_per_file', 20),
            min_content_length=analysis_config.get('min_content_length', 10),
            chunk_size=analysis_config.get('chunk_size', 1000),
            chunk_overlap=analysis_config.get('chunk_overlap', 100)
        )
        
        research_config = self._config_dict.get('research', {})
        self.research = ResearchSettings(
            min_confidence_threshold=research_config.get('min_confidence_threshold', 0.1),
            max_findings_per_category=research_config.get('max_findings_per_category', 10),
            enable_entity_extraction=research_config.get('enable_entity_extraction', True),
            enable_relationship_extraction=research_config.get('enable_relationship_extraction', True)
        )
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get the raw configuration dictionary."""
        return self._config_dict.copy()
    
    def update_setting(self, section: str, key: str, value: Any):
        """
        Update a specific setting.
        
        Args:
            section: Configuration section
            key: Setting key
            value: New value
        """
        if section not in self._config_dict:
            self._config_dict[section] = {}
        
        self._config_dict[section][key] = value
        
        # Update the corresponding setting object
        if section == 'workflow' and hasattr(self.workflow, key):
            setattr(self.workflow, key, value)
        elif section == 'logging' and hasattr(self.logging, key):
            setattr(self.logging, key, value)
        elif section == 'file_processing' and hasattr(self.file_processing, key):
            setattr(self.file_processing, key, value)
        elif section == 'analysis' and hasattr(self.analysis, key):
            setattr(self.analysis, key, value)
        elif section == 'research' and hasattr(self.research, key):
            setattr(self.research, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary format."""
        return {
            'workflow': {
                'max_concurrent_files': self.workflow.max_concurrent_files,
                'max_concurrent_analysis': self.workflow.max_concurrent_analysis,
                'research_depth': self.workflow.research_depth,
                'max_results': self.workflow.max_results
            },
            'logging': {
                'level': self.logging.level,
                'log_file': self.logging.log_file,
                'format': self.logging.format
            },
            'file_processing': {
                'max_file_size_mb': self.file_processing.max_file_size_mb,
                'supported_extensions': self.file_processing.supported_extensions,
                'exclude_patterns': self.file_processing.exclude_patterns
            },
            'analysis': {
                'min_keyword_length': self.analysis.min_keyword_length,
                'max_keywords_per_file': self.analysis.max_keywords_per_file,
                'min_content_length': self.analysis.min_content_length,
                'chunk_size': self.analysis.chunk_size,
                'chunk_overlap': self.analysis.chunk_overlap
            },
            'research': {
                'min_confidence_threshold': self.research.min_confidence_threshold,
                'max_findings_per_category': self.research.max_findings_per_category,
                'enable_entity_extraction': self.research.enable_entity_extraction,
                'enable_relationship_extraction': self.research.enable_relationship_extraction
            }
        }


# Global settings instance
_settings_instance = None


def get_settings(config_path: Optional[str] = None) -> Settings:
    """
    Get the global settings instance.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Settings instance
    """
    global _settings_instance
    
    if _settings_instance is None:
        _settings_instance = Settings(config_path)
    
    return _settings_instance


def reload_settings(config_path: Optional[str] = None):
    """
    Reload settings from configuration file.
    
    Args:
        config_path: Optional path to configuration file
    """
    global _settings_instance
    _settings_instance = Settings(config_path)