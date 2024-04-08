from __future__ import annotations

from typing import Callable

from google.cloud.firestore_v1 import DocumentReference, DocumentSnapshot

from .firestore_base import FirestoreBase

Validator = Callable[[dict], None]


class DocumentManager(FirestoreBase):

    def __init__(self, credentials_path: str, database: str = None):
        """
        Initializes the DocumentManager instance.

        :param credentials_path: Path to the Google Cloud service account credentials JSON file.
        :param database: Optional database URL. If provided, this database is used instead of the default.
        """
        super().__init__(credentials_path=credentials_path, database=database)

    def create_doc_ref(self, collection_name: str, document_name: str = None,
                       parent_ref: DocumentReference = None) -> DocumentReference:
        """
        Creates a document reference for a specific document in a collection.

        :param collection_name: The name of the collection.
        :param document_name: Optional name of the document.
        :param parent_ref: Optional parent document reference.

        :return: A DocumentReference object for the specified document.
        """
        parent_ref = parent_ref or self.db
        return parent_ref.collection(collection_name).document(document_name)

    def add_document(self, collection_name: str, data: dict, document_name: str = None, id_as_name: bool = False,
                     validator: Validator = None, merge_if_existing: bool = False,
                     parent_ref: DocumentReference = None) -> str:
        """
        Adds a new document to a specified collection.

        :param collection_name: The name of the collection.
        :param data: The data for the document as a dictionary.
        :param document_name: Optional specific name for the document. Required if id_as_name is False.
        :param id_as_name: If True, a unique ID will be generated for the document name.
        :param validator: Optional callable that validates the data dictionary.
        :param merge_if_existing: If True, merge data into an existing document instead of overwriting.
        :param parent_ref: Optional parent document reference for the new document.

        :return: The name of the document.
        """
        if not document_name and not id_as_name:
            raise ValueError('document_name must be provided if id_as_name is False')
        if document_name and id_as_name:
            raise ValueError('document_name will be ignored if id_as_name is True')
        if validator:
            validator(data)
        parent_ref = parent_ref or self.db
        if id_as_name:
            document_name = parent_ref.collection(collection_name).document().id
        parent_ref.collection(collection_name).document(document_name).set(data, merge=merge_if_existing)
        return document_name

    def add_documents_batch(self, collection_name: str, data_list: list[dict], document_names: list[str] = None,
                            validator: Validator = None, overwrite: bool = False, verbose: bool = False,
                            parent_ref: DocumentReference = None):
        """
        Adds or updates multiple documents in a specified collection using batch operations.

        :param collection_name: The collection to which documents will be added.
        :param data_list: List of data dictionaries for each document.
        :param document_names: Optional list of names for each document. Must match the length of data_list if provided.
        :param validator: Optional callable to validate each document's data.
        :param overwrite: If True, existing documents will be overwritten. If False, they will be ignored.
        :param verbose: If True, print additional information during the operation.
        """
        parent_ref = parent_ref or self.db
        existing_doc_names = self.get_document_names(collection_name, parent_ref=parent_ref)
        max_batch_size = 500  # Firestore's limit

        chunks = [data_list[i:i + max_batch_size] for i in range(0, len(data_list), max_batch_size)]
        name_chunks = [document_names[i:i + max_batch_size] if document_names else None for i in
                       range(0, len(document_names or []), max_batch_size)]

        for chunk_index, chunk in enumerate(chunks):
            batch = parent_ref.batch()
            names_chunk = name_chunks[chunk_index] if name_chunks else [None] * len(chunk)

            for index, data in enumerate(chunk):
                if validator:
                    validator(data)

                document_name = names_chunk[index] if names_chunk else None
                if document_name is None or document_name not in existing_doc_names or overwrite:
                    doc_ref = parent_ref.collection(collection_name).document(document_name)
                    batch.set(doc_ref, data)
                elif verbose:
                    print(f"Document with name '{document_name}' already exists. Skipping...")

            try:
                batch.commit()
                if verbose:
                    print(f"Batch {chunk_index + 1} write successful.")
            except Exception as e:
                print(f"Batch {chunk_index + 1} write failed: {e}")

    def add_data(self, collection_name: str, data: dict, parent_ref: DocumentReference = None):
        parent_ref = parent_ref or self.db
        parent_ref.collection(collection_name).add(data)

    def get_document(self, collection_name: str, document_name: str,
                     parent_ref: DocumentReference = None) -> DocumentSnapshot:
        """
        Retrieves a document from a specified collection.

        :param collection_name: The name of the collection.
        :param document_name: The name of the document to retrieve.
        :param parent_ref: Optional parent document reference.

        :return: A DocumentSnapshot object of the retrieved document.
        """
        parent_ref = parent_ref or self.db
        return parent_ref.collection(collection_name).document(document_name).get()

    def update_document(self, collection_name: str, document_name: str, data: dict, validator: Validator = None,
                        create_if_missing: bool = False, parent_ref: DocumentReference = None):
        """
        Updates a document in a specified collection. Optionally creates the document if it does not exist.

        :param collection_name: The name of the collection.
        :param document_name: The name of the document to update.
        :param data: The data to update the document with.
        :param validator: Optional callable to validate the data dictionary.
        :param create_if_missing: If True, create the document if it does not exist.
        :param parent_ref: Optional parent document reference.
        """
        if create_if_missing:
            return self.add_document(collection_name, data, document_name, validator=validator, merge_if_existing=True,
                                     parent_ref=parent_ref)
        else:
            if validator:
                validator(data)
            parent_ref = parent_ref or self.db
            parent_ref.collection(collection_name).document(document_name).update(data)

    def delete_document(self, collection_name: str, document_name: str, parent_ref: DocumentReference = None):
        """
        Deletes a specific document from a collection.

        :param collection_name: The name of the collection containing the document.
        :param document_name: The name of the document to delete.
        :param parent_ref: Optional parent document reference.
        """
        parent_ref = parent_ref or self.db
        parent_ref.collection(collection_name).document(document_name).delete()

    def get_document_names(self, collection_name: str, parent_ref: DocumentReference = None) -> list[str]:
        """
        Retrieves the names of all documents in a specified collection.

        :param collection_name: The name of the collection.
        :param parent_ref: Optional parent document reference.

        :return: A list of document names in the specified collection.
        """
        parent_ref = parent_ref or self.db
        return [doc.id for doc in parent_ref.collection(collection_name).stream()]

    def get_document_data(self, collection_name: str, document_name: str, with_id: bool = False,
                          parent_ref: DocumentReference = None) -> dict:
        """
        Retrieves the data of a specified document in a collection.

        :param collection_name: The name of the collection.
        :param document_name: The name of the document.
        :param with_id: If True, includes the document's ID in the returned dictionary.
        :param parent_ref: Optional parent document reference.

        :return: A dictionary containing the document's data.
        """
        parent_ref = parent_ref or self.db
        document = parent_ref.collection(collection_name).document(document_name).get()
        if with_id:
            return {'id': document.id, **document.to_dict()}
        else:
            return document.to_dict()
