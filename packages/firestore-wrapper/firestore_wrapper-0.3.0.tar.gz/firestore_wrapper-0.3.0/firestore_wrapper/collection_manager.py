from __future__ import annotations

from google.cloud.firestore_v1 import DocumentReference, DocumentSnapshot

from .firestore_base import FirestoreBase


class CollectionManager(FirestoreBase):

    def __init__(self, credentials_path: str, database: str = None, collections: list[str] = None):
        """
        Initializes the CollectionManager instance.

        :param credentials_path: Path to the Google Cloud service account credentials JSON file.
        :param database: Optional database URL. If provided, this database is used instead of the default.
        :param collections: Optional list of collection names to initialize.
        """
        super().__init__(credentials_path=credentials_path, database=database)
        if collections:
            self.init_collections(collections)

    def add_collection(self, collection_name: str, parent_ref: DocumentReference = None):
        """
        Adds a new collection to the Firestore database.

        :param collection_name: The name of the collection to add.
        :param parent_ref: Optional parent collection reference.
        """
        parent_ref = parent_ref or self.db
        parent_ref.collection(collection_name)

    def init_collections(self, collections: list[str], parent_ref: DocumentReference = None):
        """
        Initializes multiple collections in the Firestore database.

        :param collections: A list of collection names to initialize.
        :param parent_ref: Optional parent collection reference.
        """
        for collection in collections:
            self.add_collection(collection, parent_ref=parent_ref)

    def get_collection(self, collection_name: str, parent_ref: DocumentReference = None) -> list[DocumentSnapshot]:
        """
        Retrieves all documents from a specified collection.

        :param collection_name: The name of the collection to retrieve documents from.
        :param parent_ref: Optional parent collection reference.

        :return: A list of DocumentSnapshot objects for each document in the collection.
        """
        parent_ref = parent_ref or self.db
        return parent_ref.collection(collection_name).get()

    def delete_collection(self, collection_name: str, parent_ref: DocumentReference = None):
        """
        Deletes an entire collection, including all documents within it.

        :param collection_name: The name of the collection to delete.
        :param parent_ref: Optional parent collection reference.
        """
        parent_ref = parent_ref or self.db
        docs = parent_ref.collection(collection_name).stream()
        for doc in docs:
            doc.reference.delete()

    def get_collection_size(self, collection_name: str, parent_ref: DocumentReference = None) -> int:
        """
        Returns the number of documents in a collection.

        :param collection_name: The name of the collection.
        :param parent_ref: Optional parent collection reference.

        :return: The number of documents in the specified collection.
        """
        parent_ref = parent_ref or self.db
        return len(parent_ref.collection(collection_name).get())

    def get_collection_names(self, parent_ref: DocumentReference = None) -> list[str]:
        """
        Retrieves the names of all collections in the Firestore database.

        :param parent_ref: Optional parent collection reference.

        :return: A list of collection names.
        """
        parent_ref = parent_ref or self.db
        return [collection.id for collection in parent_ref.collections()]

    def get_collection_data(self, collection_name: str, with_id: bool = False,
                            parent_ref: DocumentReference = None) -> list[dict]:
        """
        Retrieves data for all documents in a specified collection.

        :param collection_name: The name of the collection.
        :param with_id: If True, includes each document's ID with its data.
        :param parent_ref: Optional parent collection reference.

        :return: A list of dictionaries, each containing data for a document in the collection.
        """
        parent_ref = parent_ref or self.db
        collection = parent_ref.collection(collection_name).stream()
        if with_id:
            return [{'id': doc.id, **doc.to_dict()} for doc in collection]
        else:
            return [doc.to_dict() for doc in collection]

    def get_collection_data_as_dict(self, collection_name: str, parent_ref: DocumentReference = None) -> dict:
        """
        Retrieves data for all documents in a specified collection, organized as a dictionary.

        :param collection_name: The name of the collection.
        :param parent_ref: Optional parent collection reference.

        :return: A dictionary with document IDs as keys and document data dictionaries as values.
        """
        parent_ref = parent_ref or self.db
        collection = parent_ref.collection(collection_name).stream()
        ret = {doc.id: doc.to_dict() for doc in collection}
        return ret
