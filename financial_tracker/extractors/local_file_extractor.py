from os import listdir
from os.path import join


class LocalFileExtractor:
    """Handles reading local files."""

    def __init__(self) -> None:
        """Initializes the LocalFileExtractor."""
        pass

    def list_files(self, path: str) -> list[str]:
        """Lists files in a local folder.

        Args:
            path: The path of the folder to list files from.

        Returns:
            A list of filenames in the folder.

        Raises:
            FileNotFoundError: If the specified path does not exist.
            NotADirectoryError: If the specified path is not a directory.
        """
        return listdir(path)

    def download_file(self, path: str, file: str) -> str:
        """Generates the full path to a file in a local folder.

        Args:
            path: The path of the folder.
            file: The name of the file.

        Returns:
            The full file path.
        """
        return join(path, file)
