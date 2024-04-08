import os

from typing import List


def get_immediate_subdirectories(full_path: str, ignore: List=[]) -> List[str]:
    """
    Get all immediate sub-directories for a certain full path.

    Args:
        full_path (str): Full path to folder to get immediate sub-directories for.
        ignore (List): List of folders to ignore. Defaults to [].

    Returns:
        List: List of immediate sub-directories.
    """
    if not os.path.isabs(full_path):
        raise ValueError("Parameter full_path must be an Absolute Path!")

    subdirectories = []
    for item in os.scandir(full_path):
        if item.is_dir() and item.name not in ignore:
                subdirectories.append(item.path)

    return subdirectories
