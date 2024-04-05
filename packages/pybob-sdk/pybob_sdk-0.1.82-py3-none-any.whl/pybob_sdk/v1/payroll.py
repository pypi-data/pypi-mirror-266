from .base import BobEndpoint
from typing import Optional


class Payroll(BobEndpoint):
    def read_history(
        self, department: Optional[str] = None, showInactive: Optional[bool] = None
    ):
        """
        Read payroll history.

        Args
           department (str): Filter payroll for specific department.
           showInactive (bool): Whether to include inactive employees in the response.

        Returns
            200: Payroll data.
            Default: Unexpected error

        References:
            https://apidocs.hibob.com/reference/get_payroll-history
        """
        query = {}

        query["department"] = department
        query["showInactive"] = showInactive

        return self.client.get("payroll/history", query=query)
