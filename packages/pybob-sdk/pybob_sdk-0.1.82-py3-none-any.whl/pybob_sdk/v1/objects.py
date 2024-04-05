from .base import BobEndpoint
from typing import Optional, List


class Objects(BobEndpoint):
    def read_company_positions(
        self,
        fields: List[str],
        filters: List[dict],
        includeHumnaReadable: Optional[bool] = None,
    ):
        """
        Read company positions.

        Args
            fields: Array of field ids (paths) to fetch for the positions.
            filters: array of objects
            includeHumanReadable (bool)

        RESPONSES:
            200: Positions

        References:
            https://apidocs.hibob.com/reference/post_objects-position-search
        """
        json_body = {}

        json_body["fields"] = fields
        json_body["filters"] = filters

        if includeHumnaReadable:
            json_body["includeHumanReadable"] = includeHumnaReadable

        return self.client.post("objects/position/search", json_body=json_body)
