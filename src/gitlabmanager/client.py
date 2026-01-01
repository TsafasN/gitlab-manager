"""Main client class for GitLab Manager."""

import gitlab
from typing import Optional
from .exceptions import AuthenticationError, GitLabManagerError
from .packages import PackageManager
from .releases import ReleaseManager
from .pipelines import PipelineManager
from .repositories import RepositoryManager


class GitLabClient:
    """
    Enhanced GitLab client with simplified operations.
    
    This client wraps python-gitlab and provides high-level operations
    for common GitLab workflows like package management, releases,
    CI/CD pipelines, and repository operations.
    
    Args:
        url: GitLab instance URL (e.g., 'https://gitlab.com')
        private_token: Personal access token for authentication
        oauth_token: OAuth token for authentication (alternative to private_token)
        job_token: CI job token for authentication (alternative to private_token)
        ssl_verify: Enable/disable SSL certificate verification
        
    Example:
        >>> client = GitLabClient('https://gitlab.com', private_token='your-token')
        >>> client.packages.upload('myproject', 'package.tar.gz')
        >>> client.releases.create('myproject', 'v1.0.0', 'Release notes')
    """
    
    def __init__(
        self,
        url: str = "https://gitlab.com",
        private_token: Optional[str] = None,
        oauth_token: Optional[str] = None,
        job_token: Optional[str] = None,
        ssl_verify: bool = True,
    ):
        """Initialize the GitLab Manager client."""
        try:
            self._gl = gitlab.Gitlab(
                url=url,
                private_token=private_token,
                oauth_token=oauth_token,
                job_token=job_token,
                ssl_verify=ssl_verify,
            )
            # Authenticate to verify credentials
            self._gl.auth()
        except gitlab.exceptions.GitlabAuthenticationError as e:
            raise AuthenticationError(f"Failed to authenticate with GitLab: {e}")
        except Exception as e:
            raise GitLabManagerError(f"Failed to initialize GitLab client: {e}")
        
        # Initialize operation managers
        self._packages = PackageManager(self._gl)
        self._releases = ReleaseManager(self._gl)
        self._pipelines = PipelineManager(self._gl)
        self._repositories = RepositoryManager(self._gl)
    
    @property
    def packages(self) -> PackageManager:
        """Access package operations."""
        return self._packages
    
    @property
    def releases(self) -> ReleaseManager:
        """Access release operations."""
        return self._releases
    
    @property
    def pipelines(self) -> PipelineManager:
        """Access pipeline operations."""
        return self._pipelines
    
    @property
    def repositories(self) -> RepositoryManager:
        """Access repository operations."""
        return self._repositories
    
    @property
    def gitlab(self) -> gitlab.Gitlab:
        """
        Access the underlying python-gitlab client.
        
        Use this for operations not yet wrapped by GitLab Manager.
        """
        return self._gl
    
    def get_project(self, project_id):
        """
        Get a project by ID or path.
        
        Args:
            project_id: Project ID (int) or path (str) like 'group/project'
            
        Returns:
            Project object
        """
        return self._gl.projects.get(project_id)