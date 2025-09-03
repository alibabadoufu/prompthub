"""
Utility functions for PromptFlow Studio.
"""
import re
import yaml
from typing import List, Dict, Any


def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml file."""
    try:
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        raise FileNotFoundError("config.yaml file not found. Please ensure it exists in the project root.")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing config.yaml: {e}")


def extract_variables(template_text: str) -> List[str]:
    """
    Extract variable names from Jinja2-style template text.
    
    Args:
        template_text (str): The prompt template containing variables like {{variable_name}}
        
    Returns:
        List[str]: List of unique variable names found in the template
    """
    if not template_text:
        return []
    
    # Pattern to match {{variable_name}} with optional whitespace
    pattern = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}'
    matches = re.findall(pattern, template_text)
    
    # Return unique variables while preserving order
    seen = set()
    unique_variables = []
    for var in matches:
        if var not in seen:
            seen.add(var)
            unique_variables.append(var)
    
    return unique_variables


def format_prompt_template(template: str, variables: Dict[str, str]) -> str:
    """
    Format a prompt template with provided variables using Jinja2-style substitution.
    
    Args:
        template (str): The prompt template with {{variable}} placeholders
        variables (Dict[str, str]): Dictionary mapping variable names to their values
        
    Returns:
        str: The formatted prompt with variables substituted
    """
    formatted_prompt = template
    
    for var_name, var_value in variables.items():
        placeholder = "{{" + var_name + "}}"
        # Also handle variations with whitespace
        placeholder_pattern = r'\{\{\s*' + re.escape(var_name) + r'\s*\}\}'
        formatted_prompt = re.sub(placeholder_pattern, str(var_value), formatted_prompt)
    
    return formatted_prompt


def validate_hyperparameters(temperature: float, max_tokens: int, top_p: float) -> Dict[str, Any]:
    """
    Validate and normalize hyperparameters.
    
    Args:
        temperature (float): Temperature value (0.0 to 2.0)
        max_tokens (int): Maximum tokens (1 to 4096)
        top_p (float): Top-p value (0.0 to 1.0)
        
    Returns:
        Dict[str, Any]: Validated hyperparameters
        
    Raises:
        ValueError: If any parameter is out of valid range
    """
    if not (0.0 <= temperature <= 2.0):
        raise ValueError("Temperature must be between 0.0 and 2.0")
    
    if not (1 <= max_tokens <= 4096):
        raise ValueError("Max tokens must be between 1 and 4096")
    
    if not (0.0 <= top_p <= 1.0):
        raise ValueError("Top-p must be between 0.0 and 1.0")
    
    return {
        "temperature": float(temperature),
        "max_tokens": int(max_tokens),
        "top_p": float(top_p)
    }


def get_model_config_by_name(model_name: str) -> Dict[str, Any]:
    """
    Get model configuration by name from config.yaml.
    
    Args:
        model_name (str): Name of the model to retrieve
        
    Returns:
        Dict[str, Any]: Model configuration including api_base and api_key
        
    Raises:
        ValueError: If model not found in configuration
    """
    config = load_config()
    
    for model in config.get("models", []):
        if model["name"] == model_name:
            return model
    
    raise ValueError(f"Model '{model_name}' not found in configuration")