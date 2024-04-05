from .bob_client import BobClient
from .v1 import (
    people,
    onboarding,
    reports,
    tasks,
    metadata,
    timeoff,
    attendance,
    payroll,
    documents,
    hiring,
    tables,
    objects,
)


class Bob:
    def __init__(self, service_account_id: str, service_account_token: str):
        self.client = BobClient(
            service_account_id=service_account_id,
            service_account_token=service_account_token,
        )

    @property
    def people(self):
        """
        This class represents the People endpoint of the Bob API.
        It provides methods to search for people.
        Methods
        -------
        search(
            fields: Optional[List[str]] = None,
            filters: Optional[List[FilterModel]] = None,
            showInactive: Optional[bool] = None,
            humanReadable: Optional[str] = None
        ):
        This API returns a list of requested employees with requested fields. The data is filtered based on the requested fields and access level of the provided credentials. Only viewable categories are returned.
        """
        return people.People(self.client)

    @property
    def onboarding(self):
        return onboarding.Onboarding(self.client)

    @property
    def reports(self):
        return reports.Reports(self.client)

    @property
    def tasks(self):
        return tasks.Tasks(self.client)

    @property
    def metadata(self):
        return metadata.Metadata(self.client)

    @property
    def time_off(self):
        return timeoff.TimeOff(self.client)

    @property
    def attendance(self):
        return attendance.Attendance(self.client)

    @property
    def payroll(self):
        return payroll.Payroll(self.client)

    @property
    def documents(self):
        return documents.Documents(self.client)

    @property
    def hiring(self):
        return hiring.Hiring(self.client)

    @property
    def tables(self):
        return tables.Tables(self.client)

    @property
    def objects(self):
        return objects.Objects(self.client)
