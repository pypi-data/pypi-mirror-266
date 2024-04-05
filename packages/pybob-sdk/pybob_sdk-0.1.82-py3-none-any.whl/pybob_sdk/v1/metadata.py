from .base import BobEndpoint
from typing import Optional, List
from .models.Metadata import BobField


class Metadata(BobEndpoint):
    @property
    def lists(self):
        return Lists(self.client)

    @property
    def fields(self):
        return Fields(self.client)

    @property
    def tables(self):
        return Tables(self.client)

    @property
    def positions(self):
        return Positions(self.client)


class Lists(BobEndpoint):
    def get(
        self, listName: Optional[str] = None, includeArchived: Optional[bool] = None
    ) -> dict:
        """
        Get company lists, defaults to get all

        Args:
            listName (str, optional): The internal name of the list (default: None)
            includeArchived (bool, optional): Whether to include archived items in the response (default: None)

        Returns:
            dict: A dictionary containing the response from the API
        """
        json_body = {}
        endpoint = "company/named-lists/"
        if listName:
            endpoint = f"company/named-lists/{listName}"
        if includeArchived:
            json_body["includeArchived"] = includeArchived
        return self.client.get(endpoint, json_body=json_body)

    def add_item(
        self, listName: str, name: str, parentId: Optional[str] = None
    ) -> dict:
        """
        Add a new item to an existing list

        Args:
            listName (str): The name of the list
            name (str): The name of the item to add to the list
            parentId (str, optional): The ID of the new hierarchy parent node.

        Returns:
            dict: A dictionary containing the response from the API
        """
        json_body = {}

        json_body["name"] = name
        if parentId:
            json_body["parentId"] = parentId

        return self.client.post(f"company/named-lists/{listName}", json_body=json_body)

    def update_item(
        self,
        listName: str,
        itemId: str,
        name: Optional[str] = None,
        parentId: Optional[str] = None,
    ):
        """
        Update an existing list item

        Args:
            listName (str): The name of the list
            itemId (str): The ID of the item to update
            name (str, optional): The new name of the item. Providing a name will rename the list item value.
            parentId (str, optional): The ID of the new hierarchy parent node. Providing the parent ID will move the hierarchy list item (together with its children) under the indicated parent node.

        Returns:
            200 response: The item was updated successfully
            404 response: The item was not found
        """
        json_body = {}

        if name:
            json_body["name"] = name
        if parentId:
            json_body["parentId"] = parentId

        return self.client.put(
            f"company/named-lists/{listName}/{itemId}", json_body=json_body
        )

    def delete_item(self, listName: str, itemId: str):
        """
        Delete an existing list item

        Args:
            listName (str): The name of the list
            itemId (str): The ID of the item to delete

        Returns:
            200 response: The item was deleted successfully
            404 response: The item was not found
        """
        return self.client.delete(f"company/named-lists/{listName}/{itemId}")


class Fields(BobEndpoint):
    def get(self) -> List[dict]:
        """
        Get all company fields

        Returns:
            List[dict]: A list of dictionaries
        """
        return self.client.get("company/people/fields")

    def create_field(
        self,
        name: str,
        category: str,
        type: str,
        description: Optional[str] = None,
        historical: Optional[str] = None,
    ):
        """
        Create a new field.

        Args:
            name (str): The name of the field.
            category (str): The category of the field.
            type (str): The type of field. Supported field types: text, text-area, number, date, list, multi-list, hierarchy-list, currency, employee-reference, document.
            description (str, optional): The description of the field.
            historical (str, optional): When true, this field keeps the history of its values, each being active starting from a certain date. The default value is false.

        Returns:
            200 response: The new field was successfully created. The ID of the field is returned.
            400 response: If the category of the field is root, or historical is set to true, but the category doesn't allow it, or if the field type is not supported.
            404 response: If the category of the field doesn't exist.
        """
        json_body = {}

        field = BobField(
            name=name,
            category=category,
            type=type.lower(),
            description=description,
            historical=historical,
        )

        json_body["name"] = field.name
        json_body["category"] = field.category
        json_body["type"] = field.type
        if description:
            json_body["description"] = field.description
        if historical:
            json_body["historical"] = field.historical

        return self.client.post("company/people/fields", json_body=json_body)

    def update_field(
        self,
        fieldId: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """
        Update an existing field

        Args:
            fieldId (str): The ID of the field to update
            name (str, optional): The name of the field
            description (str, optional): The description of the field

        Returns:
            200 response: The field was updated successfully
            404 response: The field was not found
        """
        json_body = {}

        if name:
            json_body["name"] = name
        if description:
            json_body["description"] = description

        return self.client.put(f"company/people/fields/{fieldId}", json_body=json_body)

    def delete_field(self, fieldId: str):
        """
        Delete an existing field

        Args:
            fieldId (str): The ID of the field to delete

        Returns:
            200 response: The field was deleted successfully
            400 response: If the field is a Bob default field
            404 response: The field was not found
        """
        return self.client.delete(f"company/people/fields/{fieldId}")


class Tables(BobEndpoint):
    def read(self, custom_table_id: Optional[str] = None):
        """
        Read metadata of custom tables defined
        """

        endpoint = "people/custom-tables/metadata"

        if custom_table_id:
            endpoint = f"people/custom-tables/metadata/{custom_table_id}"

        return self.client.get(endpoint)


class Positions(BobEndpoint):
    def get(self):
        """
        Get all company positions

        Returns:
            List[dict]: A list of dictionaries
        """
        return self.client.get("metadata/objects/position")
