"""
Path converter utility for handling Windows/WSL path differences.
This helps run experiments in a WSL environment when paths are stored in Windows format.
"""

import os
import re

def convert_to_wsl_path(windows_path):
    """
    Convert a Windows-style path to a WSL-compatible path.
    Example: 'c:/Users/name' -> '/mnt/c/Users/name'
    
    Args:
        windows_path (str): Windows-style path
        
    Returns:
        str: WSL-compatible path
    """
    # Skip if None or already a Linux-style path
    if not windows_path or windows_path.startswith('/'):
        return windows_path
        
    # Match drive letter pattern (e.g., "c:/")
    match = re.match(r'^([a-zA-Z]):[\\/](.*)$', windows_path)
    if match:
        drive_letter = match.group(1).lower()
        rest_of_path = match.group(2)
        # Replace backslashes with forward slashes
        rest_of_path = rest_of_path.replace('\\', '/')
        return f"/mnt/{drive_letter}/{rest_of_path}"
    
    # Return original if no match
    return windows_path