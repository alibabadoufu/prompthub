"""
Main Gradio application for PromptFlow Studio.
"""
import gradio as gr
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import json

# Import our modules
import data_manager as dm
import llm_client as llm
from utils import load_config, extract_variables, format_prompt_template, validate_hyperparameters


class PromptFlowApp:
    """Main application class for PromptFlow Studio."""
    
    def __init__(self):
        """Initialize the application."""
        self.config = load_config()
        self.model_names = [model["name"] for model in self.config["models"]]
        
        # Initialize database
        dm.db_manager.setup_database()
    
    def get_project_choices(self) -> List[str]:
        """Get list of project names for dropdown."""
        projects = dm.get_projects()
        return [proj["name"] for proj in projects]
    
    def get_prompt_choices(self, project_name: str) -> List[str]:
        """Get list of prompt names for a project."""
        if not project_name:
            return []
        
        project = dm.get_project_by_name(project_name)
        if not project:
            return []
        
        prompts = dm.get_prompts(project["id"])
        return [prompt["name"] for prompt in prompts]
    
    def get_version_choices(self, project_name: str, prompt_name: str) -> List[str]:
        """Get list of version numbers for a prompt."""
        if not project_name or not prompt_name:
            return []
        
        project = dm.get_project_by_name(project_name)
        if not project:
            return []
        
        prompt = dm.get_prompt_by_name(project["id"], prompt_name)
        if not prompt:
            return []
        
        versions = dm.get_prompt_versions(prompt["id"])
        version_list = []
        for version in versions:
            active_marker = " (ACTIVE)" if version["is_active"] else ""
            version_list.append(f"v{version['version_number']}{active_marker}")
        
        return version_list
    
    def create_new_project(self, project_name: str, description: str) -> Tuple[str, gr.update]:
        """Create a new project."""
        if not project_name.strip():
            return "❌ Project name cannot be empty", gr.update()
        
        try:
            dm.create_project(project_name.strip(), description.strip())
            updated_choices = self.get_project_choices()
            return f"✅ Project '{project_name}' created successfully!", gr.update(choices=updated_choices, value=project_name)
        except ValueError as e:
            return f"❌ {str(e)}", gr.update()
    
    def create_new_prompt(self, project_name: str, prompt_name: str) -> Tuple[str, gr.update]:
        """Create a new prompt template."""
        if not project_name or not prompt_name.strip():
            return "❌ Please select a project and provide a prompt name", gr.update()
        
        project = dm.get_project_by_name(project_name)
        if not project:
            return "❌ Selected project not found", gr.update()
        
        try:
            dm.create_prompt(project["id"], prompt_name.strip())
            updated_choices = self.get_prompt_choices(project_name)
            return f"✅ Prompt '{prompt_name}' created successfully!", gr.update(choices=updated_choices, value=prompt_name)
        except ValueError as e:
            return f"❌ {str(e)}", gr.update()
    
    def load_prompt_version(
        self, 
        project_name: str, 
        prompt_name: str, 
        version_str: str
    ) -> Tuple[str, str, float, int, float, str, str]:
        """Load a specific prompt version into the UI."""
        if not all([project_name, prompt_name, version_str]):
            return "", "", 0.7, 256, 1.0, "", ""
        
        # Extract version number from string like "v3 (ACTIVE)"
        version_num = int(version_str.split()[0][1:])  # Remove 'v' prefix
        
        project = dm.get_project_by_name(project_name)
        if not project:
            return "", "", 0.7, 256, 1.0, "", ""
        
        prompt = dm.get_prompt_by_name(project["id"], prompt_name)
        if not prompt:
            return "", "", 0.7, 256, 1.0, "", ""
        
        version = dm.get_prompt_version(prompt["id"], version_num)
        if not version:
            return "", "", 0.7, 256, 1.0, "", ""
        
        return (
            version["template_text"],
            version["model_name"],
            version["temperature"],
            version["max_tokens"],
            version["top_p"],
            version.get("changelog", ""),
            self.generate_variable_inputs(version["template_text"])
        )
    
    def generate_variable_inputs(self, template_text: str) -> str:
        """Generate HTML for variable input fields based on template."""
        variables = extract_variables(template_text)
        if not variables:
            return "No variables found in this template."
        
        html_parts = ["<div style='margin: 10px 0;'><h4>Template Variables:</h4>"]
        for var in variables:
            html_parts.append(f"<p><strong>{var}:</strong> (Use the text input below to provide value)</p>")
        html_parts.append("</div>")
        
        return "\n".join(html_parts)
    
    def preview_formatted_prompt(
        self, 
        template_text: str, 
        variable_values: str
    ) -> str:
        """Generate preview of formatted prompt with variables filled in."""
        if not template_text:
            return "No template loaded."
        
        variables = extract_variables(template_text)
        if not variables:
            return template_text
        
        # Parse variable values (expecting JSON format or simple key=value pairs)
        try:
            if variable_values.strip().startswith("{"):
                # JSON format
                var_dict = json.loads(variable_values)
            else:
                # Simple key=value format, one per line
                var_dict = {}
                for line in variable_values.strip().split("\n"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        var_dict[key.strip()] = value.strip()
        except:
            return "❌ Invalid variable format. Use JSON format like: {\"var1\": \"value1\", \"var2\": \"value2\"} or key=value format (one per line)."
        
        # Check if all variables are provided
        missing_vars = [var for var in variables if var not in var_dict]
        if missing_vars:
            return f"❌ Missing values for variables: {', '.join(missing_vars)}"
        
        formatted_prompt = format_prompt_template(template_text, var_dict)
        return f"**Formatted Prompt:**\n\n{formatted_prompt}"
    
    def generate_response(
        self,
        project_name: str,
        prompt_name: str,
        template_text: str,
        model_name: str,
        temperature: float,
        max_tokens: int,
        top_p: float,
        variable_values: str
    ) -> str:
        """Generate LLM response using current settings."""
        if not all([template_text, model_name]):
            return "❌ Please load a prompt template and select a model."
        
        try:
            # Validate hyperparameters
            validate_hyperparameters(temperature, max_tokens, top_p)
            
            # Format prompt with variables
            variables = extract_variables(template_text)
            if variables:
                try:
                    if variable_values.strip().startswith("{"):
                        var_dict = json.loads(variable_values)
                    else:
                        var_dict = {}
                        for line in variable_values.strip().split("\n"):
                            if "=" in line:
                                key, value = line.split("=", 1)
                                var_dict[key.strip()] = value.strip()
                    
                    missing_vars = [var for var in variables if var not in var_dict]
                    if missing_vars:
                        return f"❌ Missing values for variables: {', '.join(missing_vars)}"
                    
                    formatted_prompt = format_prompt_template(template_text, var_dict)
                except Exception as e:
                    return f"❌ Error formatting prompt: {str(e)}"
            else:
                formatted_prompt = template_text
            
            # Generate completion
            result = llm.generate_completion(
                model_name=model_name,
                prompt_text=formatted_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p
            )
            
            if result["success"]:
                usage_info = ""
                if "usage" in result and result["usage"]:
                    usage = result["usage"]
                    usage_info = f"\n\n**Usage:** {usage.get('prompt_tokens', 0)} prompt tokens, {usage.get('completion_tokens', 0)} completion tokens"
                
                return f"**Model:** {model_name}\n**Response:**\n\n{result['generated_text']}{usage_info}"
            else:
                return f"❌ Generation failed: {result['error']}"
                
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def save_current_version(
        self,
        project_name: str,
        prompt_name: str,
        template_text: str,
        model_name: str,
        temperature: float,
        max_tokens: int,
        top_p: float,
        changelog: str
    ) -> Tuple[str, gr.update]:
        """Save current prompt settings as a new version."""
        if not all([project_name, prompt_name, template_text, model_name]):
            return "❌ Please ensure project, prompt, template, and model are all specified.", gr.update()
        
        try:
            # Validate hyperparameters
            validate_hyperparameters(temperature, max_tokens, top_p)
            
            project = dm.get_project_by_name(project_name)
            if not project:
                return "❌ Selected project not found.", gr.update()
            
            prompt = dm.get_prompt_by_name(project["id"], prompt_name)
            if not prompt:
                return "❌ Selected prompt not found.", gr.update()
            
            version_num = dm.save_prompt_version(
                prompt_id=prompt["id"],
                template_text=template_text,
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                changelog=changelog
            )
            
            updated_choices = self.get_version_choices(project_name, prompt_name)
            return f"✅ Saved as version {version_num}!", gr.update(choices=updated_choices, value=f"v{version_num}")
            
        except Exception as e:
            return f"❌ Error saving version: {str(e)}", gr.update()
    
    def set_version_active(
        self,
        project_name: str,
        prompt_name: str,
        version_str: str
    ) -> Tuple[str, gr.update]:
        """Set a version as active."""
        if not all([project_name, prompt_name, version_str]):
            return "❌ Please select project, prompt, and version.", gr.update()
        
        try:
            version_num = int(version_str.split()[0][1:])  # Extract number from "v3 (ACTIVE)"
            
            project = dm.get_project_by_name(project_name)
            prompt = dm.get_prompt_by_name(project["id"], prompt_name)
            
            dm.set_active_version(prompt["id"], version_num)
            
            updated_choices = self.get_version_choices(project_name, prompt_name)
            active_version = f"v{version_num} (ACTIVE)"
            
            return f"✅ Version {version_num} is now active!", gr.update(choices=updated_choices, value=active_version)
            
        except Exception as e:
            return f"❌ Error setting active version: {str(e)}", gr.update()
    
    def test_model(self, model_name: str) -> str:
        """Test connection to a model."""
        if not model_name:
            return "❌ Please select a model to test."
        
        result = llm.test_model_connection(model_name)
        
        if result["success"]:
            return f"✅ {result['message']}\nResponse: {result['response']}"
        else:
            return f"❌ {result['message']}\nError: {result['error']}"
    
    def get_api_response_preview(
        self,
        project_name: str,
        prompt_name: str,
        version: str = "active"
    ) -> str:
        """Preview what the API would return for given parameters."""
        if not project_name or not prompt_name:
            return "❌ Please specify both project and prompt name."
        
        try:
            # Convert version string to appropriate format
            if version.startswith("v"):
                version_param = version[1:].split()[0]  # Extract number from "v3 (ACTIVE)"
            else:
                version_param = "active"
            
            result = dm.get_prompt_details_for_api(project_name, prompt_name, version_param)
            
            if result:
                return f"**API Response Preview:**\n```json\n{json.dumps(result, indent=2)}\n```"
            else:
                return "❌ Prompt not found or no active version available."
                
        except Exception as e:
            return f"❌ Error: {str(e)}"


def create_interface():
    """Create and configure the Gradio interface."""
    app = PromptFlowApp()
    
    with gr.Blocks(title="PromptFlow Studio", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# 🚀 PromptFlow Studio")
        gr.Markdown("*Streamline your prompt engineering workflow with version control and testing capabilities.*")
        
        with gr.Tabs():
            # Main Playground Tab
            with gr.Tab("🎮 Playground"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("## Project & Prompt Selection")
                        
                        # Project management
                        with gr.Group():
                            gr.Markdown("### Projects")
                            project_dropdown = gr.Dropdown(
                                choices=app.get_project_choices(),
                                label="Select Project",
                                value=None,
                                interactive=True
                            )
                            
                            with gr.Row():
                                new_project_name = gr.Textbox(
                                    label="New Project Name",
                                    placeholder="e.g., CustomerSupportBot"
                                )
                                new_project_desc = gr.Textbox(
                                    label="Description (optional)",
                                    placeholder="Project description..."
                                )
                            
                            create_project_btn = gr.Button("Create Project", variant="secondary")
                            project_status = gr.Markdown("")
                        
                        # Prompt management
                        with gr.Group():
                            gr.Markdown("### Prompts")
                            prompt_dropdown = gr.Dropdown(
                                choices=[],
                                label="Select Prompt",
                                value=None,
                                interactive=True
                            )
                            
                            with gr.Row():
                                new_prompt_name = gr.Textbox(
                                    label="New Prompt Name",
                                    placeholder="e.g., SummarizationTask"
                                )
                                create_prompt_btn = gr.Button("Create Prompt", variant="secondary")
                            
                            prompt_status = gr.Markdown("")
                        
                        # Version management
                        with gr.Group():
                            gr.Markdown("### Versions")
                            version_dropdown = gr.Dropdown(
                                choices=[],
                                label="Select Version",
                                value=None,
                                interactive=True
                            )
                            
                            with gr.Row():
                                set_active_btn = gr.Button("Set as Active", variant="secondary")
                                version_status = gr.Markdown("")
                    
                    with gr.Column(scale=2):
                        gr.Markdown("## Prompt Engineering Workspace")
                        
                        # Model selection
                        model_dropdown = gr.Dropdown(
                            choices=app.model_names,
                            label="Select Model",
                            value=app.model_names[0] if app.model_names else None
                        )
                        
                        test_model_btn = gr.Button("Test Model Connection", variant="secondary")
                        model_test_result = gr.Markdown("")
                        
                        # Prompt template
                        template_textbox = gr.Textbox(
                            label="Prompt Template",
                            placeholder="Enter your prompt template here. Use {{variable_name}} for variables.",
                            lines=8,
                            max_lines=15
                        )
                        
                        # Hyperparameters
                        with gr.Row():
                            temperature_slider = gr.Slider(
                                minimum=0.0,
                                maximum=2.0,
                                step=0.1,
                                value=0.7,
                                label="Temperature"
                            )
                            max_tokens_slider = gr.Slider(
                                minimum=1,
                                maximum=4096,
                                step=1,
                                value=256,
                                label="Max Tokens"
                            )
                            top_p_slider = gr.Slider(
                                minimum=0.0,
                                maximum=1.0,
                                step=0.05,
                                value=1.0,
                                label="Top-p"
                            )
                        
                        # Variable inputs
                        variable_info = gr.HTML("")
                        variable_values = gr.Textbox(
                            label="Variable Values",
                            placeholder='Provide values in JSON format: {"variable1": "value1", "variable2": "value2"} or key=value format (one per line)',
                            lines=3
                        )
                        
                        # Prompt preview
                        with gr.Group():
                            gr.Markdown("### Prompt Preview")
                            preview_btn = gr.Button("Preview Formatted Prompt", variant="secondary")
                            prompt_preview = gr.Markdown("")
                        
                        # Generation
                        generate_btn = gr.Button("🎯 Generate Response", variant="primary", size="lg")
                        response_output = gr.Markdown("")
                        
                        # Save version
                        with gr.Group():
                            gr.Markdown("### Save New Version")
                            changelog_input = gr.Textbox(
                                label="Changelog",
                                placeholder="Describe what changed in this version...",
                                lines=2
                            )
                            save_version_btn = gr.Button("💾 Save Version", variant="primary")
                            save_status = gr.Markdown("")
            
            # API Tab
            with gr.Tab("🔌 API Access"):
                gr.Markdown("## API Endpoint Testing")
                gr.Markdown("Test the programmatic API that your applications will use to retrieve prompts.")
                
                with gr.Row():
                    with gr.Column():
                        api_project = gr.Textbox(label="Project Name", placeholder="CustomerSupportBot")
                        api_prompt = gr.Textbox(label="Prompt Name", placeholder="SummarizationTask")
                        api_version = gr.Textbox(label="Version (optional)", placeholder="active or version number")
                        
                        test_api_btn = gr.Button("Test API Call", variant="primary")
                    
                    with gr.Column():
                        api_result = gr.Markdown("")
                
                gr.Markdown("""
                ### API Usage
                
                **Endpoint:** `GET /api/get_prompt`
                
                **Parameters:**
                - `project_name` (required): Name of the project
                - `prompt_name` (required): Name of the prompt template
                - `version` (optional): Version number or "active" (default: "active")
                
                **Example:**
                ```
                GET /api/get_prompt?project_name=CustomerSupportBot&prompt_name=SummarizationTask&version=active
                ```
                """)
            
            # Management Tab
            with gr.Tab("📊 Management"):
                gr.Markdown("## Project & Prompt Overview")
                
                refresh_btn = gr.Button("🔄 Refresh Data", variant="secondary")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Projects")
                        projects_df = gr.Dataframe(
                            headers=["ID", "Name", "Description", "Created"],
                            datatype=["number", "str", "str", "str"],
                            interactive=False
                        )
                    
                    with gr.Column():
                        gr.Markdown("### Recent Activity")
                        activity_df = gr.Dataframe(
                            headers=["Project", "Prompt", "Version", "Model", "Created"],
                            datatype=["str", "str", "number", "str", "str"],
                            interactive=False
                        )
        
        # Event handlers
        def update_prompt_choices(project_name):
            choices = app.get_prompt_choices(project_name)
            return gr.update(choices=choices, value=None)
        
        def update_version_choices(project_name, prompt_name):
            choices = app.get_version_choices(project_name, prompt_name)
            return gr.update(choices=choices, value=None)
        
        def update_variable_display(template_text):
            return app.generate_variable_inputs(template_text)
        
        def refresh_management_data():
            # Get projects data
            projects = dm.get_projects()
            projects_data = [
                [proj["id"], proj["name"], proj.get("description", ""), proj["created_at"]]
                for proj in projects
            ]
            
            # Get recent activity (latest 20 versions across all projects)
            with dm.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        proj.name as project_name,
                        p.name as prompt_name,
                        pv.version_number,
                        pv.model_name,
                        pv.created_at
                    FROM prompt_versions pv
                    JOIN prompts p ON pv.prompt_id = p.id
                    JOIN projects proj ON p.project_id = proj.id
                    ORDER BY pv.created_at DESC
                    LIMIT 20
                """)
                activity_data = [
                    [row["project_name"], row["prompt_name"], row["version_number"], 
                     row["model_name"], row["created_at"]]
                    for row in cursor.fetchall()
                ]
            
            return gr.update(value=projects_data), gr.update(value=activity_data)
        
        # Wire up event handlers
        project_dropdown.change(
            fn=update_prompt_choices,
            inputs=[project_dropdown],
            outputs=[prompt_dropdown]
        )
        
        prompt_dropdown.change(
            fn=update_version_choices,
            inputs=[project_dropdown, prompt_dropdown],
            outputs=[version_dropdown]
        )
        
        template_textbox.change(
            fn=update_variable_display,
            inputs=[template_textbox],
            outputs=[variable_info]
        )
        
        version_dropdown.change(
            fn=app.load_prompt_version,
            inputs=[project_dropdown, prompt_dropdown, version_dropdown],
            outputs=[template_textbox, model_dropdown, temperature_slider, max_tokens_slider, top_p_slider, changelog_input, variable_info]
        )
        
        create_project_btn.click(
            fn=app.create_new_project,
            inputs=[new_project_name, new_project_desc],
            outputs=[project_status, project_dropdown]
        )
        
        create_prompt_btn.click(
            fn=app.create_new_prompt,
            inputs=[project_dropdown, new_prompt_name],
            outputs=[prompt_status, prompt_dropdown]
        )
        
        preview_btn.click(
            fn=app.preview_formatted_prompt,
            inputs=[template_textbox, variable_values],
            outputs=[prompt_preview]
        )
        
        generate_btn.click(
            fn=app.generate_response,
            inputs=[project_dropdown, prompt_dropdown, template_textbox, model_dropdown, 
                   temperature_slider, max_tokens_slider, top_p_slider, variable_values],
            outputs=[response_output]
        )
        
        save_version_btn.click(
            fn=app.save_current_version,
            inputs=[project_dropdown, prompt_dropdown, template_textbox, model_dropdown,
                   temperature_slider, max_tokens_slider, top_p_slider, changelog_input],
            outputs=[save_status, version_dropdown]
        )
        
        set_active_btn.click(
            fn=app.set_version_active,
            inputs=[project_dropdown, prompt_dropdown, version_dropdown],
            outputs=[version_status, version_dropdown]
        )
        
        test_model_btn.click(
            fn=app.test_model,
            inputs=[model_dropdown],
            outputs=[model_test_result]
        )
        
        test_api_btn.click(
            fn=app.get_api_response_preview,
            inputs=[api_project, api_prompt, api_version],
            outputs=[api_result]
        )
        
        refresh_btn.click(
            fn=refresh_management_data,
            inputs=[],
            outputs=[projects_df, activity_df]
        )
        
        # Load initial data
        interface.load(
            fn=refresh_management_data,
            inputs=[],
            outputs=[projects_df, activity_df]
        )
    
    return interface


# API endpoint function for Gradio's built-in API
def get_prompt_api(project_name: str, prompt_name: str, version: str = "active") -> Dict[str, Any]:
    """
    API endpoint function for retrieving prompt details.
    This function will be exposed via Gradio's API functionality.
    """
    result = dm.get_prompt_details_for_api(project_name, prompt_name, version)
    
    if result:
        return result
    else:
        return {
            "error": "Prompt not found",
            "project_name": project_name,
            "prompt_name": prompt_name,
            "version": version
        }


if __name__ == "__main__":
    # Create the interface
    demo = create_interface()
    
    # Add API endpoint
    demo.api_name = "get_prompt"
    
    # Launch the application
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )