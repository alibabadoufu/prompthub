# 🚀 PromptFlow Studio

PromptFlow Studio is a comprehensive web-based tool built with Python and Gradio for streamlining the prompt engineering lifecycle. It provides a centralized platform for teams to create, version, test, and manage prompts for various Large Language Models (LLMs) with OpenAI-compatible APIs.

## ✨ Features

- **Project Management**: Organize prompts into logical projects
- **Version Control**: Track changes and maintain stable prompt versions
- **Interactive Testing**: Real-time prompt testing with variable substitution
- **Multi-Model Support**: Work with multiple LLMs through OpenAI-compatible APIs
- **API Access**: Programmatic access to prompts for integration with other applications
- **Variable Templates**: Support for Jinja2-style variable substitution (`{{variable_name}}`)
- **Hyperparameter Tuning**: Adjust temperature, max_tokens, and top_p in real-time

## 🏗️ Project Structure

```
promptflow-studio/
├── app.py                 # Main Gradio application
├── data_manager.py        # Database operations (SQLite)
├── llm_client.py          # LLM API client
├── utils.py               # Helper functions
├── config.yaml            # Model configurations
├── requirements.txt       # Python dependencies
├── install.sh             # Automatic installation script
├── launch.sh              # Application launch script
├── demo_setup.py          # Demo data creation script
├── test_system.py         # System verification tests
├── prompt_studio.db       # SQLite database (created on first run)
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Installation

**Option A: Automatic Installation (Recommended)**
```bash
# Clone or download the project
cd promptflow-studio

# Run the installation script
./install.sh
```

**Option B: Manual Installation**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run system tests
python test_system.py

# Set up demo data (optional)
python demo_setup.py
```

### 2. Configuration

Edit `config.yaml` to configure your LLM endpoints:

```yaml
database_path: "prompt_studio.db"

models:
  - name: "Llama3 8B (Internal)"
    api_base: "http://192.168.1.100:8080/v1"
    # api_key: "optional-key-if-needed"
  - name: "GPT-4 (OpenAI)"
    api_base: "https://api.openai.com/v1"
    api_key: "your-openai-api-key"
```

### 3. Launch the Application

**Option A: Using Launch Script (Recommended)**
```bash
./launch.sh
```

**Option B: Manual Launch**
```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Start the application
python app.py
```

The application will be available at `http://localhost:7860`

## 📖 Usage Guide

### Creating Projects and Prompts

1. **Create a Project**: Use the "Projects" section to create a new project (e.g., "CustomerSupportBot")
2. **Create Prompts**: Within a project, create prompt templates (e.g., "SummarizationTask")
3. **Add Variables**: Use `{{variable_name}}` syntax in your prompts for dynamic content

### Working with Templates

Example prompt template:
```
Please summarize the following customer complaint in 3 bullet points:

{{user_complaint}}

Focus on:
- Main issue
- Customer sentiment
- Suggested resolution
```

### Variable Input Formats

You can provide variable values in two formats:

**JSON Format:**
```json
{"user_complaint": "The product arrived damaged and customer service was unhelpful."}
```

**Key-Value Format:**
```
user_complaint=The product arrived damaged and customer service was unhelpful.
priority=high
```

### Version Management

- Each prompt can have multiple versions
- Save new versions when you modify the template, model, or hyperparameters
- Set one version as "active" for production use
- Add changelog messages to track what changed

### API Integration

Access prompts programmatically via the built-in API:

```python
import requests

# Get active version
response = requests.get(
    "http://localhost:7860/api/get_prompt",
    params={
        "project_name": "CustomerSupportBot",
        "prompt_name": "SummarizationTask",
        "version": "active"
    }
)

prompt_data = response.json()
print(prompt_data["prompt_template"])
```

## 🔧 API Reference

### GET /api/get_prompt

Retrieve prompt details for programmatic use.

**Parameters:**
- `project_name` (string, required): Project name
- `prompt_name` (string, required): Prompt template name  
- `version` (string, optional): Version number or "active" (default: "active")

**Response Format:**
```json
{
  "project_name": "CustomerSupportBot",
  "prompt_name": "SummarizationTask", 
  "version": 5,
  "is_active": true,
  "model": "internal-llama3-70b",
  "prompt_template": "Please summarize the following customer complaint in 3 bullet points:\n\n{{user_complaint}}",
  "hyperparameters": {
    "temperature": 0.5,
    "max_tokens": 256,
    "top_p": 0.95
  }
}
```

## 🛠️ Advanced Configuration

### Adding New Models

Add models to `config.yaml`:

```yaml
models:
  - name: "Your Custom Model"
    api_base: "http://your-server:8080/v1"
    api_key: "optional-api-key"
```

### Database Customization

Change the database path in `config.yaml`:

```yaml
database_path: "/path/to/your/database.db"
```

## 🔍 Troubleshooting

### Common Issues

1. **Model Connection Failed**: 
   - Check if the model server is running
   - Verify the API base URL in `config.yaml`
   - Test the connection using the "Test Model Connection" button

2. **Database Errors**:
   - Ensure write permissions in the application directory
   - Check if `prompt_studio.db` can be created/accessed

3. **Variable Substitution Issues**:
   - Ensure variable names match exactly (case-sensitive)
   - Use proper JSON format or key=value format for variable values

### Logs and Debugging

The application runs with debug mode enabled. Check the console output for detailed error messages.

## 🤝 Contributing

This is an internal tool. For feature requests or bug reports, please contact the development team.

## 📄 License

Internal use only. See LICENSE file for details.