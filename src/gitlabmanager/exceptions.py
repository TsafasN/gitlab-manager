"""Custom exceptions for GitLab Manager."""


class GitLabManagerError(Exception):
    """Base exception for all GitLab Manager errors."""
    pass


class AuthenticationError(GitLabManagerError):
    """Raised when authentication with GitLab fails."""
    pass


class ResourceNotFoundError(GitLabManagerError):
    """Raised when a requested resource is not found."""
    pass


class OperationError(GitLabManagerError):
    """Raised when a GitLab operation fails."""
    pass


class ValidationError(GitLabManagerError):
    """Raised when input validation fails."""
    pass