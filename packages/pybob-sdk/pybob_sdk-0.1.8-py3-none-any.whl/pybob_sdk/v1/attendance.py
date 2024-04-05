from .base import BobEndpoint
from typing import List


class Attendance(BobEndpoint):
    def import_attendance_data(
        self, importMethod: str, idType: str, requests: List[dict], dateTimeFormat: str
    ):
        """
        Import attendance data.

        Args:
            import_method (str): Indicates if the provided data should be processed via an aggregation engine or immediately.
                 Possible values: "aggregate" or "immediate".
            id_type (str): The ID type used to identify the employee.
               Possible values: "bobId", "email", "idInCompany", or a custom field.
               For custom fields, use a forward slash separator.
            requests (list[dict]): List of attendance events.
                id (str): The id from the idType
                clockIn (str): timestamp
                clockOut (str): timestamp
            dateTimeFormat (str): Allows to set custom date format for the date-time values sent in the requests.

        Returns:
            None

        References:
            https://apidocs.hibob.com/reference/post_attendance-import-importmethod
        """
        json_body = {}

        json_body["idType"] = idType
        json_body["requests"] = requests
        json_body["dateTimeFormat"] = dateTimeFormat

        return self.client.post(
            f"attendance/import/{importMethod}", json_body=json_body
        )
