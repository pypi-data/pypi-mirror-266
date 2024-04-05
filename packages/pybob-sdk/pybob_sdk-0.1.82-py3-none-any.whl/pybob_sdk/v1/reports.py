from .base import BobEndpoint
from .models.Reports import ReportFormat
from typing import Optional


class Reports(BobEndpoint):
    def read(self):
        """
        Returns a list of all the defined company reports.

        The data is filtered based on the access level of the service account.

        Only viewable categories are returned.

        References:
            https://apidocs.hibob.com/reference/get_company-reports
        """
        return self.client.get("company/reports")

    def download(
        self,
        reportId: int,
        format: str,
        includeInfo: Optional[bool] = False,
        locale: Optional[str] = None,
        humanReadable: Optional[str] = None,
    ):
        """
        Download the report by ID

        Args:
            reportId (int): The ID of the report to download.
            format (str): The file format of the downloaded report.
            includeInfo (bool, optional): Whether to include additional information in the report. Default is False.
            locale (str, optional): The requested language for the report columns in the format of locale (e.g. fr-FR).
            humanReadable (str, optional): Optional field. Only enforced when format is json.
                           If not sent: supply machine-readable values only.
                           Possible values: APPEND, REPLACE

        Returns:
            file: The report data file in the specified format.

        References:
            https://apidocs.hibob.com/reference/get_company-reports-reportid-download
        """
        query = {}

        query["format"] = ReportFormat(format).value

        if includeInfo:
            query["includeInfo"] = includeInfo
        if locale:
            query["locale"] = locale
        if humanReadable:
            query["humanReadable"] = humanReadable

        return self.client.get(f"company/reports/{reportId}/download", query=query)

    def get_report_download_url(
        self,
        reportId: int,
        format: str,
        includeInfo: bool = False,
        locale: Optional[str] = None,
        humanReadable: Optional[str] = None,
    ):
        """
        Get the report download URL for polling.

        Args:
            reportId (int): The ID of the report.
            format (str): The file format of the report.
            includeInfo (bool, optional): Whether to include additional information in the report. Default is False.
            locale (str, optional): The requested language for the report columns in the format of the locale (e.g. fr-FR).
            humanReadable (str, optional): Optional field. Only enforced when format is json.
                           If not sent: supply machine-readable values only.
                           Possible values: APPEND, REPLACE

        Returns:
            str: The polling URL for the report file.

        References:
            https://apidocs.hibob.com/reference/get_company-reports-reportid-download-async
        """
        query = {"format": format}

        if includeInfo:
            query["includeInfo"] = includeInfo
        if locale:
            query["locale"] = locale
        if humanReadable:
            query["humanReadable"] = humanReadable

        response = self.client.get(
            f"company/reports/{reportId}/download-async", query=query
        )

        return response.headers.get("Location")

    def download_report_by_url(self, reportName: str):
        """
        Download the report by report name

        Args:
            reportName (str): The name return of get_report_download_url function (.split('/')[-1])

        Returns:
            200 - file: The report data file when it is ready.
            204: Report isn't ready try again soon.

        References:
            https://apidocs.hibob.com/reference/get_company-reports-download-reportname
        """

        return self.client.get(f"company/reports/download/{reportName}")
