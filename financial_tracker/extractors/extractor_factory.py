from abc import ABC, abstractmethod

from .google_drive_extractor import GoogleDriveExtractor


class ExtractorFactory(ABC):
    """Defines the interface for creating extractor objects."""

    @abstractmethod
    def create_extractor(self):
        """Creates an extractor instance."""
        pass


class GoogleDriveExtractorFactory(ExtractorFactory):
    """Factory class for creating GoogleDriveExtractor instances."""

    def create_extractor(self) -> GoogleDriveExtractor:
        """Creates an extractor instance.

        Returns:
            GoogleDriveExtractor: An instance of GoogleDriveExtractor.
        """
        return GoogleDriveExtractor()
