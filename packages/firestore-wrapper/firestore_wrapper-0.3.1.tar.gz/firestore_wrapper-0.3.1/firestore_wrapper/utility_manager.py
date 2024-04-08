from __future__ import annotations

from google.cloud import firestore

from .firestore_base import FirestoreBase


class UtilityManager(FirestoreBase):

    def __init__(self, credentials_path: str, database: str = None):
        """
        Initializes the UtilityManager instance.

        :param credentials_path: Path to the Google Cloud service account credentials JSON file.
        :param database: Optional database URL. If provided, this database is used instead of the default.
        """
        super().__init__(credentials_path=credentials_path, database=database)

    def change_field_name(self, collection_name: str, document_name: str, old_field_name: str, new_field_name: str):
        """
        Renames a field in a specific document within a collection.

        :param collection_name: The name of the collection.
        :param document_name: The name of the document.
        :param old_field_name: The current name of the field.
        :param new_field_name: The new name for the field.
        """
        doc = self.db.collection(collection_name).document(document_name)
        data = doc.get().to_dict()
        data[new_field_name] = data.pop(old_field_name)
        doc.update(data)

    def change_field_name_for_all_documents(self, collection_name: str, old_field_name: str, new_field_name: str,
                                            remove_old_field: bool = True):
        """
        Renames a field for all documents in a specified collection.

        :param collection_name: The name of the collection.
        :param old_field_name: The current name of the field.
        :param new_field_name: The new name for the field.
        :param remove_old_field: If True, the old field name is removed from the documents.
        """
        docs = self.db.collection(collection_name).stream()
        for doc in docs:
            data = doc.to_dict()
            if old_field_name not in data:
                continue
            data[new_field_name] = data.pop(old_field_name)
            doc.reference.update(data)
            if remove_old_field:
                doc.reference.update({old_field_name: firestore.DELETE_FIELD})

    def parse_field_from_string_to_float_for_all_documents(self, collection_name: str, field_name: str):
        """
        Parses a specified field from string to float for all documents in a collection.

        :param collection_name: The name of the collection.
        :param field_name: The name of the field to parse.
        """
        docs = self.db.collection(collection_name).stream()
        for doc in docs:
            data = doc.to_dict()
            if field_name not in data:
                continue
            data[field_name] = float(data[field_name])
            doc.reference.update(data)
