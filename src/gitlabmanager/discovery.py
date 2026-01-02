"""Project discovery and search functionality."""

import gitlab
from typing import List, Dict, Any, Optional
from .exceptions import OperationError


class ProjectDiscovery:
    """
    Discover and search for projects in a GitLab instance.
    
    This helps solve the pain point of "remembering project paths"
    by providing easy ways to find and list projects.
    """
    
    def __init__(self, gl: gitlab.Gitlab):
        """Initialize project discovery."""
        self._gl = gl
    
    def list_all(
        self,
        owned: bool = False,
        starred: bool = False,
        archived: bool = False,
        visibility: Optional[str] = None,
        order_by: str = "last_activity_at",
        sort: str = "desc",
        simple: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        List all projects you have access to.
        
        Args:
            owned: Only projects owned by you
            starred: Only starred projects
            archived: Include archived projects
            visibility: Filter by visibility ('public', 'internal', 'private')
            order_by: Sort by field ('id', 'name', 'path', 'created_at', 
                     'updated_at', 'last_activity_at')
            sort: Sort direction ('asc' or 'desc')
            simple: Return simplified project info (faster)
            
        Returns:
            List of project dictionaries
            
        Example:
            >>> # List all your projects
            >>> projects = client.projects.discover.list_all()
            >>> for p in projects:
            ...     print(f"{p['path_with_namespace']}")
            
            >>> # List only your owned projects
            >>> my_projects = client.projects.discover.list_all(owned=True)
            
            >>> # List starred projects
            >>> starred = client.projects.discover.list_all(starred=True)
        """
        try:
            print("Debug: Fetching all projects with specified filters")

            projects = self._gl.projects.list(
                owned=True, 
                get_all=True
            )

            print(f"Debug: Retrieved {len(projects)} projects from GitLab")
            
            for p in projects:
                print(f"Debug: Checking project {p.path_with_namespace}")

            return [self._project_to_dict(p, simple) for p in projects]
            
        except Exception as e:
            raise OperationError(f"Failed to list projects: {e}") from e
    
    def search(
        self,
        query: str,
        search_in: str = "name",
        order_by: str = "last_activity_at",
        sort: str = "desc",
    ) -> List[Dict[str, Any]]:
        """
        Search for projects by name, description, or path.
        
        Args:
            query: Search query string
            search_in: Where to search ('name', 'path', 'description')
            order_by: Sort by field
            sort: Sort direction ('asc' or 'desc')
            
        Returns:
            List of matching project dictionaries
            
        Example:
            >>> # Search by name
            >>> results = client.projects.discover.search('docker')
            >>> 
            >>> # Search in path
            >>> results = client.projects.discover.search(
            ...     'mygroup',
            ...     search_in='path'
            ... )
        """
        try:
            projects = self._gl.projects.list(
                search=query,
                order_by=order_by,
                sort=sort,
                get_all=True,
            )
            
            results = []
            query_lower = query.lower()
            
            for p in projects:
                # Additional filtering based on search_in
                if search_in == "name" and query_lower in p.name.lower():
                    results.append(self._project_to_dict(p))
                elif search_in == "path" and query_lower in p.path_with_namespace.lower():
                    results.append(self._project_to_dict(p))
                elif search_in == "description":
                    desc = getattr(p, 'description', '') or ''
                    if query_lower in desc.lower():
                        results.append(self._project_to_dict(p))
                elif search_in not in ["name", "path", "description"]:
                    # Default: include if matches anything
                    results.append(self._project_to_dict(p))
            
            return results
            
        except Exception as e:
            raise OperationError(f"Failed to search projects: {e}") from e
    
    def by_namespace(
        self,
        namespace: str,
        order_by: str = "name",
        sort: str = "asc",
    ) -> List[Dict[str, Any]]:
        """
        Get all projects in a specific namespace/group.
        
        Args:
            namespace: Namespace or group name (e.g., 'mygroup')
            order_by: Sort by field
            sort: Sort direction
            
        Returns:
            List of projects in the namespace
            
        Example:
            >>> # Get all projects in a group
            >>> projects = client.projects.discover.by_namespace('mygroup')
            >>> for p in projects:
            ...     print(p['name'])
        """
        try:
            # Search by namespace in path
            all_projects = self._gl.projects.list(
                order_by=order_by,
                sort=sort,
                get_all=True,
            )
            
            namespace_lower = namespace.lower()
            results = []
            
            for p in all_projects:
                # Check if namespace matches
                project_namespace = p.namespace.get('path', '').lower()
                if project_namespace == namespace_lower:
                    results.append(self._project_to_dict(p))
                # Also check if it's nested (e.g., 'group/subgroup')
                elif p.path_with_namespace.lower().startswith(namespace_lower + '/'):
                    results.append(self._project_to_dict(p))
            
            return results
            
        except Exception as e:
            raise OperationError(f"Failed to get projects by namespace: {e}") from e
    
    def by_topic(
        self,
        topic: str,
    ) -> List[Dict[str, Any]]:
        """
        Find projects by topic/tag.
        
        Args:
            topic: Topic/tag name
            
        Returns:
            List of projects with that topic
            
        Example:
            >>> # Find all Docker-related projects
            >>> docker_projects = client.projects.discover.by_topic('docker')
        """
        try:
            projects = self._gl.projects.list(
                topic=topic,
                get_all=True,
            )
            
            return [self._project_to_dict(p) for p in projects]
            
        except Exception as e:
            raise OperationError(f"Failed to search by topic: {e}") from e
    
    def get_project_info(
        self,
        project_id_or_path: str,
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific project.
        
        Args:
            project_id_or_path: Project ID (int) or path ('group/project')
            
        Returns:
            Detailed project information
            
        Example:
            >>> info = client.projects.discover.get_project_info('mygroup/myproject')
            >>> print(f"ID: {info['id']}")
            >>> print(f"URL: {info['web_url']}")
        """
        try:
            project = self._gl.projects.get(project_id_or_path)
            return self._project_to_dict(project, simple=False, detailed=True)
            
        except gitlab.exceptions.GitlabGetError as e:
            raise OperationError(f"Project not found: {project_id_or_path}") from e
    
    def list_with_packages(
        self,
        min_packages: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        List projects that have packages.
        
        Args:
            min_packages: Minimum number of packages required
            
        Returns:
            List of projects with packages
            
        Example:
            >>> # Find projects with packages
            >>> projects_with_packages = client.projects.discover.list_with_packages()
        """
        try:
            all_projects = self._gl.projects.list(get_all=True)
            results = []
            
            for p in all_projects:
                try:
                    # Try to get packages for this project
                    project = self._gl.projects.get(p.id)
                    packages = project.packages.list()
                    
                    if len(packages) >= min_packages:
                        project_dict = self._project_to_dict(p)
                        project_dict['package_count'] = len(packages)
                        results.append(project_dict)
                except:
                    # Skip projects we can't access or that error
                    continue
            
            return results
            
        except Exception as e:
            raise OperationError(f"Failed to list projects with packages: {e}") from e
    
    def recent_activity(
        self,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get projects with recent activity.
        
        Args:
            limit: Number of projects to return
            
        Returns:
            List of recently active projects
            
        Example:
            >>> # Get 5 most recently active projects
            >>> recent = client.projects.discover.recent_activity(limit=5)
        """
        try:
            projects = self._gl.projects.list(
                order_by='last_activity_at',
                sort='desc',
                per_page=limit,
            )
            
            return [self._project_to_dict(p) for p in projects]
            
        except Exception as e:
            raise OperationError(f"Failed to get recent projects: {e}") from e
    
    def _project_to_dict(
        self,
        project,
        simple: bool = False,
        detailed: bool = False,
    ) -> Dict[str, Any]:
        """Convert project object to dictionary."""
        if simple:
            return {
                'id': project.id,
                'name': project.name,
                'path': project.path,
                'path_with_namespace': project.path_with_namespace,
            }
        
        result = {
            'id': project.id,
            'name': project.name,
            'path': project.path,
            'path_with_namespace': project.path_with_namespace,
            'description': getattr(project, 'description', None),
            'web_url': getattr(project, 'web_url', None),
            'created_at': getattr(project, 'created_at', None),
            'last_activity_at': getattr(project, 'last_activity_at', None),
            'namespace': getattr(project, 'namespace', {}),
            'visibility': getattr(project, 'visibility', None),
            'archived': getattr(project, 'archived', False),
            'star_count': getattr(project, 'star_count', 0),
            'forks_count': getattr(project, 'forks_count', 0),
        }
        
        if detailed:
            result.update({
                'http_url_to_repo': getattr(project, 'http_url_to_repo', None),
                'ssh_url_to_repo': getattr(project, 'ssh_url_to_repo', None),
                'readme_url': getattr(project, 'readme_url', None),
                'default_branch': getattr(project, 'default_branch', None),
                'topics': getattr(project, 'topics', []),
                'statistics': getattr(project, 'statistics', {}),
            })
        
        return result