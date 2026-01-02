"""Progress tracking utilities for file uploads and downloads."""

from typing import Optional, Callable


class ProgressTracker:
    """
    Simple progress tracker that can be used with or without tqdm.
    
    This provides a consistent interface for progress tracking,
    with optional tqdm integration for fancy progress bars.
    """
    
    def __init__(
        self,
        total: int,
        description: str = "Progress",
        use_tqdm: bool = True,
    ):
        """
        Initialize progress tracker.
        
        Args:
            total: Total number of bytes/items
            description: Description to show
            use_tqdm: Whether to use tqdm for display (falls back to simple print)
        """
        self.total = total
        self.description = description
        self.current = 0
        self.use_tqdm = use_tqdm
        self._tqdm = None
        
        if use_tqdm:
            try:
                from tqdm import tqdm
                self._tqdm = tqdm(
                    total=total,
                    desc=description,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                )
            except ImportError:
                # tqdm not available, fall back to simple progress
                self.use_tqdm = False
    
    def update(self, amount: int):
        """Update progress by amount."""
        self.current += amount
        
        if self._tqdm:
            self._tqdm.update(amount)
        elif not self.use_tqdm:
            # Simple text progress
            percent = (self.current / self.total) * 100 if self.total > 0 else 0
            print(f"\r{self.description}: {percent:.1f}%", end='', flush=True)
    
    def close(self):
        """Close the progress tracker."""
        if self._tqdm:
            self._tqdm.close()
        elif not self.use_tqdm:
            print()  # New line after progress
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close on context exit."""
        self.close()


def create_progress_callback(
    total_bytes: int,
    description: str = "Upload",
    use_tqdm: bool = True,
) -> Callable[[int, int], None]:
    """
    Create a progress callback function.
    
    Args:
        total_bytes: Total size in bytes
        description: Description for the progress bar
        use_tqdm: Whether to use tqdm
        
    Returns:
        Callback function that accepts (current, total) arguments
        
    Example:
        >>> callback = create_progress_callback(1000000, "Uploading")
        >>> # Use with PackageManager
        >>> result = client.packages.upload(
        ...     'project',
        ...     'file.tar.gz',
        ...     progress_callback=callback
        ... )
    """
    tracker = ProgressTracker(total_bytes, description, use_tqdm)
    last_update = [0]  # Use list to allow modification in closure
    
    def callback(current: int, total: int):
        """Progress callback that updates the tracker."""
        # Calculate the delta since last update
        delta = current - last_update[0]
        if delta > 0:
            tracker.update(delta)
            last_update[0] = current
        
        # Close when complete
        if current >= total:
            tracker.close()
    
    return callback


def format_bytes(bytes_size: int) -> str:
    """
    Format bytes into human-readable string.
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"
    