"""
Configuration utilities for the ROMA research agent.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


def load_config(config_path: Union[str, Path], 
               default_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Load configuration from a file.
    
    Args:
        config_path: Path to configuration file
        default_config: Default configuration to use if file doesn't exist
        
    Returns:
        Configuration dictionary
    """
    config_path = Path(config_path)
    
    # Use default config if file doesn't exist
    if not config_path.exists():
        if default_config:
            logger.info(f"Config file {config_path} not found, using default configuration")
            return default_config.copy()
        else:
            logger.warning(f"Config file {config_path} not found and no default provided")
            return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                config = yaml.safe_load(f) or {}
            elif config_path.suffix.lower() == '.json':
                config = json.load(f) or {}
            else:
                raise ValueError(f"Unsupported config file format: {config_path.suffix}")
        
        logger.info(f"Successfully loaded configuration from {config_path}")
        
        # Merge with default config if provided
        if default_config:
            merged_config = default_config.copy()
            merged_config.update(config)
            return merged_config
        
        return config
        
    except Exception as e:
        logger.error(f"Error loading configuration from {config_path}: {e}")
        if default_config:
            logger.info("Using default configuration due to loading error")
            return default_config.copy()
        raise


def save_config(config: Dict[str, Any], 
               config_path: Union[str, Path],
               format: str = 'yaml') -> bool:
    """
    Save configuration to a file.
    
    Args:
        config: Configuration dictionary to save
        config_path: Path to save configuration file
        format: File format ('yaml' or 'json')
        
    Returns:
        True if successful, False otherwise
    """
    config_path = Path(config_path)
    
    try:
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            if format.lower() in ['yaml', 'yml']:
                yaml.safe_dump(config, f, default_flow_style=False, indent=2)
            elif format.lower() == 'json':
                json.dump(config, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Successfully saved configuration to {config_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving configuration to {config_path}: {e}")
        return False


def validate_config(config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Validate configuration against a schema.
    
    Args:
        config: Configuration to validate
        schema: Validation schema
        
    Returns:
        True if valid, False otherwise
    """
    try:
        return _validate_dict_against_schema(config, schema)
    except Exception as e:
        logger.error(f"Configuration validation error: {e}")
        return False


def _validate_dict_against_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Recursively validate dictionary against schema."""
    
    for key, expected_type in schema.items():
        if key not in data:
            if isinstance(expected_type, dict) and 'required' in expected_type and expected_type['required']:
                logger.error(f"Required configuration key missing: {key}")
                return False
            continue
        
        value = data[key]
        
        if isinstance(expected_type, dict):
            if 'type' in expected_type:
                expected_python_type = _get_python_type(expected_type['type'])
                if not isinstance(value, expected_python_type):
                    logger.error(f"Configuration key '{key}' should be {expected_type['type']}, got {type(value).__name__}")
                    return False
            
            if 'min' in expected_type and isinstance(value, (int, float)) and value < expected_type['min']:
                logger.error(f"Configuration key '{key}' should be >= {expected_type['min']}, got {value}")
                return False
            
            if 'max' in expected_type and isinstance(value, (int, float)) and value > expected_type['max']:
                logger.error(f"Configuration key '{key}' should be <= {expected_type['max']}, got {value}")
                return False
            
            if 'choices' in expected_type and value not in expected_type['choices']:
                logger.error(f"Configuration key '{key}' should be one of {expected_type['choices']}, got {value}")
                return False
        
        elif isinstance(expected_type, type):
            if not isinstance(value, expected_type):
                logger.error(f"Configuration key '{key}' should be {expected_type.__name__}, got {type(value).__name__}")
                return False
    
    return True


def _get_python_type(type_string: str) -> type:
    """Convert string type name to Python type."""
    type_map = {
        'str': str,
        'string': str,
        'int': int,
        'integer': int,
        'float': float,
        'number': (int, float),
        'bool': bool,
        'boolean': bool,
        'list': list,
        'array': list,
        'dict': dict,
        'object': dict
    }
    
    return type_map.get(type_string.lower(), str)


def get_default_config() -> Dict[str, Any]:
    """Get default configuration for ROMA research agent."""
    return {
        'workflow': {
            'max_concurrent_files': 10,
            'max_concurrent_analysis': 5,
            'research_depth': 'medium',
            'max_results': 50
        },
        'logging': {
            'level': 'INFO',
            'log_file': None,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'file_processing': {
            'max_file_size_mb': 100,
            'supported_extensions': [
                '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml',
                '.yaml', '.yml', '.csv', '.log', '.rst', '.tex', '.sql',
                '.pdf', '.docx', '.xlsx'
            ],
            'exclude_patterns': [
                '*.pyc', '*.pyo', '*.pyd', '__pycache__/*', '.git/*',
                'node_modules/*', '*.log', '*.tmp', '.DS_Store'
            ]
        },
        'analysis': {
            'min_keyword_length': 3,
            'max_keywords_per_file': 20,
            'min_content_length': 10,
            'chunk_size': 1000,
            'chunk_overlap': 100
        },
        'research': {
            'min_confidence_threshold': 0.1,
            'max_findings_per_category': 10,
            'enable_entity_extraction': True,
            'enable_relationship_extraction': True
        }
    }


def get_config_schema() -> Dict[str, Any]:
    """Get configuration validation schema."""
    return {
        'workflow': {
            'type': 'dict',
            'required': False,
            'schema': {
                'max_concurrent_files': {'type': 'int', 'min': 1, 'max': 50},
                'max_concurrent_analysis': {'type': 'int', 'min': 1, 'max': 20},
                'research_depth': {'type': 'str', 'choices': ['shallow', 'medium', 'deep']},
                'max_results': {'type': 'int', 'min': 1, 'max': 1000}
            }
        },
        'logging': {
            'type': 'dict',
            'required': False,
            'schema': {
                'level': {'type': 'str', 'choices': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']},
                'log_file': {'type': 'str', 'required': False},
                'format': {'type': 'str'}
            }
        },
        'file_processing': {
            'type': 'dict',
            'required': False,
            'schema': {
                'max_file_size_mb': {'type': 'int', 'min': 1, 'max': 1000},
                'supported_extensions': {'type': 'list'},
                'exclude_patterns': {'type': 'list'}
            }
        },
        'analysis': {
            'type': 'dict',
            'required': False,
            'schema': {
                'min_keyword_length': {'type': 'int', 'min': 1, 'max': 10},
                'max_keywords_per_file': {'type': 'int', 'min': 1, 'max': 100},
                'min_content_length': {'type': 'int', 'min': 1},
                'chunk_size': {'type': 'int', 'min': 100, 'max': 10000},
                'chunk_overlap': {'type': 'int', 'min': 0, 'max': 1000}
            }
        },
        'research': {
            'type': 'dict',
            'required': False,
            'schema': {
                'min_confidence_threshold': {'type': 'float', 'min': 0.0, 'max': 1.0},
                'max_findings_per_category': {'type': 'int', 'min': 1, 'max': 100},
                'enable_entity_extraction': {'type': 'bool'},
                'enable_relationship_extraction': {'type': 'bool'}
            }
        }
    }


def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple configuration dictionaries.
    Later configs override earlier ones.
    
    Args:
        *configs: Configuration dictionaries to merge
        
    Returns:
        Merged configuration
    """
    merged = {}
    
    for config in configs:
        if not isinstance(config, dict):
            continue
            
        merged = _deep_merge_dicts(merged, config)
    
    return merged


def _deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two dictionaries."""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result