from __future__ import annotations

import json
import os
from datetime import datetime, timedelta

from .collection_manager import CollectionManager


class BackupManager(CollectionManager):

    def __init__(self, credentials_path: str, database: str = None, collections: list[str] = None,
                 backup_folder: str = None):
        """
        Initializes the FirestoreDB instance.

        :param credentials_path: Path to the Google Cloud service account credentials JSON file.
        :param database: Optional database URL. If provided, this database is used instead of the default.
        :param collections: Optional list of collection names to initialize.
        :param backup_folder: Optional path to a folder where backups will be stored.
        """
        super().__init__(credentials_path=credentials_path, database=database, collections=collections)
        self._backup_folder = backup_folder
        self.collections_to_backup = collections
        self.ensure_backup()

    @property
    def backup_folder(self) -> str:
        v = self._backup_folder
        if '~' in v:
            v = os.path.expanduser(v)
        return v

    @backup_folder.setter
    def backup_folder(self, value: str):
        self._backup_folder = value

    def save_collections_backup(self, collections: list[str] = None):
        """
        Saves a backup of specified collections or all collections if none are specified. The backup is saved in the
        backup folder specified during the initialization of the FirestoreDB instance.

        :param collections: Optional list of collection names to back up. If None, back up all collections.
        """
        if not self.backup_folder:
            print('Property backup_folder must be provided to save backup. Nothing will be done.')
            return
        base_folder = self.backup_folder
        collection_names = collections or self.collections_to_backup or self.get_collection_names()

        backup_time = datetime.now().strftime("%Y-%m-%d %H%M%S")
        backup_path = os.path.join(base_folder, 'db_backup', backup_time)
        os.makedirs(backup_path, exist_ok=True)

        for collection_name in collection_names:
            collection_data = self.get_collection_data_as_dict(collection_name)
            file_path = os.path.join(backup_path, f"{collection_name}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(collection_data, f, ensure_ascii=False, indent=4)

        print(f"Backup completed at {backup_path}")

    def ensure_backup(self, max_days: int = 7):
        """
        Ensures that a backup is taken if the latest backup is older than the specified number of days. If no backup
        exists, or the latest backup is too old, a new backup is created.

        :param max_days: The maximum number of days that can elapse before a new backup is required.
        """
        if not self.backup_folder:
            print('Property backup_folder must be provided to save backup. Nothing will be done.')
            return

        backup_base_path = os.path.join(self.backup_folder, 'db_backup')

        if not os.path.exists(backup_base_path):
            self.save_collections_backup()
            return

        backup_dirs = [d for d in os.listdir(backup_base_path) if os.path.isdir(os.path.join(backup_base_path, d))]
        backup_dates = []
        for dir_name in backup_dirs:
            try:
                backup_date = datetime.strptime(dir_name, "%Y-%m-%d %H%M%S")
                backup_dates.append(backup_date)
            except ValueError:
                continue

        if backup_dates:
            latest_backup_date = max(backup_dates)
            if datetime.now() - latest_backup_date > timedelta(days=max_days):
                self.save_collections_backup()
            else:
                print("A recent DB backup already exists. No new backup needed.")
                print(f"Latest DB backup: {latest_backup_date}")
        else:
            self.save_collections_backup()
