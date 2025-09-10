"""
File-based research tools for searching, listing, and reading files.
"""

import os
import re
import glob
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import subprocess
import mimetypes

from ..models.state import SearchResult


class FileSearchTool:
    """Advanced file search using grep and pattern matching."""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
    
    def grep_search(self, pattern: str, file_types: Optional[List[str]] = None, 
                   case_sensitive: bool = False, whole_word: bool = False,
                   context_lines: int = 2) -> List[SearchResult]:
        """Search for patterns in files using grep."""
        results = []
        
        # Build grep command
        cmd = ["grep", "-r", "-n"]  # recursive, line numbers
        
        if not case_sensitive:
            cmd.append("-i")
        if whole_word:
            cmd.append("-w")
        if context_lines > 0:
            cmd.extend(["-C", str(context_lines)])
            
        # Add file type filters
        if file_types:
            for file_type in file_types:
                cmd.extend(["--include", f"*.{file_type}"])
        
        cmd.extend([pattern, str(self.workspace_path)])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.workspace_path)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        results.append(self._parse_grep_line(line, pattern))
        except Exception as e:
            print(f"Grep search error: {e}")
            
        return results
    
    def regex_search(self, pattern: str, file_paths: List[str], 
                    flags: int = 0) -> List[SearchResult]:
        """Search for regex patterns in specific files."""
        results = []
        compiled_pattern = re.compile(pattern, flags)
        
        for file_path in file_paths:
            full_path = self.workspace_path / file_path
            if full_path.exists() and full_path.is_file():
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        matches = compiled_pattern.finditer(content)
                        
                        for match in matches:
                            # Get line number and context
                            line_start = content.rfind('\n', 0, match.start()) + 1
                            line_end = content.find('\n', match.end())
                            if line_end == -1:
                                line_end = len(content)
                            
                            line_content = content[line_start:line_end]
                            line_number = content[:match.start()].count('\n') + 1
                            
                            results.append(SearchResult(
                                source=str(file_path),
                                content=line_content,
                                relevance_score=0.8,
                                metadata={
                                    "line_number": line_number,
                                    "match_start": match.start() - line_start,
                                    "match_end": match.end() - line_start,
                                    "matched_text": match.group()
                                },
                                search_query=pattern,
                                tool_used="regex_search"
                            ))
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    
        return results
    
    def fuzzy_search(self, query: str, file_paths: List[str], 
                    threshold: float = 0.6) -> List[SearchResult]:
        """Fuzzy search for approximate matches."""
        results = []
        query_words = query.lower().split()
        
        for file_path in file_paths:
            full_path = self.workspace_path / file_path
            if full_path.exists() and full_path.is_file():
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        
                        for line_num, line in enumerate(lines, 1):
                            line_lower = line.lower()
                            matches = sum(1 for word in query_words if word in line_lower)
                            relevance = matches / len(query_words)
                            
                            if relevance >= threshold:
                                results.append(SearchResult(
                                    source=str(file_path),
                                    content=line.strip(),
                                    relevance_score=relevance,
                                    metadata={
                                        "line_number": line_num,
                                        "matched_words": matches,
                                        "total_words": len(query_words)
                                    },
                                    search_query=query,
                                    tool_used="fuzzy_search"
                                ))
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    
        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results
    
    def _parse_grep_line(self, line: str, pattern: str) -> SearchResult:
        """Parse a grep output line into a SearchResult."""
        parts = line.split(':', 2)
        if len(parts) >= 3:
            file_path = parts[0]
            line_number = parts[1]
            content = parts[2]
            
            return SearchResult(
                source=file_path,
                content=content.strip(),
                relevance_score=0.9,  # High relevance for exact matches
                metadata={
                    "line_number": int(line_number) if line_number.isdigit() else 0,
                    "grep_pattern": pattern
                },
                search_query=pattern,
                tool_used="grep_search"
            )
        
        # Fallback for malformed lines
        return SearchResult(
            source="unknown",
            content=line,
            relevance_score=0.5,
            metadata={},
            search_query=pattern,
            tool_used="grep_search"
        )


class FileListTool:
    """Tool for listing and discovering files in the workspace."""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
    
    def list_files(self, pattern: str = "*", recursive: bool = True, 
                  include_hidden: bool = False) -> List[str]:
        """List files matching a pattern."""
        if recursive:
            pattern = f"**/{pattern}"
        
        files = []
        try:
            for file_path in self.workspace_path.glob(pattern):
                if file_path.is_file():
                    rel_path = file_path.relative_to(self.workspace_path)
                    if include_hidden or not any(part.startswith('.') for part in rel_path.parts):
                        files.append(str(rel_path))
        except Exception as e:
            print(f"Error listing files: {e}")
            
        return sorted(files)
    
    def list_by_extension(self, extensions: List[str], 
                         exclude_dirs: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """List files grouped by extension."""
        if exclude_dirs is None:
            exclude_dirs = ['.git', '__pycache__', 'node_modules', '.venv']
            
        files_by_ext = {ext: [] for ext in extensions}
        
        for ext in extensions:
            pattern = f"**/*.{ext}"
            try:
                for file_path in self.workspace_path.glob(pattern):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(self.workspace_path)
                        # Check if file is in excluded directory
                        if not any(excluded in str(rel_path) for excluded in exclude_dirs):
                            files_by_ext[ext].append(str(rel_path))
            except Exception as e:
                print(f"Error listing {ext} files: {e}")
                
        return files_by_ext
    
    def find_related_files(self, file_path: str, similarity_types: List[str] = None) -> List[str]:
        """Find files related to the given file."""
        if similarity_types is None:
            similarity_types = ["same_dir", "same_name", "same_ext"]
            
        related_files = []
        target_path = Path(file_path)
        
        if "same_dir" in similarity_types:
            # Files in the same directory
            dir_pattern = str(target_path.parent / "*")
            related_files.extend(self.list_files(dir_pattern, recursive=False))
        
        if "same_name" in similarity_types:
            # Files with similar names
            name_pattern = f"**/{target_path.stem}*"
            related_files.extend(self.list_files(name_pattern))
        
        if "same_ext" in similarity_types:
            # Files with the same extension
            if target_path.suffix:
                ext_pattern = f"**/*{target_path.suffix}"
                related_files.extend(self.list_files(ext_pattern))
        
        # Remove duplicates and the original file
        related_files = list(set(related_files))
        if file_path in related_files:
            related_files.remove(file_path)
            
        return related_files
    
    def get_file_stats(self, file_paths: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get statistics for files."""
        stats = {}
        
        for file_path in file_paths:
            full_path = self.workspace_path / file_path
            if full_path.exists():
                try:
                    stat = full_path.stat()
                    mime_type, _ = mimetypes.guess_type(str(full_path))
                    
                    stats[file_path] = {
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                        "mime_type": mime_type,
                        "extension": full_path.suffix,
                        "is_text": self._is_text_file(full_path)
                    }
                except Exception as e:
                    stats[file_path] = {"error": str(e)}
                    
        return stats
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Check if a file is likely a text file."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' not in chunk
        except:
            return False


class FileReadTool:
    """Tool for reading and extracting content from files."""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
    
    def read_file(self, file_path: str, start_line: Optional[int] = None, 
                 end_line: Optional[int] = None) -> Optional[str]:
        """Read file content with optional line range."""
        full_path = self.workspace_path / file_path
        
        if not full_path.exists():
            return None
            
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                if start_line is None and end_line is None:
                    return f.read()
                
                lines = f.readlines()
                start_idx = (start_line - 1) if start_line else 0
                end_idx = end_line if end_line else len(lines)
                
                return ''.join(lines[start_idx:end_idx])
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def read_around_line(self, file_path: str, line_number: int, 
                        context: int = 5) -> Optional[str]:
        """Read content around a specific line number."""
        start_line = max(1, line_number - context)
        end_line = line_number + context
        return self.read_file(file_path, start_line, end_line)
    
    def extract_sections(self, file_path: str, 
                        section_markers: List[Tuple[str, str]]) -> Dict[str, str]:
        """Extract sections from a file based on start/end markers."""
        content = self.read_file(file_path)
        if not content:
            return {}
            
        sections = {}
        
        for start_marker, end_marker in section_markers:
            start_idx = content.find(start_marker)
            if start_idx != -1:
                end_idx = content.find(end_marker, start_idx + len(start_marker))
                if end_idx != -1:
                    section_name = f"{start_marker}...{end_marker}"
                    sections[section_name] = content[start_idx:end_idx + len(end_marker)]
                    
        return sections
    
    def get_file_structure(self, file_path: str) -> Dict[str, Any]:
        """Analyze file structure (functions, classes, etc.)."""
        content = self.read_file(file_path)
        if not content:
            return {}
            
        structure = {
            "functions": [],
            "classes": [],
            "imports": [],
            "comments": [],
            "line_count": len(content.split('\n'))
        }
        
        # Simple pattern matching for Python files
        if file_path.endswith('.py'):
            structure.update(self._analyze_python_structure(content))
        elif file_path.endswith(('.js', '.ts')):
            structure.update(self._analyze_javascript_structure(content))
            
        return structure
    
    def _analyze_python_structure(self, content: str) -> Dict[str, List[str]]:
        """Analyze Python file structure."""
        lines = content.split('\n')
        structure = {"functions": [], "classes": [], "imports": []}
        
        for line in lines:
            line = line.strip()
            if line.startswith('def '):
                func_name = line.split('(')[0].replace('def ', '')
                structure["functions"].append(func_name)
            elif line.startswith('class '):
                class_name = line.split('(')[0].split(':')[0].replace('class ', '')
                structure["classes"].append(class_name)
            elif line.startswith(('import ', 'from ')):
                structure["imports"].append(line)
                
        return structure
    
    def _analyze_javascript_structure(self, content: str) -> Dict[str, List[str]]:
        """Analyze JavaScript/TypeScript file structure."""
        lines = content.split('\n')
        structure = {"functions": [], "classes": [], "imports": []}
        
        for line in lines:
            line = line.strip()
            if 'function ' in line or '=>' in line:
                # Simple function detection
                if 'function ' in line:
                    func_name = line.split('function ')[1].split('(')[0].strip()
                    structure["functions"].append(func_name)
            elif line.startswith('class '):
                class_name = line.split(' ')[1].split(' ')[0].split('{')[0]
                structure["classes"].append(class_name)
            elif line.startswith(('import ', 'const ', 'let ', 'var ')) and 'require(' in line:
                structure["imports"].append(line)
                
        return structure