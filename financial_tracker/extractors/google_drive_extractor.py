from io import BytesIO
from typing import IO, Any, Dict, List, cast

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from streamlit import session_state


class GoogleDriveExtractor:
    """Handles interactions with Google Drive."""

    def __init__(self) -> None:
        """Initializes Google Drive credentials and service.

        Raises:
            KeyError: If 'gcp_credentials_json' is not found in session_state.
        """
        try:
            creds_json = session_state["gcp_credentials_json"]
        except KeyError as e:
            raise KeyError(
                "Google Cloud Platform credentials JSON is missing in session_state."
            ) from e

        SCOPES: List[str] = [
            "https://www.googleapis.com/auth/drive.metadata.readonly",
            "https://www.googleapis.com/auth/drive",
        ]

        self.creds: Credentials = Credentials.from_service_account_info(
            creds_json, scopes=SCOPES
        )
        self.service = build("drive", "v3", credentials=self.creds)

    def list_files(self, folder_id: str) -> List[Dict[str, Any]]:
        """Lists files in a Google Drive folder.

        Args:
            folder_id: The ID of the folder to list files from.

        Returns:
            A list of dictionaries containing file information.
        """
        response = (
            self.service.files()
            .list(q=f'"{folder_id}" in parents and mimeType="text/csv"')
            .execute()
        )
        return cast(List[Dict[str, Any]], response.get("files", []))

    def download_file(self, file_id: str) -> IO[bytes]:
        """Downloads a file from Google Drive.

        Args:
            file_id: The ID of the file to download.

        Returns:
            A BytesIO object containing the downloaded file data.
        """
        request = self.service.files().get_media(fileId=file_id)
        downloaded = BytesIO()
        downloader = MediaIoBaseDownload(downloaded, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        downloaded.seek(0)
        return downloaded
