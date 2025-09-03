"""
LLM client for making API calls to OpenAI-compatible endpoints.
"""
import requests
import json
from typing import Dict, Any, Optional
from utils import get_model_config_by_name


class LLMClient:
    """Client for making requests to OpenAI-compatible LLM APIs."""
    
    def __init__(self):
        """Initialize the LLM client."""
        pass
    
    def generate_completion(
        self,
        model_name: str,
        prompt_text: str,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Generate completion using the specified model and parameters.
        
        Args:
            model_name (str): Name of the model from config.yaml
            prompt_text (str): The formatted prompt text to send
            temperature (float): Temperature parameter (0.0 to 2.0)
            max_tokens (int): Maximum tokens to generate
            top_p (float): Top-p parameter (0.0 to 1.0)
            timeout (int): Request timeout in seconds
            
        Returns:
            Dict[str, Any]: Response containing either success data or error information
        """
        try:
            # Get model configuration
            model_config = get_model_config_by_name(model_name)
            api_base = model_config["api_base"]
            api_key = model_config.get("api_key")
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json"
            }
            
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            # Prepare request payload for OpenAI-compatible API
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt_text
                    }
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p
            }
            
            # Construct API endpoint URL
            if api_base.endswith("/"):
                api_base = api_base.rstrip("/")
            
            endpoint_url = f"{api_base}/chat/completions"
            
            # Make the API request
            response = requests.post(
                endpoint_url,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            # Handle response
            if response.status_code == 200:
                response_data = response.json()
                
                # Extract the generated text
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    generated_text = response_data["choices"][0]["message"]["content"]
                    
                    return {
                        "success": True,
                        "generated_text": generated_text,
                        "model": model_name,
                        "usage": response_data.get("usage", {}),
                        "raw_response": response_data
                    }
                else:
                    return {
                        "success": False,
                        "error": "Invalid response format: no choices found",
                        "raw_response": response_data
                    }
            else:
                # Handle HTTP errors
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", {}).get("message", f"HTTP {response.status_code}")
                except:
                    error_message = f"HTTP {response.status_code}: {response.text}"
                
                return {
                    "success": False,
                    "error": f"API request failed: {error_message}",
                    "status_code": response.status_code
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": f"Request timed out after {timeout} seconds"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": f"Failed to connect to {api_base}. Please check if the model server is running."
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }
        except ValueError as e:
            return {
                "success": False,
                "error": f"Configuration error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def test_model_connection(self, model_name: str) -> Dict[str, Any]:
        """
        Test connection to a specific model with a simple prompt.
        
        Args:
            model_name (str): Name of the model to test
            
        Returns:
            Dict[str, Any]: Test result with success status and details
        """
        test_prompt = "Hello! Please respond with 'Connection successful' to confirm the API is working."
        
        result = self.generate_completion(
            model_name=model_name,
            prompt_text=test_prompt,
            temperature=0.1,
            max_tokens=50,
            top_p=1.0,
            timeout=10
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Successfully connected to {model_name}",
                "response": result["generated_text"]
            }
        else:
            return {
                "success": False,
                "message": f"Failed to connect to {model_name}",
                "error": result["error"]
            }


# Global LLM client instance
llm_client = LLMClient()


# Convenience functions
def generate_completion(
    model_name: str,
    prompt_text: str,
    temperature: float = 0.7,
    max_tokens: int = 256,
    top_p: float = 1.0
) -> Dict[str, Any]:
    """Generate completion using the global LLM client."""
    return llm_client.generate_completion(
        model_name, prompt_text, temperature, max_tokens, top_p
    )


def test_model_connection(model_name: str) -> Dict[str, Any]:
    """Test connection to a model using the global LLM client."""
    return llm_client.test_model_connection(model_name)