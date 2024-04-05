from .base import BobEndpoint
from typing import Optional, List

class Documents(BobEndpoint):
    def upload_document(
        self,
        employeeId: str,
        folderId: str = "shared",
        documentName: Optional[str] = None,
        documentUrl: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ):
        """
        Upload a document to the employee's folder.

        Args
            id: Employee ID.
            folderId: Folder ID. Possible values are shared, confidential, or custom.
            document_name: Document name.
            document_url: URL of the document to upload.
            tags: A list of tags to associate with the document.

        Responses
            200: Upload success.

        References:
            https://apidocs.hibob.com/reference/post_docs-people-id-shared
        """
        json_body = {}

        endpoint = f"docs/people/{employeeId}/shared"

        match folderId.lower():
            case "shared":
                endpoint = endpoint
            case "confidential":
                endpoint = f"docs/people/{employeeId}/confidential"
            case _:
                endpoint = f"docs/people/{employeeId}/custom/{folderId}"

        if documentName:
            json_body["documentName"] = documentName
        if documentUrl:
            json_body["documentUrl"] = documentUrl
        if tags:
            json_body["tags"] = tags

        return self.client.post(endpoint, json_body=json_body)

    def upload_file(self, employeeId: str, file: str, folderId: str = "shared"):
        """
        Upload a file to the employee's folder.

        Args:
            employeeId (str): Employee ID.
            file (file): The file to upload.

        Returns:
            200: Uploaded document ID.

        Raises:
            Exception: Unexpected error.

        References:
            https://apidocs.hibob.com/reference/post_docs-people-id-shared-upload
            https://apidocs.hibob.com/reference/post_docs-people-id-confidential-upload
            https://apidocs.hibob.com/reference/post_docs-people-id-folders-folderid-upload
        """
        endpoint = f"docs/people/{employeeId}/shared/upload"

        match folderId.lower():
            case "shared":
                endpoint = endpoint
            case "confidential":
                endpoint = f"docs/people/{employeeId}/confidential/upload"
            case _:
                endpoint = f"docs/people/{employeeId}/folders/{folderId}/upload"

        return self.client.post(
            endpoint, files={"file": file}
        )

    def delete_document(self, employeeId: str, docId: str, folderId: str):
        """
        Delete a specific document from the employee's shared folder.

        Args:
            employeeId (str): Employee ID.
            docId (str): Document ID.

        Returns:
            200: Delete success.

        Raises:
            Exception: Unexpected error.

        References:
            https://apidocs.hibob.com/reference/delete_docs-people-id-shared-docid
            https://apidocs.hibob.com/reference/delete_docs-people-id-confidential-docid
            https://apidocs.hibob.com/reference/delete_docs-people-id-folders-folderid-docid
        """

        endpoint = f"docs/people/{employeeId}/shared/{docId}"

        match folderId.lower():
            case "shared":
                endpoint = endpoint
            case "confidential":
                endpoint = f"docs/people/{employeeId}/confidential/{docId}"
            case _:
                endpoint = f"docs/people/{employeeId}/folders/{folderId}/{docId}"

        return self.client.delete(endpoint)

    def download_documents(self, employeeId: str):
        """
        Download employee's documents.

        Args:
            employeeId (str): Employee ID.

        Returns:
            List[Dict]: A list of documents' names and download links.

        Raises:
            Exception: Unexpected error.

        References:
            https://apidocs.hibob.com/reference/get_docs-people-id
        """

        return self.client.get(f"docs/people/{employeeId}")
