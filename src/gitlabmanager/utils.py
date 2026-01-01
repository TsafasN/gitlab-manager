"""Utility functions for GitLab Manager."""

import os
from pathlib import Path
from typing import Optional


def get_token_from_env(var_name: str = "GITLAB_TOKEN") -> Optional[str]:
    """
    Get GitLab token from environment variable.
    
    Args:
        var_name: Name of the environment variable
        
    Returns:
        Token string or None if not found
    """
    return os.environ.get(var_name)


def validate_project_path(project_path: str) -> bool:
    """
    Validate GitLab project path format.
    
    Args:
        project_path: Project path (e.g., 'group/project')
        
    Returns:
        True if valid format
    """
    parts = project_path.split('/')
    return len(parts) >= 2 and all(part for part in parts)


def ensure_path_exists(path: str) -> Path:
    """
    Ensure a directory path exists.
    
    Args:
        path: Directory path to create
        
    Returns:
        Path object
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p