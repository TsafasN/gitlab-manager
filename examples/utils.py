import os
from pathlib import Path

def create_test_file(
    filename: str,
    size_mb: int = 100,
    file_type: str = "random",
) -> str:
    """
    Create a test file of specified size.
    
    Args:
        filename: Name of the file to create
        size_mb: Size in megabytes
        file_type: Type of data ('random', 'zeros', 'text', 'repeating')
        
    Returns:
        Path to the created file
    """
    filepath = Path(filename)
    size_bytes = size_mb * 1024 * 1024
    
    print(f"Creating {size_mb}MB test file: {filename}")
    print(f"Type: {file_type}")

    if file_type == "random":
        # Random data (most realistic for testing compression, etc.)
        create_random_file(filepath, size_bytes)
        return str(filepath)

def create_random_file(filepath: Path, size_bytes: int):
    """Create file with random data."""
    chunk_size = 1024 * 1024  # 1MB chunks
    
    with open(filepath, 'wb') as f:
        remaining = size_bytes
        while remaining > 0:
            chunk = min(chunk_size, remaining)
            f.write(os.urandom(chunk))
            remaining -= chunk
            
            # Show progress
            progress = ((size_bytes - remaining) / size_bytes) * 100
            print(f"\rProgress: {progress:.1f}%", end='', flush=True)
    
    print()  # New line after progress


def print_package_info(result:dict[str, any]):
    """Print package information in a readable format."""
    print("-" * 40)
    print(f" Upload successful: {result['message']}")
    print(f" Package: {result['package_name']}")
    print(f" Version: {result['package_version']}")
    print(f" Project ID: {result['project_id']}")
    print(f" Package ID: {result['package_id']}")
    print(f" File: {result['file_name']}")
    print(f" Size: {result['file_size']} bytes")
    print(f" Time: {result['uploaded_at']}")
    print("-" * 40)