import os
from typing import IO, Any, Dict, List


class LocalFileExtractor:
    """Handles reading local files."""

    def __init__(self) -> None:
        """Initializes the LocalFileExtractor with the file path."""
        pass

    def list_files(self, path: str) -> List[Dict[str, Any]]:
        """Lists files in a local folder.

        Args:
            path (str): The path of the folder to list files from.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing file information.
        """
        return os.listdir(path)

    def download_file(self, path: str, file: str) -> IO[bytes]:
        """Downloads a file from a local folder.

        Args:
            path (str): The path of the folder.
            file (str): The name of the file to download.

        Returns:
            IO[bytes]: A BytesIO object containing the downloaded file data.
        """
        return os.path.join(path, file)
