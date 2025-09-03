"""
Database operations for PromptFlow Studio.
Handles all CRUD operations for projects, prompts, and versions.
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from utils import load_config


class DatabaseManager:
    """Manages SQLite database operations for PromptFlow Studio."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database manager with optional custom database path."""
        if db_path is None:
            config = load_config()
            db_path = config.get("database_path", "prompt_studio.db")
        
        self.db_path = db_path
        self.setup_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory for dict-like access."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def setup_database(self) -> None:
        """Create database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Projects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Prompts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                    UNIQUE(project_id, name)
                )
            """)
            
            # Prompt versions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompt_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id INTEGER NOT NULL,
                    version_number INTEGER NOT NULL,
                    template_text TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    temperature REAL NOT NULL DEFAULT 0.7,
                    max_tokens INTEGER NOT NULL DEFAULT 256,
                    top_p REAL NOT NULL DEFAULT 1.0,
                    changelog TEXT,
                    is_active BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (prompt_id) REFERENCES prompts (id) ON DELETE CASCADE,
                    UNIQUE(prompt_id, version_number)
                )
            """)
            
            conn.commit()
    
    # Project operations
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    def create_project(self, name: str, description: str = "") -> int:
        """
        Create a new project.
        
        Args:
            name (str): Unique project name
            description (str): Optional project description
            
        Returns:
            int: The ID of the created project
            
        Raises:
            ValueError: If project name already exists
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO projects (name, description) VALUES (?, ?)",
                    (name, description)
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                raise ValueError(f"Project '{name}' already exists")
    
    def get_project_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get project by name."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE name = ?", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # Prompt operations
    def get_prompts(self, project_id: int) -> List[Dict[str, Any]]:
        """Get all prompts for a project."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, 
                       COUNT(pv.id) as version_count,
                       MAX(pv.version_number) as latest_version
                FROM prompts p
                LEFT JOIN prompt_versions pv ON p.id = pv.prompt_id
                WHERE p.project_id = ?
                GROUP BY p.id
                ORDER BY p.name
            """, (project_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def create_prompt(self, project_id: int, name: str) -> int:
        """
        Create a new prompt template.
        
        Args:
            project_id (int): ID of the parent project
            name (str): Name of the prompt template
            
        Returns:
            int: The ID of the created prompt
            
        Raises:
            ValueError: If prompt name already exists in the project
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO prompts (project_id, name) VALUES (?, ?)",
                    (project_id, name)
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                raise ValueError(f"Prompt '{name}' already exists in this project")
    
    def get_prompt_by_name(self, project_id: int, prompt_name: str) -> Optional[Dict[str, Any]]:
        """Get prompt by name within a project."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM prompts WHERE project_id = ? AND name = ?",
                (project_id, prompt_name)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # Prompt version operations
    def get_prompt_versions(self, prompt_id: int) -> List[Dict[str, Any]]:
        """Get all versions of a prompt, ordered by version number descending."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM prompt_versions 
                WHERE prompt_id = ? 
                ORDER BY version_number DESC
            """, (prompt_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def save_prompt_version(
        self,
        prompt_id: int,
        template_text: str,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        changelog: str = ""
    ) -> int:
        """
        Save a new version of a prompt.
        
        Args:
            prompt_id (int): ID of the prompt
            template_text (str): The prompt template text
            model_name (str): Name of the target model
            temperature (float): Temperature parameter
            max_tokens (int): Maximum tokens parameter
            top_p (float): Top-p parameter
            changelog (str): Description of changes in this version
            
        Returns:
            int: The version number of the created version
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get the next version number
            cursor.execute(
                "SELECT COALESCE(MAX(version_number), 0) + 1 FROM prompt_versions WHERE prompt_id = ?",
                (prompt_id,)
            )
            version_number = cursor.fetchone()[0]
            
            # Insert new version
            cursor.execute("""
                INSERT INTO prompt_versions 
                (prompt_id, version_number, template_text, model_name, temperature, max_tokens, top_p, changelog)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (prompt_id, version_number, template_text, model_name, temperature, max_tokens, top_p, changelog))
            
            conn.commit()
            return version_number
    
    def set_active_version(self, prompt_id: int, version_number: int) -> None:
        """
        Set a specific version as the active version for a prompt.
        
        Args:
            prompt_id (int): ID of the prompt
            version_number (int): Version number to set as active
            
        Raises:
            ValueError: If version doesn't exist
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if version exists
            cursor.execute(
                "SELECT id FROM prompt_versions WHERE prompt_id = ? AND version_number = ?",
                (prompt_id, version_number)
            )
            if not cursor.fetchone():
                raise ValueError(f"Version {version_number} not found for prompt ID {prompt_id}")
            
            # Deactivate all versions for this prompt
            cursor.execute(
                "UPDATE prompt_versions SET is_active = FALSE WHERE prompt_id = ?",
                (prompt_id,)
            )
            
            # Activate the specified version
            cursor.execute(
                "UPDATE prompt_versions SET is_active = TRUE WHERE prompt_id = ? AND version_number = ?",
                (prompt_id, version_number)
            )
            
            conn.commit()
    
    def get_active_version(self, prompt_id: int) -> Optional[Dict[str, Any]]:
        """Get the active version of a prompt."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM prompt_versions 
                WHERE prompt_id = ? AND is_active = TRUE
            """, (prompt_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_prompt_version(self, prompt_id: int, version_number: int) -> Optional[Dict[str, Any]]:
        """Get a specific version of a prompt."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM prompt_versions 
                WHERE prompt_id = ? AND version_number = ?
            """, (prompt_id, version_number))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_prompt_details_for_api(
        self, 
        project_name: str, 
        prompt_name: str, 
        version: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get prompt details for API access.
        
        Args:
            project_name (str): Name of the project
            prompt_name (str): Name of the prompt
            version (Optional[str]): Version number or "active". If None, returns active version.
            
        Returns:
            Optional[Dict[str, Any]]: Prompt details or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get project ID
            cursor.execute("SELECT id FROM projects WHERE name = ?", (project_name,))
            project_row = cursor.fetchone()
            if not project_row:
                return None
            
            project_id = project_row[0]
            
            # Get prompt ID
            cursor.execute(
                "SELECT id FROM prompts WHERE project_id = ? AND name = ?",
                (project_id, prompt_name)
            )
            prompt_row = cursor.fetchone()
            if not prompt_row:
                return None
            
            prompt_id = prompt_row[0]
            
            # Get version details
            if version is None or version == "active":
                # Get active version
                cursor.execute("""
                    SELECT * FROM prompt_versions 
                    WHERE prompt_id = ? AND is_active = TRUE
                """, (prompt_id,))
            else:
                # Get specific version
                try:
                    version_num = int(version)
                    cursor.execute("""
                        SELECT * FROM prompt_versions 
                        WHERE prompt_id = ? AND version_number = ?
                    """, (prompt_id, version_num))
                except ValueError:
                    return None
            
            version_row = cursor.fetchone()
            if not version_row:
                return None
            
            # Format response
            return {
                "project_name": project_name,
                "prompt_name": prompt_name,
                "version": version_row["version_number"],
                "is_active": bool(version_row["is_active"]),
                "model": version_row["model_name"],
                "prompt_template": version_row["template_text"],
                "hyperparameters": {
                    "temperature": version_row["temperature"],
                    "max_tokens": version_row["max_tokens"],
                    "top_p": version_row["top_p"]
                }
            }
    
    def get_latest_version_number(self, prompt_id: int) -> int:
        """Get the latest version number for a prompt."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COALESCE(MAX(version_number), 0) FROM prompt_versions WHERE prompt_id = ?",
                (prompt_id,)
            )
            return cursor.fetchone()[0]
    
    def delete_project(self, project_id: int) -> None:
        """Delete a project and all its associated prompts and versions."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            conn.commit()
    
    def delete_prompt(self, prompt_id: int) -> None:
        """Delete a prompt and all its versions."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
            conn.commit()
    
    def search_prompts(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for prompts by name or template content.
        
        Args:
            search_term (str): Term to search for
            
        Returns:
            List[Dict[str, Any]]: List of matching prompts with project info
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    proj.name as project_name,
                    p.name as prompt_name,
                    p.id as prompt_id,
                    pv.version_number,
                    pv.template_text,
                    pv.is_active
                FROM projects proj
                JOIN prompts p ON proj.id = p.project_id
                JOIN prompt_versions pv ON p.id = pv.prompt_id
                WHERE p.name LIKE ? OR pv.template_text LIKE ?
                ORDER BY proj.name, p.name, pv.version_number DESC
            """, (f"%{search_term}%", f"%{search_term}%"))
            
            return [dict(row) for row in cursor.fetchall()]


# Global database manager instance
db_manager = DatabaseManager()


# Convenience functions that use the global instance
def get_projects() -> List[Dict[str, Any]]:
    """Get all projects."""
    return db_manager.get_projects()


def create_project(name: str, description: str = "") -> int:
    """Create a new project."""
    return db_manager.create_project(name, description)


def get_project_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get project by name."""
    return db_manager.get_project_by_name(name)


def get_prompts(project_id: int) -> List[Dict[str, Any]]:
    """Get all prompts for a project."""
    return db_manager.get_prompts(project_id)


def create_prompt(project_id: int, name: str) -> int:
    """Create a new prompt template."""
    return db_manager.create_prompt(project_id, name)


def get_prompt_by_name(project_id: int, prompt_name: str) -> Optional[Dict[str, Any]]:
    """Get prompt by name within a project."""
    return db_manager.get_prompt_by_name(project_id, prompt_name)


def get_prompt_versions(prompt_id: int) -> List[Dict[str, Any]]:
    """Get all versions of a prompt."""
    return db_manager.get_prompt_versions(prompt_id)


def save_prompt_version(
    prompt_id: int,
    template_text: str,
    model_name: str,
    temperature: float = 0.7,
    max_tokens: int = 256,
    top_p: float = 1.0,
    changelog: str = ""
) -> int:
    """Save a new version of a prompt."""
    return db_manager.save_prompt_version(
        prompt_id, template_text, model_name, temperature, max_tokens, top_p, changelog
    )


def set_active_version(prompt_id: int, version_number: int) -> None:
    """Set a specific version as active."""
    return db_manager.set_active_version(prompt_id, version_number)


def get_active_version(prompt_id: int) -> Optional[Dict[str, Any]]:
    """Get the active version of a prompt."""
    return db_manager.get_active_version(prompt_id)


def get_prompt_version(prompt_id: int, version_number: int) -> Optional[Dict[str, Any]]:
    """Get a specific version of a prompt."""
    return db_manager.get_prompt_version(prompt_id, version_number)


def get_prompt_details_for_api(
    project_name: str, 
    prompt_name: str, 
    version: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Get prompt details for API access."""
    return db_manager.get_prompt_details_for_api(project_name, prompt_name, version)