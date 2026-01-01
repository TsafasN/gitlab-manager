"""
Example usage of GitLab Manager package operations.

This script demonstrates how to use the package management features
to upload, list, download, and delete packages from GitLab.
"""

import os
from gitlabmanager import GitLabClient
from gitlabmanager.exceptions import (
    ResourceNotFoundError,
    ValidationError,
    OperationError,
)


def main():
    # Initialize the client
    # You can use environment variables or pass tokens directly
    client = GitLabClient(
        url='https://gitlab.com',
        private_token=os.environ.get('GITLAB_TOKEN')
    )
    
    # Replace with your project ID or path
    project_id = 'mygroup/myproject'
    project_id = '52929099'
    
    print("=" * 60)
    print("GitLab Package Manager Examples")
    print("=" * 60)
    
    # Example 1: Upload a generic package
    print("\n1. Uploading a package...")
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
        print(f"✓ Upload successful: {result['message']}")
        print(f"  Package: {result['package_name']} v{result['package_version']}")
        print(f"  File: {result['file_name']}")
        
        # Clean up test file
        os.remove(test_file)
    except ValidationError as e:
        print(f"✗ Validation error: {e}")
    except OperationError as e:
        print(f"✗ Upload failed: {e}")
    
    # Example 2: List all packages
    print("\n2. Listing all packages...")
    try:
        packages = client.packages.list(project_id)
        print(f"✓ Found {len(packages)} packages:")
        for pkg in packages[:5]:  # Show first 5
            print(f"  - {pkg['name']} v{pkg['version']} ({pkg['package_type']}) [ID: {pkg['id']}]")
        if len(packages) > 5:
            print(f"  ... and {len(packages) - 5} more")
    except ResourceNotFoundError as e:
        print(f"✗ Project not found: {e}")
    except OperationError as e:
        print(f"✗ Listing failed: {e}")
    
    # Example 3: Filter packages by type
    print("\n3. Filtering packages by type...")
    try:
        generic_packages = client.packages.list(
            project_id,
            package_type='generic'
        )
        print(f"✓ Found {len(generic_packages)} generic packages")
        
        pypi_packages = client.packages.list(
            project_id,
            package_type='pypi'
        )
        print(f"✓ Found {len(pypi_packages)} PyPI packages")
    except OperationError as e:
        print(f"✗ Filtering failed: {e}")
    
    # Example 4: Get specific package details
    print("\n4. Getting package details...")
    try:
        if packages:
            package_id = packages[0]['id']
            details = client.packages.get(project_id, package_id)
            print(f"✓ Package details:")
            print(f"  Name: {details['name']}")
            print(f"  Version: {details['version']}")
            print(f"  Type: {details['package_type']}")
            print(f"  Created: {details['created_at']}")
    except ResourceNotFoundError as e:
        print(f"✗ Package not found: {e}")
    except OperationError as e:
        print(f"✗ Failed to get details: {e}")
    
    # Example 5: Download a package
    print("\n5. Downloading a package...")
    try:
        # Download the package we uploaded earlier
        download_path = client.packages.download(
            project_id=project_id,
            package_name='my-test-package',
            package_version='1.0.0',
            file_name='test-package.txt',
            output_path='./downloads/'
        )
        print(f"✓ Package downloaded to: {download_path}")
        
        # Verify the content
        with open(download_path, 'r') as f:
            content = f.read()
            print(f"  Content: {content.strip()}")
        
        # Clean up
        os.remove(download_path)
        os.rmdir('./downloads/')
    except ResourceNotFoundError as e:
        print(f"✗ Package not found: {e}")
    except OperationError as e:
        print(f"✗ Download failed: {e}")
    
    # Example 6: Delete a package
    print("\n6. Deleting a package...")
    try:
        # Find the package we want to delete
        packages = client.packages.list(
            project_id,
            package_name='my-test-package'
        )
        
        if packages:
            package_id = packages[0]['id']
            success = client.packages.delete(project_id, package_id)
            if success:
                print(f"✓ Package {package_id} deleted successfully")
        else:
            print("  No package to delete")
    except ResourceNotFoundError as e:
        print(f"✗ Package not found: {e}")
    except ValidationError as e:
        print(f"✗ Invalid package ID: {e}")
    except OperationError as e:
        print(f"✗ Deletion failed: {e}")
    
    # Example 7: Upload with auto-detected name
    print("\n7. Upload with auto-detected package name...")
    try:
        # Create a file with a descriptive name
        test_file = 'my-awesome-app-2.0.tar.gz'
        with open(test_file, 'w') as f:
            f.write('App content here\n')
        
        # Package name will be auto-detected as 'my-awesome-app-2.0'
        # Version defaults to '1.0.0'
        result = client.packages.upload(
            project_id=project_id,
            file_path=test_file
        )
        print(f"✓ Auto-detected package name: {result['package_name']}")
        print(f"  Version: {result['package_version']}")
        
        os.remove(test_file)
    except Exception as e:
        print(f"✗ Upload failed: {e}")
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == '__main__':
    main()
