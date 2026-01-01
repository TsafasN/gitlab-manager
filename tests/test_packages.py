"""Unit tests for package management operations."""

import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from pathlib import Path
import gitlab.exceptions

from gitlabmanager.packages import PackageManager
from gitlabmanager.exceptions import (
    ResourceNotFoundError,
    OperationError,
    ValidationError,
)


@pytest.fixture
def mock_gitlab():
    """Create a mock GitLab client."""
    gl = Mock()
    gl.projects = Mock()
    return gl


@pytest.fixture
def package_manager(mock_gitlab):
    """Create a PackageManager instance with mocked GitLab client."""
    return PackageManager(mock_gitlab)


@pytest.fixture
def mock_project():
    """Create a mock project."""
    project = Mock()
    project.id = 123
    project.name = 'test-project'
    return project


class TestPackageList:
    """Tests for listing packages."""
    
    def test_list_all_packages(self, package_manager, mock_gitlab, mock_project):
        """Test listing all packages in a project."""
        # Setup
        mock_gitlab.projects.get.return_value = mock_project
        
        mock_package1 = Mock()
        mock_package1.id = 1
        mock_package1.name = 'package1'
        mock_package1.version = '1.0.0'
        mock_package1.package_type = 'generic'
        mock_package1.created_at = '2024-01-01T00:00:00Z'
        
        mock_package2 = Mock()
        mock_package2.id = 2
        mock_package2.name = 'package2'
        mock_package2.version = '2.0.0'
        mock_package2.package_type = 'pypi'
        mock_package2.created_at = '2024-01-02T00:00:00Z'
        
        mock_project.packages.list.return_value = [mock_package1, mock_package2]
        
        # Execute
        result = package_manager.list('test-project')
        
        # Assert
        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[0]['name'] == 'package1'
        assert result[0]['version'] == '1.0.0'
        assert result[0]['package_type'] == 'generic'
        assert result[1]['id'] == 2
        mock_project.packages.list.assert_called_once_with(get_all=True)
    
    def test_list_packages_with_type_filter(self, package_manager, mock_gitlab, mock_project):
        """Test filtering packages by type."""
        mock_gitlab.projects.get.return_value = mock_project
        mock_project.packages.list.return_value = []
        
        package_manager.list('test-project', package_type='pypi')
        
        mock_project.packages.list.assert_called_once_with(
            get_all=True,
            package_type='pypi'
        )
    
    def test_list_packages_with_name_filter(self, package_manager, mock_gitlab, mock_project):
        """Test filtering packages by name."""
        mock_gitlab.projects.get.return_value = mock_project
        mock_project.packages.list.return_value = []
        
        package_manager.list('test-project', package_name='my-package')
        
        mock_project.packages.list.assert_called_once_with(
            get_all=True,
            package_name='my-package'
        )
    
    def test_list_packages_project_not_found(self, package_manager, mock_gitlab):
        """Test listing packages when project doesn't exist."""
        mock_gitlab.projects.get.side_effect = gitlab.exceptions.GitlabGetError()
        
        with pytest.raises(ResourceNotFoundError, match="Project .* not found"):
            package_manager.list('nonexistent-project')
    
    def test_list_packages_operation_error(self, package_manager, mock_gitlab, mock_project):
        """Test handling of operation errors during listing."""
        mock_gitlab.projects.get.return_value = mock_project
        mock_project.packages.list.side_effect = Exception("API error")
        
        with pytest.raises(OperationError, match="Failed to list packages"):
            package_manager.list('test-project')


class TestPackageGet:
    """Tests for getting package details."""
    
    def test_get_package_success(self, package_manager, mock_gitlab, mock_project):
        """Test getting package details successfully."""
        mock_gitlab.projects.get.return_value = mock_project
        
        mock_package = Mock()
        mock_package.attributes = {
            'id': 1,
            'name': 'test-package',
            'version': '1.0.0',
            'package_type': 'generic',
            'created_at': '2024-01-01T00:00:00Z',
        }
        mock_project.packages.get.return_value = mock_package
        
        result = package_manager.get('test-project', 1)
        
        assert result['id'] == 1
        assert result['name'] == 'test-package'
        mock_project.packages.get.assert_called_once_with(1)
    
    def test_get_package_not_found(self, package_manager, mock_gitlab, mock_project):
        """Test getting non-existent package."""
        mock_gitlab.projects.get.return_value = mock_project
        mock_project.packages.get.side_effect = gitlab.exceptions.GitlabGetError()
        
        with pytest.raises(ResourceNotFoundError, match="Package .* not found"):
            package_manager.get('test-project', 999)


class TestPackageDelete:
    """Tests for deleting packages."""
    
    def test_delete_package_success(self, package_manager, mock_gitlab, mock_project):
        """Test successful package deletion."""
        mock_gitlab.projects.get.return_value = mock_project
        mock_project.packages.delete.return_value = None
        
        result = package_manager.delete('test-project', 1)
        
        assert result is True
        mock_project.packages.delete.assert_called_once_with(1)
    
    def test_delete_package_invalid_id(self, package_manager):
        """Test deletion with invalid package ID."""
        with pytest.raises(ValidationError, match="Invalid package_id"):
            package_manager.delete('test-project', 0)
        
        with pytest.raises(ValidationError, match="Invalid package_id"):
            package_manager.delete('test-project', -1)
    
    def test_delete_package_not_found(self, package_manager, mock_gitlab, mock_project):
        """Test deleting non-existent package."""
        mock_gitlab.projects.get.return_value = mock_project
        mock_project.packages.delete.side_effect = gitlab.exceptions.GitlabDeleteError()
        
        with pytest.raises(ResourceNotFoundError, match="Package .* not found"):
            package_manager.delete('test-project', 999)


class TestPackageUpload:
    """Tests for uploading packages."""
    
    def test_upload_with_all_parameters(self, package_manager, mock_gitlab, mock_project):
        """Test uploading with all parameters specified."""
        mock_gitlab.projects.get.return_value = mock_project
        mock_project.generic_packages.upload.return_value = None
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.absolute', return_value=Path('/abs/path/test.tar.gz')):
            
            result = package_manager.upload(
                project_id='test-project',
                file_path='test.tar.gz',
                package_name='my-package',
                package_version='2.0.0',
                file_name='custom-name.tar.gz'
            )
        
        assert result['message'] == 'Package uploaded successfully'
        assert result['package_name'] == 'my-package'
        assert result['package_version'] == '2.0.0'
        assert result['file_name'] == 'custom-name.tar.gz'
        
        mock_project.generic_packages.upload.assert_called_once()
    
    def test_upload_with_defaults(self, package_manager, mock_gitlab, mock_project):
        """Test uploading with default parameters."""
        mock_gitlab.projects.get.return_value = mock_project
        mock_project.generic_packages.upload.return_value = None
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.absolute', return_value=Path('/abs/path/myapp-1.0.tar.gz')), \
             patch('pathlib.Path.name', 'myapp-1.0.tar.gz'), \
             patch('pathlib.Path.stem', 'myapp-1.0'):
            
            result = package_manager.upload(
                project_id='test-project',
                file_path='myapp-1.0.tar.gz'
            )
        
        assert result['package_version'] == '1.0.0'  # Default version
    
    def test_upload_file_not_found(self, package_manager):
        """Test uploading non-existent file."""
        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(ValidationError, match="File not found"):
                package_manager.upload('test-project', 'nonexistent.tar.gz')
    
    def test_upload_path_is_directory(self, package_manager):
        """Test uploading when path is a directory."""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=False):
            with pytest.raises(ValidationError, match="Path is not a file"):
                package_manager.upload('test-project', '/some/directory')
    
    def test_upload_empty_package_name(self, package_manager, mock_gitlab, mock_project):
        """Test uploading with empty package name."""
        mock_gitlab.projects.get.return_value = mock_project
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True):
            with pytest.raises(ValidationError, match="Package name cannot be empty"):
                package_manager.upload(
                    'test-project',
                    'test.tar.gz',
                    package_name='   '  # Empty after strip
                )
    
    def test_upload_project_not_found(self, package_manager, mock_gitlab):
        """Test uploading to non-existent project."""
        mock_gitlab.projects.get.side_effect = gitlab.exceptions.GitlabGetError()
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True):
            with pytest.raises(ResourceNotFoundError, match="Project .* not found"):
                package_manager.upload('nonexistent-project', 'test.tar.gz')


class TestPackageDownload:
    """Tests for downloading packages."""
    
    def test_download_to_default_location(self, package_manager, mock_gitlab, mock_project):
        """Test downloading to current directory."""
        mock_gitlab.projects.get.return_value = mock_project
        mock_project.generic_packages.download.return_value = b'file content'
        
        with patch('pathlib.Path.cwd', return_value=Path('/current/dir')), \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('pathlib.Path.mkdir'):
            
            result = package_manager.download(
                project_id='test-project',
                package_name='my-package',
                package_version='1.0.0',
                file_name='app.tar.gz'
            )
        
        assert '/current/dir/app.tar.gz' in result
        mock_project.generic_packages.download.assert_called_once_with(
            package_name='my-package',
            package_version='1.0.0',
            file_name='app.tar.gz'
        )
    
    def test_download_to_custom_location(self, package_manager, mock_gitlab, mock_project):
        """Test downloading to custom path."""
        mock_gitlab.projects.get.return_value = mock_project
        mock_project.generic_packages.download.return_value = b'file content'
        
        with patch('builtins.open', mock_open()) as mock_file, \
             patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.is_dir', return_value=False):
            
            result = package_manager.download(
                project_id='test-project',
                package_name='my-package',
                package_version='1.0.0',
                file_name='app.tar.gz',
                output_path='/tmp/custom.tar.gz'
            )
        
        assert '/tmp/custom.tar.gz' in result
    
    def test_download_empty_package_name(self, package_manager):
        """Test downloading with empty package name."""
        with pytest.raises(ValidationError, match="Package name cannot be empty"):
            package_manager.download(
                'test-project',
                '',
                '1.0.0',
                'file.tar.gz'
            )
    
    def test_download_empty_version(self, package_manager):
        """Test downloading with empty version."""
        with pytest.raises(ValidationError, match="Package version cannot be empty"):
            package_manager.download(
                'test-project',
                'my-package',
                '   ',
                'file.tar.gz'
            )
    
    def test_download_package_not_found(self, package_manager, mock_gitlab, mock_project):
        """Test downloading non-existent package."""
        mock_gitlab.projects.get.return_value = mock_project
        mock_project.generic_packages.download.side_effect = gitlab.exceptions.GitlabGetError()
        
        with patch('pathlib.Path.mkdir'):
            with pytest.raises(ResourceNotFoundError, match="Package .* not found"):
                package_manager.download(
                    'test-project',
                    'nonexistent',
                    '1.0.0',
                    'file.tar.gz'
                )
