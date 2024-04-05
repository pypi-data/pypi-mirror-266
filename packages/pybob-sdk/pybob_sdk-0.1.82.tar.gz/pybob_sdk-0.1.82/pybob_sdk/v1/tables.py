from .base import BobEndpoint
from typing import Optional


class Tables(BobEndpoint):
    def read_all_entries(
        self,
        employeeId: str,
        customTableId: str,
        includeHumanReadable: Optional[bool] = None,
    ):
        """
        Read all entries of the given custom table.

        Args:
            employee_id (str): Employee ID.
            custom_table_id (str): The ID of the custom table.
            include_human_readable (bool, optional): Whether to include the additional "humanReadable" JSON node in the response. Defaults to False.

        Returns:
            dict: The response body as a dictionary.

        References:
            https://apidocs.hibob.com/reference/get_people-custom-tables-employee-id-custom-table-id
        """
        query = {}

        if includeHumanReadable:
            query["includeHumanReadable"] = includeHumanReadable

        return self.client.get(
            f"people/custom-tables/{employeeId}/{customTableId}", query=query
        )

    def create_custom_table_entry(
        self, employeeId: str, customTableId: str, rawBody: Optional[str] = None
    ):
        """
        Create a new entry in the custom table.

        Args:
            employee_id (str): Employee ID.
            custom_table_id (str): The ID of the custom table.
            raw_body (str): The raw body of the request.

        Returns:
            200: Entry created successfully

        References:
            https://apidocs.hibob.com/reference/post_people-custom-tables-employee-id-custom-table-id
        """

        json_body = {}

        if rawBody:
            json_body["rawBody"] = rawBody

        return self.client.post(
            f"people/custom-tables/{employeeId}/{customTableId}", json_body=json_body
        )

    def update_custom_table_entry(
        self,
        employeeId: str,
        customTableId: str,
        entryId: str,
        rawBody: Optional[str] = None,
    ):
        """
        Update a custom table entry.

        Args:
            employee_id (str): Employee ID.
            custom_table_id (str): The ID of the custom table.
            entry_id (str): The ID of the custom table entry.
            raw_body (str, optional): The raw body of the request.

        Returns:
            200: Entry updated succesfully

        References:
            https://apidocs.hibob.com/reference/put_people-custom-tables-employee-id-custom-table-id-entry-id
        """
        json_body = {}
        if rawBody:
            json_body["rawBody"] = rawBody

        return self.client.put(
            f"people/custom-tables/{employeeId}/{customTableId}/{entryId}",
            json_body=json_body,
        )

    def delete_custom_table_entry(
        self, employeeId: str, customTableId: str, entryId: str
    ) -> dict:
        """
        Delete a custom table entry.

        Args:
            employee_id (str): Employee ID.
            custom_table_id (str): The ID of the custom table.
            entry_id (str): The ID of the custom table entry.

        Returns:
            200: Entry deleted successfully

        References:
            https://apidocs.hibob.com/reference/delete_people-custom-tables-employee-id-custom-table-id-entry-id
        """
        return self.client.delete(
            f"people/custom-tables/{employeeId}/{customTableId}/{entryId}"
        )
