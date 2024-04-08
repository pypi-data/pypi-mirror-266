from __future__ import annotations

from .backup_manager import BackupManager
from .document_manager import DocumentManager
from .query_manager import QueryManager
from .utility_manager import UtilityManager


class FirestoreDB(BackupManager, DocumentManager, QueryManager, UtilityManager):
    def __init__(self, credentials_path: str, database: str = None, collections: list[str] = None,
                 backup_folder: str = None):
        """
        Initializes the FirestoreDB instance, combining functionalities of document and collection management,
        querying, and backup management into a single interface.

        Inherits and extends BackupManager, DocumentManager, QueryManager, and UtilityManager functionalities.

        :param credentials_path: Path to the Google Cloud service account credentials JSON file.
        :param database: Optional database URL. If provided, this database is used instead of the default.
        :param collections: Optional list of collection names to initialize.
        :param backup_folder: Optional path to a folder where backups will be stored.
        """
        # Initialize BackupManager as it also initializes CollectionManager and FirestoreBase
        super().__init__(credentials_path=credentials_path, database=database, collections=collections,
                         backup_folder=backup_folder)
