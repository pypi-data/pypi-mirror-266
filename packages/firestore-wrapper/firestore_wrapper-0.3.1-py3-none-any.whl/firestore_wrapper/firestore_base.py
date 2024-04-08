from __future__ import annotations

from google.cloud import firestore
from google.oauth2 import service_account


class FirestoreBase:

    def __init__(self, credentials_path: str, database: str = None):
        """
        Initializes the FirestoreBase instance.

        :param credentials_path: Path to the Google Cloud service account credentials JSON file.
        :param database: Optional database URL. If provided, this database is used instead of the default.
        """
        self.credentials = service_account.Credentials.from_service_account_file(credentials_path)
        self.db = firestore.Client(credentials=self.credentials, database=database)
