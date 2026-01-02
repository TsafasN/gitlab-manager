"""
Example usage of GitLab Manager package operations.

This script demonstrates how to use the package management features
to upload, list, download, and delete packages from GitLab.
"""

import os
from utils import create_test_file, print_package_info
from gitlabmanager import GitLabClient
from gitlabmanager.progress import create_progress_callback
from gitlabmanager.exceptions import (
    ResourceNotFoundError,
    ValidationError,
    OperationError,
)

project_id = 'tutorialprojects1/softwareprojects/socketprogramming'

def example_basic_upload(client: GitLabClient):
    """Basic package upload without progress tracking."""
    try:
        # Create a test file to upload
        test_file = 'test-package.txt'
        with open(test_file, 'w') as f:
            f.write('This is a test package file\n')
        
        result = client.packages.upload(
            project_id=project_id,
            file_path=test_file,
            package_name='my-test-package',
            package_version='1.0.0'
        )
        print_package_info(result)
        print(f" Upload complete!")
        
        # Clean up test file
        os.remove(test_file)
    except ValidationError as e:
        print(f"Validation error: {e}")
    except OperationError as e:
        print(f"Upload failed: {e}")

def example_upload_with_progress(client: GitLabClient):
    """Upload a large file with progress bar."""
    try:
        # Create a test file
        test_file = create_test_file(
            filename='upload-test.tar.gz',
            size_mb=400,  # MB
            file_type='random'
        )

        # Create progress callback
        callback = create_progress_callback(
            total_bytes=os.path.getsize(filename=test_file),
            description="Uploading large file"
        )
        
        result = client.packages.upload(
            project_id=project_id,
            file_path=test_file,
            package_name='large-test-package',
            package_version='2024.1',
            progress_callback=callback,
        )
        print_package_info(result)        
        print(f" Upload complete!")

        # Clean up test file
        os.remove(test_file)
    except ValidationError as e:
        print(f"Validation error: {e}")
    except OperationError as e:
        print(f"Upload failed: {e}")

def example_delete_package(client: GitLabClient, package_name: str):
    """Delete old package versions (cleanup example)."""
    # Find old versions to delete
    packages = client.packages.list(
        project_id=project_id, 
        package_name=package_name
    )
    try:
        if packages:
            package_id = packages[0]['id']
            if client.packages.delete(
                project_id=project_id,
                package_id=package_id,
            ):
                print(f" Package {package_id} deleted successfully") 
        else:
            print(" No packages found to delete.")
            return
    except ResourceNotFoundError as e:
        print(f"Package not found: {e}")
    except ValidationError as e:
        print(f"Invalid package ID: {e}")
    except OperationError as e:
        print(f"Deletion failed: {e}")

def example_list_packages(client: GitLabClient):
    try:
        packages = client.packages.list(project_id)
        print(f"Found {len(packages)} packages:")
        for pkg in packages[:5]:  # Show first 5
            print(f"- {pkg['name']} v{pkg['version']} ({pkg['package_type']}) [ID: {pkg['id']}]")
        if len(packages) > 5:
            print(f"... and {len(packages) - 5} more")
    except ResourceNotFoundError as e:
        print(f"Project not found: {e}")
    except OperationError as e:
        print(f"Listing failed: {e}")

def example_filter_packages_by_type(client: GitLabClient):    
    try:
        generic_packages = client.packages.list(
            project_id,
            package_type='generic'
        )
        print(f"Found {len(generic_packages)} generic packages")
        
        pypi_packages = client.packages.list(
            project_id,
            package_type='pypi'
        )
        print(f"Found {len(pypi_packages)} PyPI packages")
    except OperationError as e:
        print(f"Filtering failed: {e}")

def example_get_package_details(client: GitLabClient):
    try:
        packages = client.packages.list(project_id)

        if packages:
            package_id = packages[0]['id']
            details = client.packages.get(project_id, package_id)
            print(f"Package details:")
            print(f"Name: {details['name']}")
            print(f"Version: {details['version']}")
            print(f"Type: {details['package_type']}")
            print(f"Created: {details['created_at']}")
    except ResourceNotFoundError as e:
        print(f"Package not found: {e}")
    except OperationError as e:
        print(f"Failed to get details: {e}")

def example_download_package(client: GitLabClient):
    try:
        # Download the package we uploaded earlier
        download_path = client.packages.download(
            project_id=project_id,
            package_name='my-test-package',
            package_version='1.0.0',
            file_name='test-package.txt',
            output_path='./downloads/'
        )
        print(f"Package downloaded to: {download_path}")
        
        # Verify the content
        with open(download_path, 'r') as f:
            content = f.read()
            print(f"Content: {content.strip()}")
        
        # Clean up
        os.remove(download_path)
        # Remove directory if it exists and is empty
        downloads_dir = './downloads/'
        if os.path.exists(downloads_dir) and not os.listdir(downloads_dir):
            os.rmdir(downloads_dir)
    except ResourceNotFoundError as e:
        print(f"Package not found: {e}")
    except OperationError as e:
        print(f"Download failed: {e}")

def example_upload_with_auto_name(client: GitLabClient):
    try:
        # Create a file with a descriptive name
        test_file = 'my-awesome-app-2.0.tar.gz'
        with open(test_file, 'w') as f:
            f.write('App content here\n')
        
        result = client.packages.upload(
            project_id=project_id,
            file_path=test_file
        )
        print(f"Auto-detected package name: {result['package_name']}")
        print(f"Version: {result['package_version']}")
        
        os.remove(test_file)
    except Exception as e:
        print(f"Upload failed: {e}")

def example_duplicate_package_check(client: GitLabClient):
    try:
        # Try to upload the same package from Example 7 again
        test_file = 'my-awesome-app-2.0.tar.gz'
        with open(test_file, 'w') as f:
            f.write('Attempting to upload duplicate\n')
        
        # This should fail because we already uploaded this in Example 7
        result = client.packages.upload(
            project_id=project_id,
            file_path=test_file
            # Will auto-detect same name and version as Example 7
        )
        print(f"Unexpected: Upload succeeded when it should have been blocked")
        os.remove(test_file)
    except ValidationError as e:
        print(f"Duplicate correctly detected and blocked!")
        print(f"Error message: {str(e)[:80]}...")
        if os.path.exists(test_file):
            os.remove(test_file)
    except Exception as e:
        print(f"Unexpected error: {e}")
        if os.path.exists(test_file):
            os.remove(test_file)

def main():
    
    print("=" * 60)
    print("GitLab Package Manager Examples")
    print("=" * 60)

    # Initialize the client
    client = GitLabClient(
        url='https://gitlab.com',
        private_token=os.environ['GITLAB_TOKEN']
    )
    
    print("\nExample: Upload a generic package...")
    example_basic_upload(client)

    print("\nExample: Upload a large file with progress bar...")
    example_upload_with_progress(client)

    print("\nExample: List all packages...")
    example_list_packages(client)

    print("\nExample: Filter packages by type...")
    example_filter_packages_by_type(client)

    print("\nExample: Get specific package details...")
    example_get_package_details(client)
    
    print("\nExample: Download a package...")
    example_download_package(client)

    print("\nExample: Upload with auto-detected package name...")
    example_upload_with_auto_name(client)

    print("\nExample: Test upload duplicate package detection...")
    example_duplicate_package_check(client)
    
    print("\nExample: Delete a package...")
    example_delete_package(client, "my-test-package")

    print("\nExample: Delete a large package...")
    example_delete_package(client, "large-test-package")

    print("\nExample: Delete a package...")
    example_delete_package(client, "my-awesome-app-2")
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)

if __name__ == '__main__':
    main()
