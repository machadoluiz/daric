from os import listdir
from os.path import join
from typing import List


class LocalFileExtractor:
    """Handles reading local files."""

    def __init__(self) -> None:
        """Initializes the LocalFileExtractor with the file path."""
        pass

    def list_files(self, path: str) -> List[str]:
        """Lists files in a local folder.

        Args:
            path (str): The path of the folder to list files from.

        Returns:
            List[str]: A list of filenames in the folder.
        """
        return listdir(path)

    def download_file(self, path: str, file: str) -> str:
        """Downloads a file from a local folder.

        Args:
            path (str): The path of the folder.
            file (str): The name of the file to download.

        Returns:
            str: The full file path.
        """
        return join(path, file)
