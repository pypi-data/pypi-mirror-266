from .base import BobEndpoint
from .models.People import (
    SearchModel,
    FilterModel,
    HumanReadableValues,
    TerminationReasonType,
)
from .models.Payroll import (
    PayFrequency,
    PayPeriod,
    Base,
    ExcercisePrice,
    VariablePayPeriod,
)
from pydantic import ValidationError
from typing import Optional, List
import json


class People(BobEndpoint):
    def search(
        self,
        fields: Optional[List[str]] = None,
        filters: Optional[List[FilterModel]] = None,
        showInactive: Optional[bool] = None,
        humanReadable: Optional[str] = None,
    ) -> List[dict]:
        """
        This API returns a list of requested employees with requested fields. The data is filtered based on the requested fields and access level of the logged-in user. Only viewable categories are returned.

        Args:
            fields (array of strings): Optional array of employee field paths that are required in response. If not specified, only basic fields and categories are returned.

            filters (array of objects): Optional list of filters for filtering employees. Currently only one filter is supported by the Bob API.

            showInactive (bool): Optional field. Default value is False. Defines whether the response should include inactive employees.

            humanReadable (str): Optional field. Default value is None. Defines whether the response should include human-readable values. Possible values are "APPEND" and "REPLACE". If not sent, machine-readable values will be supplied.

        References:
            https://apidocs.hibob.com/reference/post_people-search
        """

        if humanReadable:
            humanReadable = humanReadable.lower()

        search_parameters = SearchModel(
            fields=fields,
            filters=filters,
            showInactive=showInactive,
            humanReadable=humanReadable,
        )

        json_body = {}

        if search_parameters.fields:
            json_body["fields"] = search_parameters.fields
        if search_parameters.filters:
            json_body["filters"] = [
                filter.model_dump() for filter in search_parameters.filters
            ]
        if search_parameters.showInactive:
            json_body["showInactive"] = search_parameters.showInactive
        if search_parameters.humanReadable:
            json_body["humanReadable"] = search_parameters.humanReadable

        return self.client.post("people/search", json_body=json_body)

    def read(self, sortBy: Optional[str] = None):
        """
        Read the public profile section of all active employees.

        Args:
            sortBy (str): Optional field name to sort by. This defaults to firstName.

        Returns:
            Employee profiles

        References:
            https://apidocs.hibob.com/reference/get_profiles
        """

        return self.client.get("profiles", query={"sortBy": sortBy})

    @property
    def employee(self):
        return Employee(self.client)


class Employee(BobEndpoint):
    def get(
        self,
        identifier: str,
        fields: Optional[List[str]] = None,
        humanReadable: Optional[str] = None,
    ) -> dict:
        """
        Read company people by id or email

        Returns the employee by the specified id or email.

        Args:
            identifier (str): employee id or email
            fields (array of strings): Optional array of employee field paths that are required in response.
            humanReadable (str): Optional field. Defines whether the response should include human-readable values. Possible values are "APPEND" and "REPLACE".

        References:
            https://apidocs.hibob.com/reference#get_people-identifier
        """
        json_body = {}

        if fields:
            json_body["fields"] = fields
        if humanReadable:
            humanReadable = HumanReadableValues(humanReadable.lower())
            json_body["humanReadable"] = humanReadable

        return self.client.post(f"people/{identifier}", json_body=json_body)

    def create(
        self,
        firstName: str,
        surname: str,
        email: str,
        site: str,
        startDate: str,
        **kwargs,
    ):
        """
        Create a new employee

        Args:
            firstName (str): employee's first name
            surname (str): employee's surname
            email (str): employee's email
            site (str): site name
            startDate (str): employee's start date in the format "YYYY-MM-DD"

        References:
            https://apidocs.hibob.com/reference/post_people
        """
        json_body = {}

        json_body["firstName"] = firstName
        json_body["surname"] = surname
        json_body["email"] = email
        json_body["work"] = {"site": site, "startDate": startDate}

        for key, value in kwargs.items():
            json_body[key] = value

        return self.client.post(
            "people",
            json_body={
                "firstName": firstName,
                "surname": surname,
                "email": email,
                "work": {"site": site, "startDate": startDate},
            },
        )

    def update(self, identifier: str, **kwargs):
        """
        Update an employee

        Args:
            identifier (str): employee id or email

        Returns:
            - 200: Employee updated successfully.
            - 304: If employee data not modified.

        References:
            https://apidocs.hibob.com/reference/put_people-identifier
        """
        json_body = {}

        for key, value in kwargs.items():
            json_body[key] = value

        return self.client.put(f"people/{identifier}", json_body=json_body)

    def revoke(self, identifier: str):
        """
        Revoke employee access

        Args:
            identifier (str): employee id or email

        Returns:
            - 200: Employee revoked successfully.

        References:
            https://apidocs.hibob.com/reference/delete_people-identifier
        """
        return self.client.post(f"employees/{identifier}/uninvite")

    def terminate(
        self,
        identifier: str,
        terminationDate: str,
        terminationReason: Optional[str] = None,
        reasonType: Optional[str] = None,
        noticePeriod: Optional[dict] = None,
        lastDayOfWork: Optional[str] = None,
    ):
        """
        Terminate an employee

        Args:
            identifier (str): employee id or email
            terminationDate (str): termination date in the format "YYYY-MM-DD"
            terminationReason (str): termination reason
            reasonType (str): termination reason type
            noticePeriod (dict): notice period
            lastDayOfWork (str): last day of work in the format "YYYY-MM-DD"

        Returns:
            - 200: Employee terminated successfully.

        References:
            https://apidocs.hibob.com/reference/post_people-identifier-terminate
        """
        json_body = {}

        json_body["terminationDate"] = (terminationDate,)

        if terminationReason:
            json_body["terminationReason"] = terminationReason
        if reasonType:
            reasonType = TerminationReasonType(reasonType.lower())
            json_body["reasonType"] = reasonType
        if noticePeriod:
            json_body["noticePeriod"] = noticePeriod
        if lastDayOfWork:
            json_body["lastDayOfWork"] = lastDayOfWork

        return self.client.post(
            f"employees/{identifier}/terminate", json_body=json_body
        )

    def invite(self, employeeId: str, welcomeWizardId: int):
        """
        Invite an employee

        Args:
            employeeId (str): employee id
            welcomeWizardId (int): welcome wizard id

        Returns:
            - 200: Employee invited successfully.

        References:
            https://apidocs.hibob.com/reference/post_employees-employeeid-invitations
        """
        json_body = {}

        json_body["welcomeWizardId"] = welcomeWizardId

        return self.client.post(
            f"employees/{employeeId}/invitations", json_body=json_body
        )

    def set_start_date(
        self, employeeId: str, startDate: str, reason: Optional[str] = None
    ):
        """
        Set or update an employee's start date

        Args:
            employeeId (str): employee id
            startDate (str): employee's start date in the format "YYYY-MM-DD"
            reason (str): Additional info for the start date update

        Returns:
            - 200: Employee start date set successfully.

        References:
            https://apidocs.hibob.com/reference/post_people-identifier-setstartdate
        """
        json_body = {}

        json_body["startDate"] = startDate

        if reason:
            json_body["reason"] = reason

        return self.client.post(
            f"employees/{employeeId}/start-date", json_body=json_body
        )

    def get_avatar(
        self, email: Optional[str] = None, employeeId: Optional[str] = None
    ) -> str:
        """
        Read avatar for an employee email or employeeId

        Returns the avatar image URL of the employee.

        Args:
            email (str): Employee email
            employeeId (str): Employee ID

        Returns:
            str: URL of the employee avatar.

        References:
            GET https://api.hibob.com/v1/avatars
        """
        endpoint = "avatars"
        query = {}

        if employeeId:
            endpoint = f"avatars/{employeeId}"
        if email:
            query = {"email": email}

        return self.client.get(endpoint, query=query)

    def upload_avatar(self, employeeId: str, url: str):
        """
        Upload an avatar for an employee

        Args:
            employeeId (str): employee id
            url (str): URL of the avatar

        Returns:
            - 200: Avatar uploaded successfully.

        References:
            https://apidocs.hibob.com/reference/put_avatars-employeeid
        """
        return self.client.put(f"avatars/{employeeId}", json_body={"url": url})

    def update_email(self, employeeId: str, email: str):
        """
        Update an employee's email

        Args:
            employeeId (str): employee id
            email (str): new email

        Returns:
            - 200: Employee email updated successfully.

        References:
            https://apidocs.hibob.com/reference/put_people-id-email
        """
        return self.client.put(f"people/{employeeId}/email", json_body={"email": email})

    def list_work_history(self, employeeId: str):
        """
        List an employee's work history

        Args:
            employeeId (str): employee id

        Returns:
            - 200: Employee work history.

        References:
            https://apidocs.hibob.com/reference/get_people-id-work
        """
        return self.client.get(f"people/{employeeId}/work")

    def create_work_entry(
        self,
        employeeId: str,
        effectiveDate: str,
        title: Optional[str] = None,
        department: Optional[str] = None,
        id: Optional[int] = None,
        reason: Optional[str] = None,
        site: Optional[str] = None,
        siteId: Optional[int] = None,
        reportsTo: Optional[dict] = None,
        customColumns: Optional[dict] = None,
    ):
        """
        Create a new work entry for a given employee.

        Args:
            employeeId (str): Employee ID.
            effectiveDate (str): The date this entry becomes effective.
            title (str): The employee's job title.
            department (str): The employee's department.
            id (int): ID of the work entry.
            reason (str): The reason for this change.
            site (str): The employee's site.
            siteId (int): The employee's site ID.
            reportsTo (dict): The manager's details.
            customColumns (dict): Custom columns for the work entry.

        Returns:
            - 200: Entry created successfully.

        References:
            https://apidocs.hibob.com/reference/post_people-id-work
        """
        json_body = {}

        json_body["effectiveDate"] = effectiveDate

        if id:
            json_body["id"] = id
        if reason:
            json_body["reason"] = reason
        if title:
            json_body["title"] = title
        if department:
            json_body["department"] = department
        if site:
            json_body["site"] = site
        if siteId:
            json_body["siteId"] = siteId
        if reportsTo:
            json_body["reportsTo"] = reportsTo
        if customColumns:
            json_body["customColumns"] = customColumns

        return self.client.post(f"people/{employeeId}/work", json_body=json_body)

    def update_work_entry(
        self,
        employeeId: str,
        entryId: int,
        effectiveDate: str,
        id: Optional[int] = None,
        title: Optional[str] = None,
        department: Optional[str] = None,
        reason: Optional[str] = None,
        site: Optional[str] = None,
        siteId: Optional[int] = None,
        reportsTo: Optional[dict] = None,
        customColumns: Optional[dict] = None,
    ):
        """
        Update a work entry from employee's work history

        Args:
            employeeId (str): Employee ID.
            entryId (int): The entry ID to update.
            effectiveDate (str): The date this entry becomes effective.
            title (str): The employee's job title.
            department (str): The employee's department.
            reason (str): The reason for this change.
            site (str): The employee's site.
            siteId (int): The employee's site ID.
            reportsTo (dict): The manager's details.
            customColumns (dict): Custom columns for the work entry.

        Returns:
            - 200: Entry updated successfully.
            - 404: Requested entry not found. Nothing was changed.

        References:
            https://apidocs.hibob.com/reference/put_people-id-work-entry-id
        """
        json_body = {}
        json_body["effectiveDate"] = effectiveDate

        if id:
            json_body["id"] = id
        if reason:
            json_body["reason"] = reason
        if title:
            json_body["title"] = title
        if department:
            json_body["department"] = department
        if site:
            json_body["site"] = site
        if siteId:
            json_body["siteId"] = siteId
        if reportsTo:
            json_body["reportsTo"] = reportsTo
        if customColumns:
            json_body["customColumns"] = customColumns

        return self.client.put(
            f"people/{employeeId}/work/{entryId}", json_body=json_body
        )

    def delete_work_entry(self, employeeId: str, entryId: int):
        """
        Deletes a work entry from a given employee's work history.

        Args:
            employeeId (str): Employee ID.
            entryId (int): The entry ID to delete.

        Returns:
            - 200: Entry deleted successfully.

        References:
            https://api.hibob.com/v1/people/{id}/work/{entry_id}
        """
        return self.client.delete(f"people/{employeeId}/work/{entryId}")

    def list_employment_history(self, employeeId: str):
        """
        List an employee's employment history

        Args:
            employeeId (str): employee id

        Returns:
            - 200: Employee employment history.

        References:
            https://api.hibob.com/v1/people/{id}/employment
        """
        return self.client.get(f"people/{employeeId}/employment")

    def create_employment_entry(
        self,
        employeeId: str,
        effectiveDate: str,
        id: Optional[int] = None,
        reason: Optional[str] = None,
        contract: Optional[str] = None,
        type: Optional[str] = None,
        salaryPayType: Optional[str] = None,
    ):
        """
        Create a new employment entry for a given employee.

        Args:
            employeeId (str): Employee ID.
            id (int): ID of the employment entry.
            effectiveDate (str): The date this entry becomes effective.
            reason (str): The reason for this change.
            contract (str): Contract.
            type (str): Type.
            salaryPayType (str): Salary pay type.

        Returns:
            - 200: Entry created successfully.

        References:
            https://apidocs.hibob.com/reference/post_people-id-employment
        """
        json_body = {}
        json_body["effectiveDate"] = effectiveDate

        if id:
            json_body["id"] = id
        if reason:
            json_body["reason"] = reason
        if contract:
            json_body["contract"] = contract
        if type:
            json_body["type"] = type
        if salaryPayType:
            json_body["salaryPayType"] = salaryPayType

        return self.client.post(f"people/{employeeId}/employment", json_body=json_body)

    def update_employment_entry(
        self,
        employeeId: str,
        entryId: int,
        effectiveDate: str,
        id: Optional[int] = None,
        reason: Optional[str] = None,
        contract: Optional[str] = None,
        type: Optional[str] = None,
        salaryPayType: Optional[str] = None,
    ):
        """
        Update an employment entry from a given employee's employment history

        Args:
            employeeId (str): Employee ID.
            entryId (int): The entry ID to update.
            effectiveDate (str): The date this entry becomes effective.
            id (int): ID.
            reason (str): The reason for this change.
            contract (str): Contract.
            type (str): Type.
            salaryPayType (str): Salary pay type.

        Returns:
            - 200: Entry updated successfully.
            - 404: Requested entry not found. Nothing was changed.

        References:
            https://apidocs.hibob.com/reference/put_people-id-employment-entry-id
        """
        json_body = {}
        json_body["effectiveDate"] = effectiveDate

        if id:
            json_body["id"] = id
        if reason:
            json_body["reason"] = reason
        if contract:
            json_body["contract"] = contract
        if type:
            json_body["type"] = type
        if salaryPayType:
            json_body["salaryPayType"] = salaryPayType

        return self.client.put(
            f"people/{employeeId}/employment/{entryId}", json_body=json_body
        )

    def delete_employment_entry(self, employeeId: str, entryId: int):
        """
        Deletes an employment entry from a given employee's employment history.

        Args:
            employeeId (str): Employee ID.
            entryId (int): The entry ID to delete.

        Returns:
            - 200: Entry deleted successfully.

        References:
            https://apidocs.hibob.com/reference/delete_people-id-employment-entry-id
        """
        return self.client.delete(f"people/{employeeId}/employment/{entryId}")

    def list_lifecycle_history(self, employeeId: str):
        """
        List an employee's life-cycle status history.

        Args:
            employeeId (str): Employee ID.

        Returns:
            - 200: List of life-cycle history entries.

        References:
            https://apidocs.hibob.com/reference/get_people-id-lifecycle
        """
        return self.client.get(f"people/{employeeId}/lifecycle")

    def list_salary_history(self, employeeId: str):
        """
        List an employee's salary history.

        Args:
            employeeId (str): Employee ID.

        Returns:
            - 200: List of salary entries.

        References:
            https://apidocs.hibob.com/reference/get_people-id-salaries
        """
        return self.client.get(f"people/{employeeId}/salaries")

    def create_salary_entry(
        self,
        employeeId: str,
        effectiveDate: str,
        base: dict,
        payPeriod: str,
        payFrequency: Optional[str] = None,
        id: Optional[int] = None,
        reason: Optional[str] = None,
    ):
        """
        Create a new salary entry for a given employee.

        Args:
            employeeId (str): Employee ID.
            id (int): ID of the salary entry.
            reason (str): The reason for this change.
            effectiveDate (str): The date this entry becomes effective.
            base (dict): Base salary details. Includes value and currency code.
            payPeriod (str): Represents the period for this salary entry. This can be one of: Annual, Hourly, Daily, Weekly, Monthly.
            payFrequency (str): Represents the frequency the salary is paid. This can be one of: Weekly, Monthly, Pro rata, Every two weeks, Twice a month, Every four weeks.

        Returns:
            - 200: Entry added successfully.

        References:
            https://api.hibob.com/v1/people/{id}/salaries
        """
        json_body = {}
        json_body["effectiveDate"] = effectiveDate
        json_body["base"] = Base(
            value=base["value"], currency=base["currency"]
        ).model_dump_json()
        json_body["payPeriod"] = PayPeriod(payPeriod).value

        if id:
            json_body["id"] = id
        if reason:
            json_body["reason"] = reason
        if payFrequency:
            json_body["payFrequency"] = PayFrequency(payFrequency).value

        return self.client.post(f"people/{employeeId}/salaries", json_body=json_body)

    def delete_salary_entry(self, employeeId: str, entryId: int):
        """
        Deletes a salary entry from the employee's list.

        Args:
            employeeId (str): Employee ID.
            entryId (int): The entry ID to delete.

        Returns:
            - 200: Entry deleted successfully.

        References:
            https://apidocs.hibob.com/reference/delete_people-id-salaries-entry-id
        """
        return self.client.delete(f"people/{employeeId}/salaries/{entryId}")

    def list_equity_grants(self, employeeId: str):
        """
        List the employee's equity grants.

        Args:
            employeeId (str): Employee ID.

        Returns:
            - 200: List of equity grants.

        References:
            https://apidocs.hibob.com/reference/get_people-id-equities
        """
        return self.client.get(f"people/{employeeId}/equities")

    def create_equity_grant(
        self,
        employeeId: str,
        effectiveDate: str,
        quantity: float,
        equityType: str,
        excerisePrice: dict,
        id: Optional[int] = None,
        reason: Optional[str] = None,
        vestingCommencementDate: Optional[str] = None,
        consentNumber: Optional[str] = None,
        grantDate: Optional[str] = None,
        optionExpiration: Optional[str] = None,
        vestingTerm: Optional[str] = None,
        grantType: Optional[str] = None,
        vestingSchedule: Optional[float] = None,
        grantNumber: Optional[float] = None,
        grantStatus: Optional[str] = None,
    ):
        """
        Create a new equity grant for a given employee.

        Args:
            employeeId (str): Employee ID.
            equityGrant (dict): Equity grant details.

            id (int): ID.
            reason (str): The reason for this change.
            effectiveDate (str): The date this entry becomes effective.
            quantity (float): The number of equities granted.
            equityType (str): The type of the grant.
            vestingCommencementDate (str): Vesting commencement date.
            consentNumber (str): Consent number.
            grantDate (str): Date the equity was granted.
            optionExpiration (str): Date the options expire.
            exercisePrice (dict): Exercise price details.
                value (float): The value of the exercise price.
                currency (str): Three-letter currency code.
            vestingTerm (str): Terms for exercising this grant.
            grantType (str): Grant type. One of: Initial Grant, Merit Grant
            vestingSchedule (float): The vesting schedule ID assigned to this grant.
            grantNumber (float): The Grant number for employee.
            grantStatus (str): Grant status. One of: Granted, Pending Approval

        Returns:
            - 200: Entry added successfully.

        References:
            https://apidocs.hibob.com/reference/post_people-id-equities
        """
        json_body = {}

        json_body["effectiveDate"] = effectiveDate
        json_body["quantity"] = quantity
        json_body["equityType"] = equityType
        json_body["exercisePrice"] = ExcercisePrice(
            value=excerisePrice["value"], currency=excerisePrice["currency"]
        ).model_dump_json()

        if id:
            json_body["id"] = id
        if reason:
            json_body["reason"] = reason
        if vestingCommencementDate:
            json_body["vestingCommencementDate"] = vestingCommencementDate
        if consentNumber:
            json_body["consentNumber"] = consentNumber
        if grantDate:
            json_body["grantDate"] = grantDate
        if optionExpiration:
            json_body["optionExpiration"] = optionExpiration
        if vestingTerm:
            json_body["vestingTerm"] = vestingTerm
        if grantType:
            json_body["grantType"] = grantType
        if vestingSchedule:
            json_body["vestingSchedule"] = vestingSchedule
        if grantNumber:
            json_body["grantNumber"] = grantNumber
        if grantStatus:
            json_body["grantStatus"] = grantStatus

        return self.client.post(f"people/{employeeId}/equities", json_body=json_body)

    def update_equity_grant(
        self,
        employeeId: str,
        entryId: int,
        effectiveDate: str,
        quantity: float,
        equityType: str,
        excerisePrice: dict,
        id: Optional[int] = None,
        reason: Optional[str] = None,
        vestingCommencementDate: Optional[str] = None,
        consentNumber: Optional[str] = None,
        grantDate: Optional[str] = None,
        optionExpiration: Optional[str] = None,
        vestingTerm: Optional[str] = None,
        grantType: Optional[str] = None,
        vestingSchedule: Optional[float] = None,
        grantNumber: Optional[float] = None,
        grantStatus: Optional[str] = None,
    ):
        """
        Update an equity grant for a given employee.

        Args:
            employeeId (str): Employee ID.
            entryId (int): entry ID to update
            id (int): ID.
            reason (str): The reason for this change.
            effectiveDate (str): The date this entry becomes effective.
            quantity (float): The number of equities granted.
            equityType (str): The type of the grant.
            vestingCommencementDate (str): Vesting commencement date.
            consentNumber (str): Consent number.
            grantDate (str): Date the equity was granted.
            optionExpiration (str): Date the options expire.
            exercisePrice (dict): Exercise price details.
                value (float): The value of the exercise price.
                currency (str): Three-letter currency code.
            vestingTerm (str): Terms for exercising this grant.
            grantType (str): Grant type. One of: Initial Grant, Merit Grant
            vestingSchedule (float): The vesting schedule ID assigned to this grant.
            grantNumber (float): The Grant number for employee.
            grantStatus (str): Grant status. One of: Granted, Pending Approval

        Returns:
            - 200: Entry updated successfully.

        References:
            https://apidocs.hibob.com/reference/put_people-id-equities-entry-id
        """
        json_body = {}

        json_body["effectiveDate"] = effectiveDate
        json_body["quantity"] = quantity
        json_body["equityType"] = equityType
        json_body["exercisePrice"] = ExcercisePrice(
            value=excerisePrice["value"], currency=excerisePrice["currency"]
        ).model_dump_json()

        if id:
            json_body["id"] = id
        if reason:
            json_body["reason"] = reason
        if vestingCommencementDate:
            json_body["vestingCommencementDate"] = vestingCommencementDate
        if consentNumber:
            json_body["consentNumber"] = consentNumber
        if grantDate:
            json_body["grantDate"] = grantDate
        if optionExpiration:
            json_body["optionExpiration"] = optionExpiration
        if vestingTerm:
            json_body["vestingTerm"] = vestingTerm
        if grantType:
            json_body["grantType"] = grantType
        if vestingSchedule:
            json_body["vestingSchedule"] = vestingSchedule
        if grantNumber:
            json_body["grantNumber"] = grantNumber
        if grantStatus:
            json_body["grantStatus"] = grantStatus

        return self.client.put(
            f"people/{employeeId}/equities/{entryId}", json_body=json_body
        )

    def delete_equity_grant(self, employeeId: str, entryId: int):
        """
        Deletes an equity grant for an employee.

        Args:
            employeeId (str): Employee ID.
            entryId (int): The Entry ID to delete.

        Returns:
            - 200: Entry deleted successfully.

        References:
            https://apidocs.hibob.com/reference/delete_people-id-equities-entry-id
        """
        return self.client.delete(f"people/{employeeId}/equities/{entryId}")

    def list_variable_payments(self, employeeId: str) -> List[dict]:
        """
        List employee's variable payments.

        Args:
            employeeId (str): Employee ID.

        Returns:
            List[dict]: List of variable payments.

        References:
            https://apidocs.hibob.com/reference/get_people-id-variable
        """
        return self.client.get(f"people/{employeeId}/variable")

    def create_variable_payment(
        self,
        employeeId: str,
        effectiveDate: str,
        amount: dict,
        paymentPeriod: str,
        id: Optional[int] = None,
        reason: Optional[str] = None,
        variableType: Optional[str] = None,
        companyPercent: Optional[float] = None,
        departmentPercent: Optional[float] = None,
        individualPercent: Optional[float] = None,
    ):
        """
        Creates a new variable payment for a given employee.

        Args:
            employeeId (str): Employee ID.
            id (int): ID.
            reason (str): The reason for this change.
            effectiveDate (str): The date this entry becomes effective.
            amount (dict): Variable payment amount details.
                value (float): The value of the variable payment.
                currency (str): Three-letter currency code.
            variableType (str): The type of variable pay.
            paymentPeriod (str): This represents the period for this variable entry. It can be one of: Annual, Half-Yearly, Quarterly, Monthly.
            companyPercent (float): The employee's company on-target weight, in percent.
            departmentPercent (float): The employee's department on-target weight, in percent.
            individualPercent (float): The employee's individual on-target weight, in percent.

        Returns:
            - 200: Entry added successfully.

        References:
            https://apidocs.hibob.com/reference/post_people-id-variable
        """
        json_body = {}
        json_body["effectiveDate"] = effectiveDate
        json_body["amount"] = Base(
            value=amount["value"], currency=amount["currency"]
        ).model_dump_json()
        json_body["paymentPeriod"] = VariablePayPeriod(paymentPeriod).value

        if id:
            json_body["id"] = id
        if reason:
            json_body["reason"] = reason
        if variableType:
            json_body["variableType"] = variableType
        if companyPercent:
            json_body["companyPercent"] = companyPercent
        if departmentPercent:
            json_body["departmentPercent"] = departmentPercent
        if individualPercent:
            json_body["individualPercent"] = individualPercent

        return self.client.post(f"people/{employeeId}/variable", json_body=json_body)

    def delete_variable_record(self, employeeId: str, entryId: int):
        """
        Deletes a variable record for an employee.

        Args:
            employeeId (str): Employee ID.
            entryId (int): The Entry ID to delete.

        Returns:
            - 200: Entry deleted successfully.

        References:
            https://apidocs.hibob.com/reference/delete_people-id-variable-entry-id
        """
        return self.client.delete(f"people/{employeeId}/variable/{entryId}")

    def list_training_records(self, employeeId: str) -> List[dict]:
        """
        List the employee's training records.

        Args:
            employeeId (str): Employee ID.

        Returns:
            List[dict]: List of training records.

        References:
            https://apidocs.hibob.com/reference/get_people-id-training
        """
        return self.client.get(f"people/{employeeId}/training")

    def create_training_record(
        self,
        employeeId: str,
        effectiveDate: str,
        cost: dict,
        name: str,
        description: Optional[str] = None,
        id: Optional[int] = None,
        reason: Optional[str] = None,
        startDate: Optional[str] = None,
        endDate: Optional[str] = None,
        documentId: Optional[int] = None,
    ):
        """
        Creates a new training record for a given employee.

        Args:
            employeeId (str): Employee ID.
            id (int): ID.
            reason (str): The reason for this change.
            effectiveDate (str): The date this entry becomes effective.
            name (str): The name of the training entry. The name must be an item in the training list field.
            description (str, optional): Further description about the training entry. Defaults to None.
            cost (dict): Cost object. Defaults to None.
                value (float): The value of the cost.
                currency (str): Three-letter currency code.
            status (str): The status of the training entry.
            frequency (str): The frequency of the training entry.
            startDate (str, optional): The date this entry becomes effective. Defaults to None.
            endDate (str, optional): The date of training completion. Defaults to None.
            documentId (int, optional): ID of the document attached to this training entry. Defaults to None.

        Returns:
            - 200: Entry added successfully.

        References:
            https://apidocs.hibob.com/reference/post_people-id-training
        """
        json_body = {}

        json_body["effectiveDate"] = effectiveDate
        json_body["name"] = name
        json_body["cost"] = Base(
            value=cost["value"], currency=cost["currency"]
        ).model_dump_json()

        if description:
            json_body["description"] = description
        if cost:
            json_body["cost"] = cost
        if id:
            json_body["id"] = id
        if reason:
            json_body["reason"] = reason
        if startDate:
            json_body["startDate"] = startDate
        if endDate:
            json_body["endDate"] = endDate
        if documentId:
            json_body["documentId"] = documentId

        return self.client.post(f"people/{employeeId}/training", json_body=json_body)

    def delete_training_record(self, employeeId: str, entryId: int):
        """
        Deletes a training record for an employee.

        Args:
            employeeId (str): Employee ID.
            entryId (int): The Entry ID to delete.

        Returns:
            - 200: Entry deleted successfully.

        References:
            https://apidocs.hibob.com/reference/delete_people-id-training-entry-id
        """
        return self.client.delete(f"people/{employeeId}/training/{entryId}")
