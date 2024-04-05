from .base import BobEndpoint
from typing import Optional, List


class TimeOff(BobEndpoint):
    def new_request(
        self,
        employeeId: str,
        policyType: str,
        startDate: str,
        requestRangeType: Optional[str] = None,
        startDatePortion: Optional[str] = None,
        endDate: Optional[str] = None,
        hours: Optional[int] = None,
        minutes: Optional[int] = None,
        endDatePortion: Optional[str] = None,
        dayPortion: Optional[str] = None,
        dailyHours: Optional[int] = None,
        dailyMinutes: Optional[int] = None,
        skipManagerApproval: Optional[bool] = None,
        approver: Optional[str] = None,
        description: Optional[str] = None,
        reasonCode: Optional[int] = None,
    ):
        """
        Submit a new time off request.

        Args:
            id (str): Employee ID.
            policyType (str): Request policy type, e.g. Holiday, Sick or any custom type defined.
            requestRangeType (str): The type of request duration.
                Select hours when the request is for X hours during the day requested (This is supported only for policy types measured in hours).
                Select portionOnRange when the request is for every morning or every afternoon during the days requested.
                Select hoursOnRange when the request is for X hours every day during the days requested (This is supported only for policy types measured in hours).
                Default: days
            days (str): Date of the first day of the time off (not relevant for requests using the hours type).
            startDatePortion (str): Portion of the first day - relevant for requests in days.
                Default: all_day
            endDate (str, optional): Date of the last day of the time off (not relevant for requests using the hours type).
            hours (int, optional): This field is mandatory if the requestRangeType is set to 'hours'.
            minutes (int, optional): Relevant if requestRangeType is set to 'hours'.
            endDatePortion (str, optional): Portion of the last day - relevant for requests in days.
                Default: all_day
            dayPortion (str, optional): Select morning when the request is for mornings on the days requested. Select afternoon when the request is for afternoons on the days requested.
                This is mandatory if the requestRangeType is portionOnRange.
            dailyHours (int, optional): Enter the number of hours when the request is for X hours on the days requested.
                This is mandatory if the requestRangeType is hoursOnRange.
            dailyMinutes (int, optional): Enter the number of minutes when the request is for X hours and X minutes on the days requested.
                This is relevant if the requestRangeType is hoursOnRange and the amount requested is not a full hour or hours.
            skipManagerApproval (bool, optional): Admins only can skip the approval policy. Setting this field to true will create an approved request.
                Default: False
            approver (str, optional): The employee ID of the user to be set as the approver for this request. This is relevant if 'skipManagerApproval' is set to true.
                Please note that the user calling the API with this param must have permission to import time off requests.
            description (str, optional): Request reason.
            reasonCode (int, optional): The reason code ID taken from the policy type's reason codes list. The list is available in GET /timeoff/policy-types/{policyType}/reason-codes

        Returns:
            200: Successfully submitted timeoff request.

        Reference:
            https://apidocs.hibob.com/reference/post_timeoff-employees-id-requests
        """

        json_body = {}

        json_body["policyType"] = policyType
        json_body["startDate"] = startDate

        if requestRangeType:
            json_body["requestRangeType"] = requestRangeType
        if startDatePortion:
            json_body["startDatePortion"] = startDatePortion
        if endDate:
            json_body["endDate"] = endDate
        if hours:
            json_body["hours"] = hours
        if minutes:
            json_body["minutes"] = minutes
        if endDatePortion:
            json_body["endDatePortion"] = endDatePortion
        if dayPortion:
            json_body["dayPortion"] = dayPortion
        if dailyHours:
            json_body["dailyHours"] = dailyHours
        if dailyMinutes:
            json_body["dailyMinutes"] = dailyMinutes
        if skipManagerApproval:
            json_body["skipManagerApproval"] = skipManagerApproval
        if approver:
            json_body["approver"] = approver
        if description:
            json_body["description"] = description
        if reasonCode:
            json_body["reasonCode"] = reasonCode

        return self.client.post(
            f"timeoff/employees/{employeeId}/requests", json_body=json_body
        )

    def new_diff_hours_request(
        self,
        employeeId: str,
        policyType: str,
        startDate: str,
        endDate: str,
        durations: List[dict],
        skipManagerApproval: Optional[bool] = None,
        approver: Optional[str] = None,
        description: Optional[str] = None,
        reasonCode: Optional[int] = None,
    ):
        """
        Submit a new time off request of different hours per day.

        Args:
            employeeId (str): Employee ID.
            policyType (str): Request policy type, e.g. Holiday, Sick or any custom type defined.
            startDate (str): Date of the first day of the time off.
            endDate (str): Date of the last day of the time off.
            durations (List[Dict[str, Union[str, int]]]): Array of durations for each day in the request.
                Each duration should be a dictionary with the following keys:
                - date (str): Date of the duration.
                - hours (int): The number of hours in the duration.
                - minutes (int): The number of minutes in the duration.
            skipManagerApproval (bool, optional): Admins only can skip the approval policy. Setting this field to true will create an approved request.
                Default: None
            approver (str, optional): The employee ID of the user to be set as the approver for this request. This is relevant if 'skipManagerApproval' is set to true.
                Please note that the user calling the API with this param must have permission to import time off requests.
                Default: None
            description (str, optional): Request reason.
                Default: None
            reasonCode (int, optional): The reason code ID taken from the policy type's reason codes list. The list is available in GET /timeoff/policy-types/{policyType}/reason-codes
                Default: None

        Returns:
            200: Successfully submitted timeoff request.

        Reference:
            https://apidocs.hibob.com/reference/post_timeoff-employees-id-diffhours-requests
        """

        json_body = {}

        json_body["policyType"] = policyType
        json_body["startDate"] = startDate
        json_body["endDate"] = endDate
        json_body["durations"] = durations

        if skipManagerApproval:
            json_body["skipManagerApproval"] = skipManagerApproval
        if approver:
            json_body["approver"] = approver
        if description:
            json_body["description"] = description
        if reasonCode:
            json_body["reasonCode"] = reasonCode

        return self.client.post(
            f"timeoff/employees/{employeeId}/diffHours/requests", json_body=json_body
        )

    def get_request_details(self, employeeId: str, requestId: int):
        """
        Get the details of an existing timeoff request.

        Args:
            employeeId (str): Employee ID.
            requestId (int): Request ID.

        Returns:
            200: Success.
            404: A request with the specified ID is not found for the specified employee.

        Reference:
            https://apidocs.hibob.com/reference/get_timeoff-employees-id-requests-requestid
        """
        return self.client.get(f"timeoff/employees/{employeeId}/requests/{requestId}")

    def cancel_request(self, employeeId: str, requestId: int):
        """
        Cancel an existing timeoff request.

        Args:
            employeeId (str): Employee ID.
            requestId (int): Request ID.

        Returns:
            200: Successfully canceled.

        Reference:
            https://apidocs.hibob.com/reference/delete_timeoff-employees-id-requests-requestid
        """
        return self.client.delete(
            f"timeoff/employees/{employeeId}/requests/{requestId}"
        )

    def get_requests_since_date(
        self, since: str, includePending: Optional[bool] = None
    ):
        """
        Get all new/deleted time off requests since the specified date.

        Args:
            since (str): Timestamp starting from which to return the changes.
            includePending (bool, optional): Indicates whether to include pending requests in the results.

        Returns:
            List: List of changes.

        Reference:
            https://apidocs.hibob.com/reference/get_timeoff-requests-changes
        """
        query = {}

        query["since"] = since

        if includePending:
            query["includePending"] = includePending

        return self.client.get("timeoff/requests/changes", query=query)

    def get_whos_out_of_office(
        self,
        fromDate: str,
        toDate: str,
        includeHourly: Optional[bool] = None,
        includePrivate: Optional[bool] = None,
        includePending: Optional[bool] = None,
    ):
        """
        Read a list of who's out of the office.

        Args:
            from_date (str): Start period date.
            to_date (str): End period date.
            include_hourly (bool, optional): Include Hourly Requests. Default: False.
            include_private (bool, optional): Show the policy type's name instead of the policy's custom public name if the user has permission to view it, and the policy's custom public name exists. Default: False.
            include_pending (bool, optional): Include Pending Requests. Default: False.

        Returns:
            List: Time off requests as seen by the logged in user for a given date range.

        Reference:
            https://apidocs.hibob.com/reference/get_timeoff-whosout
        """
        query = {}

        query["from"] = fromDate
        query["to"] = toDate

        if includeHourly:
            query["includeHourly"] = includeHourly
        if includePrivate:
            query["includePrivate"] = includePrivate
        if includePending:
            query["includePending"] = includePending

        return self.client.get("timeoff/whosout", query=query)

    def get_whos_out_of_office_today(
        self,
        includeHourly: Optional[bool] = None,
        includePrivate: Optional[bool] = None,
        siteId: Optional[int] = None,
    ):
        """
        Read a list of who's out of the office today

        Args:
            includeHourly (bool, optional): Include Hourly Requests.
            includePrivate (bool, optional): Show the policy type's name instead of the policy's custom public name if the user has permission to view it, and the policy's custom public name exists.
            siteId (int, optional): The employee's site ID.

        Returns:
            List: Time off requests as seen by the logged in user for today

        Reference:
            https://apidocs.hibob.com/reference/get_timeoff-outtoday
        """
        query = {}

        if includeHourly is not None:
            query["includeHourly"] = includeHourly
        if includePrivate is not None:
            query["includePrivate"] = includePrivate
        if siteId is not None:
            query["siteId"] = siteId

        return self.client.get("timeoff/outtoday", query=query)

    def get_policy_type_reason_codes(self, policyType: str):
        """
        Get the list of reason codes for a given policy type.

        Args:
            policyType (str): Policy Type name.

        Returns:
            200: List of reason codes.

        Raises:
            404: A policy type with the specified name was not found.

        Reference:
            https://apidocs.hibob.com/reference/get_timeoff-policy-types-policytype-reason-codes
        """
        return self.client.get(f"timeoff/policy-types/{policyType}/reason-codes")

    def add_reason_codes(self, policyType: str, reasonCodes: List[str]):
        """
        Add a list of reason codes for a given policy type.

        Args:
            policyType (str): Policy Type name.
            reasonCodes (List[str]): List of reason codes to be added.

        Returns:
            200: Submitted successfully.

        Raises:
            404: A policy type with the specified name was not found.

        Reference:
            https://apidocs.hibob.com/reference/post_timeoff-policy-types-policytype-reason-codes
        """
        json_body = {}

        json_body["reasonCodes"] = reasonCodes

        return self.client.post(
            f"timeoff/policy-types/{policyType}/reason-codes", json_body=json_body
        )

    def get_policy_type_details(self, policyType: str):
        """
        Get details about a given policy type.

        Args:
            policyType (str): Policy Type name.

        Returns:
            200: Policy type details.

        Raises:
            404: A policy type with the specified name was not found.

        Reference:
            https://apidocs.hibob.com/reference/get_timeoff-policy-types-policytype
        """
        return self.client.get(f"timeoff/policy-types/{policyType}")

    def get_policy_types(self):
        """
        Get a list of all policy type names.

        Returns:
            List: List of policy type names.

        Reference:
            https://apidocs.hibob.com/reference/get_timeoff-policy-types
        """
        return self.client.get("timeoff/policy-types")

    def get_policy_details(self, policyName: str):
        """
        Get details about a given policy.

        Args:
            policyName (str): Policy name.

        Returns:
            200: Policy details.
            404: A policy with the specified name was not found.

        Reference:
            https://apidocs.hibob.com/reference/get_timeoff-policies
        """
        query = {}

        query["policyName"] = policyName

        return self.client.get(f"timeoff/policies", query=query)

    def get_policy_names(self, policyTypeName: str):
        """
        Get a list of policy names for a given policy type.

        Args:
            policyTypeName (str): Policy type name.

        Returns:
            List: List of policy names.

        Reference:
            https://apidocs.hibob.com/reference/get_timeoff-policies-names
        """
        query = {}

        query["policyTypeName"] = policyTypeName

        return self.client.get("timeoff/policies/names", query=query)

    def get_employee_balance(self, employeeId: str, policyType: str, date: str):
        """
        Get the balance for a given employee, for a given policy type, as of a given date.

        Args:
            employeeId (str): Employee ID.
            policyType (str): Policy type name.
            date (str): Point in time.

        Returns:
            200: Balance result.
            Default: Unexpected error.

        Reference:
            https://apidocs.hibob.com/reference/get_timeoff-employees-id-balance
        """
        query = {}

        query["policyType"] = policyType
        query["date"] = date

        return self.client.get(f"timeoff/employees/{employeeId}/balance", query=query)

    def create_balance_adjustment(
        self,
        employeeId: str,
        adjustmentType: Optional[str] = None,
        policyType: Optional[str] = None,
        effectiveDate: Optional[str] = None,
        amount: Optional[float] = None,
        reason: Optional[str] = None,
    ):
        """
        Create a balance adjustment for a given employee for a given effective date.

        Args:
            employeeId (str): Employee ID.
            adjustmentType (str): Adjustment type - balance or time used.
            policyType (str): Policy type name.
            effectiveDate (str): The date this adjustment becomes effective.
            amount (float): The amount of days/hours to add/subtract.
            reason (str): A reason for this adjustment.

        Returns:
            200: Success.
            Default: Unexpected error.

        Reference:
            https://apidocs.hibob.com/reference/post_timeoff-employees-id-adjustments
        """
        json_body = {}

        if adjustmentType:
            json_body["adjustmentType"] = adjustmentType
        if policyType:
            json_body["policyType"] = policyType
        if effectiveDate:
            json_body["effectiveDate"] = effectiveDate
        if amount:
            json_body["amount"] = amount
        if reason:
            json_body["reason"] = reason

        return self.client.post(
            f"timeoff/employees/{employeeId}/adjustments", json_body=json_body
        )
