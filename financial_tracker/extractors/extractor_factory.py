from typing import Type

from .google_drive_extractor import GoogleDriveExtractor
from .local_file_extractor import LocalFileExtractor


class ExtractorFactory:
    """Factory class to create data extractors."""

    _extractors: dict[str, Type[object]] = {
        "Sample data (demo)": LocalFileExtractor,
        "Local files": LocalFileExtractor,
        "Google Drive": GoogleDriveExtractor,
    }

    @classmethod
    def create_extractor(cls, data_source: str) -> object:
        """Creates an extractor instance based on the specified data source.

        Args:
            data_source: The type of data source.

        Returns:
            An instance of the appropriate extractor class.

        Raises:
            ValueError: If the data source is unknown.
        """
        extractor_class = cls._extractors.get(data_source)
        if extractor_class is not None:
            return extractor_class()
        raise ValueError(f"Unknown data source: {data_source}")
