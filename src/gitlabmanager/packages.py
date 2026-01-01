"""Package management operations."""

import gitlab
from pathlib import Path
from typing import Optional, List, Dict, Any
from .exceptions import OperationError, ResourceNotFoundError, ValidationError


class PackageManager:
    """
    Manage GitLab packages.
    
    Provides high-level operations for uploading, downloading,
    listing, and managing packages in GitLab package registries.
    """
    
    def __init__(self, gl: gitlab.Gitlab):
        """Initialize the package manager."""
        self._gl = gl
    
    def list(
        self,
        project_id: str,
        package_type: Optional[str] = None,
        package_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List packages in a project.
        
        Args:
            project_id: Project ID or path (e.g., 'group/project' or 123)
            package_type: Optional filter by package type (e.g., 'pypi', 'npm', 'maven', 'generic')
            package_name: Optional filter by package name
            
        Returns:
            List of package information dictionaries with keys:
            - id: Package ID
            - name: Package name
            - version: Package version
            - package_type: Type of package
            - created_at: Creation timestamp
            
        Raises:
            ResourceNotFoundError: If project is not found
            OperationError: If listing fails
            
        Example:
            >>> # List all packages
            >>> packages = client.packages.list('mygroup/myproject')
            >>> 
            >>> # Filter by type
            >>> pypi_packages = client.packages.list('mygroup/myproject', package_type='pypi')
            >>> 
            >>> # Filter by name
            >>> specific = client.packages.list('mygroup/myproject', package_name='my-package')
        """
        try:
            project = self._gl.projects.get(project_id)
        except gitlab.exceptions.GitlabGetError as e:
            raise ResourceNotFoundError(f"Project '{project_id}' not found: {e}")
        except Exception as e:
            raise OperationError(f"Failed to get project: {e}")
        
        try:
            # Build filter parameters
            filters = {}
            if package_type:
                filters['package_type'] = package_type
            if package_name:
                filters['package_name'] = package_name
            
            # Get all packages with optional filters
            packages = project.packages.list(get_all=True, **filters)
            
            # Return simplified package information
            return [
                {
                    'id': pkg.id,
                    'name': pkg.name,
                    'version': pkg.version,
                    'package_type': pkg.package_type,
                    'created_at': pkg.created_at,
                }
                for pkg in packages
            ]
        except Exception as e:
            raise OperationError(f"Failed to list packages: {e}")
    
    def get(self, project_id: str, package_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific package.
        
        Args:
            project_id: Project ID or path
            package_id: ID of the package
            
        Returns:
            Dictionary with detailed package information including:
            - id, name, version, package_type
            - created_at, _links
            - All other attributes from the GitLab API
            
        Raises:
            ResourceNotFoundError: If project or package is not found
            OperationError: If retrieval fails
            
        Example:
            >>> package = client.packages.get('myproject', 123)
            >>> print(f"Package: {package['name']} v{package['version']}")
        """
        try:
            project = self._gl.projects.get(project_id)
        except gitlab.exceptions.GitlabGetError as e:
            raise ResourceNotFoundError(f"Project '{project_id}' not found: {e}")
        except Exception as e:
            raise OperationError(f"Failed to get project: {e}")
        
        try:
            package = project.packages.get(package_id)
            return package.attributes
        except gitlab.exceptions.GitlabGetError as e:
            raise ResourceNotFoundError(f"Package {package_id} not found: {e}")
        except Exception as e:
            raise OperationError(f"Failed to get package: {e}")
    
    def delete(self, project_id: str, package_id: int) -> bool:
        """
        Delete a package from the project.
        
        Args:
            project_id: Project ID or path
            package_id: ID of the package to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            ResourceNotFoundError: If project or package is not found
            OperationError: If deletion fails
            ValidationError: If package_id is invalid
            
        Example:
            >>> success = client.packages.delete('myproject', 123)
            >>> if success:
            >>>     print("Package deleted successfully")
        """
        if not isinstance(package_id, int) or package_id <= 0:
            raise ValidationError(f"Invalid package_id: {package_id}. Must be a positive integer.")
        
        try:
            project = self._gl.projects.get(project_id)
        except gitlab.exceptions.GitlabGetError as e:
            raise ResourceNotFoundError(f"Project '{project_id}' not found: {e}")
        except Exception as e:
            raise OperationError(f"Failed to get project: {e}")
        
        try:
            project.packages.delete(package_id)
            return True
        except gitlab.exceptions.GitlabDeleteError as e:
            raise ResourceNotFoundError(f"Package {package_id} not found or cannot be deleted: {e}")
        except Exception as e:
            raise OperationError(f"Failed to delete package: {e}")
    
    def upload(
        self,
        project_id: str,
        file_path: str,
        package_name: Optional[str] = None,
        package_version: Optional[str] = None,
        file_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a generic package to GitLab.
        
        This method uploads files to the GitLab Generic Package Registry,
        which supports arbitrary file types.
        
        Args:
            project_id: Project ID or path
            file_path: Path to the file to upload
            package_name: Name of the package (defaults to filename without extension)
            package_version: Version of the package (defaults to '1.0.0')
            file_name: Name for the file in the package (defaults to original filename)
            
        Returns:
            Dictionary with upload results including:
            - message: Success message
            - package_name: Name of the uploaded package
            - package_version: Version of the package
            - file_name: Name of the uploaded file
            
        Raises:
            ValidationError: If file doesn't exist or parameters are invalid
            ResourceNotFoundError: If project is not found
            OperationError: If upload fails
            
        Example:
            >>> # Upload with auto-detected name
            >>> result = client.packages.upload('myproject', 'dist/myapp-1.0.tar.gz')
            >>> 
            >>> # Upload with custom name and version
            >>> result = client.packages.upload(
            ...     'myproject',
            ...     'build/app.zip',
            ...     package_name='my-app',
            ...     package_version='2.0.0'
            ... )
        """
        # Validate file exists
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise ValidationError(f"File not found: {file_path}")
        if not file_path_obj.is_file():
            raise ValidationError(f"Path is not a file: {file_path}")
        
        # Set defaults
        if file_name is None:
            file_name = file_path_obj.name
        
        if package_name is None:
            # Use filename without extension as package name
            package_name = file_path_obj.stem
        
        if package_version is None:
            package_version = "1.0.0"
        
        # Validate package name and version
        if not package_name or not package_name.strip():
            raise ValidationError("Package name cannot be empty")
        if not package_version or not package_version.strip():
            raise ValidationError("Package version cannot be empty")
        
        try:
            project = self._gl.projects.get(project_id)
        except gitlab.exceptions.GitlabGetError as e:
            raise ResourceNotFoundError(f"Project '{project_id}' not found: {e}")
        except Exception as e:
            raise OperationError(f"Failed to get project: {e}")
        
        try:
            # Upload the generic package
            project.generic_packages.upload(
                package_name=package_name,
                package_version=package_version,
                file_name=file_name,
                path=str(file_path_obj.absolute()),
            )
            
            return {
                'message': 'Package uploaded successfully',
                'package_name': package_name,
                'package_version': package_version,
                'file_name': file_name,
            }
        except Exception as e:
            raise OperationError(f"Failed to upload package: {e}")
    
    def download(
        self,
        project_id: str,
        package_name: str,
        package_version: str,
        file_name: str,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Download a generic package from GitLab.
        
        Args:
            project_id: Project ID or path
            package_name: Name of the package
            package_version: Version of the package
            file_name: Name of the file within the package
            output_path: Where to save the file (defaults to current directory with original filename)
            
        Returns:
            Absolute path to the downloaded file
            
        Raises:
            ResourceNotFoundError: If project or package is not found
            OperationError: If download fails
            ValidationError: If parameters are invalid
            
        Example:
            >>> # Download to current directory
            >>> path = client.packages.download(
            ...     'myproject',
            ...     'my-app',
            ...     '1.0.0',
            ...     'app.tar.gz'
            ... )
            >>> print(f"Downloaded to: {path}")
            >>> 
            >>> # Download to specific location
            >>> path = client.packages.download(
            ...     'myproject',
            ...     'my-app',
            ...     '1.0.0',
            ...     'app.tar.gz',
            ...     output_path='/tmp/myapp.tar.gz'
            ... )
        """
        # Validate inputs
        if not package_name or not package_name.strip():
            raise ValidationError("Package name cannot be empty")
        if not package_version or not package_version.strip():
            raise ValidationError("Package version cannot be empty")
        if not file_name or not file_name.strip():
            raise ValidationError("File name cannot be empty")
        
        # Determine output path
        if output_path is None:
            output_path = Path.cwd() / file_name
        else:
            output_path = Path(output_path)
            # If output_path is a directory, append the filename
            if output_path.is_dir():
                output_path = output_path / file_name
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            project = self._gl.projects.get(project_id)
        except gitlab.exceptions.GitlabGetError as e:
            raise ResourceNotFoundError(f"Project '{project_id}' not found: {e}")
        except Exception as e:
            raise OperationError(f"Failed to get project: {e}")
        
        try:
            # Download the generic package
            content = project.generic_packages.download(
                package_name=package_name,
                package_version=package_version,
                file_name=file_name,
            )
            
            # Write content to file
            with open(output_path, 'wb') as f:
                f.write(content)
            
            return str(output_path.absolute())
        except gitlab.exceptions.GitlabGetError as e:
            raise ResourceNotFoundError(
                f"Package '{package_name}' version '{package_version}' "
                f"with file '{file_name}' not found: {e}"
            )
        except Exception as e:
            raise OperationError(f"Failed to download package: {e}")