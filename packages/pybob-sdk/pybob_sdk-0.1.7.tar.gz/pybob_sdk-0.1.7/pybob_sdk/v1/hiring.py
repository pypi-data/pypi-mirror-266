from .base import BobEndpoint
from typing import Optional, List
from typing import Optional, List


class Hiring(BobEndpoint):
    def get_job_ads(
        self,
        fields: List[str],
        filters: List[dict],
        preferredLanguage: Optional[str] = None,
    ):
        """
        Get a list of all active job ads.

        Args:
            fields (List[str]): List of field ids (paths) to fetch for job ads. Minimum 1 up to 50 fields.
                       Any invalid number of fields will get a response of 400 HTTP error.
            filters (List[dict]): List of filters to apply to the job ads.
            preferredLanguage (Optional[str]): Preferred language code for the language results will be returned in if available,
                            otherwise language specified on the job ad will be used.

        Returns:
            List[dict]: The list of job ads.

        References:
            https://apidocs.hibob.com/reference/post_hiring-job-ads
        """

        query = {}
        json_body = {}

        if preferredLanguage:
            query["preferredLanguage"] = preferredLanguage

        json_body["fields"] = fields
        json_body["filters"] = filters

        return self.client.post("hiring/job-ads", query=query, json=json_body)

    def get_job_ad_details(self, id: str, preferredLanguage: Optional[str] = None):
        """
        Get the details of the job ad.

        Args:
            id (str): Job Ad ID.
            preferredLanguage (str): Preferred language code for the language results will be returned in if available,
                                    otherwise language specified on the job ad will be used.

        Returns:
            dict: The details of the job ad.

        References:
            https://apidocs.hibob.com/reference/get_hiring-job-ads-id
        """
        query = {}

        if preferredLanguage:
            query["preferredLanguage"] = preferredLanguage

        return self.client.get(f"hiring/job-ads/{id}", query=query)
