"""
GitLab Manager - Enhanced GitLab operations and automation library.

A Python wrapper around python-gitlab that provides simplified,
high-level operations for common GitLab workflows.
"""

from .client import GitLabClient
from .exceptions import (
    GitLabManagerError,
    AuthenticationError,
    ResourceNotFoundError,
    OperationError,
)

__version__ = "0.1.0"
__all__ = [
    "GitLabClient",
    "GitLabManagerError",
    "AuthenticationError",
    "ResourceNotFoundError",
    "OperationError",
]