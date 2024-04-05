import json
import logging
import requests
from requests.auth import HTTPBasicAuth

log = logging.getLogger("py-bob")
log.setLevel(logging.INFO)


class BobClient:
    def __init__(self, service_account_id: str, service_account_token: str):
        self.api = "https://api.hibob.com/v1/"
        self.timeout = 30
        self.service_account_id = service_account_id
        self.service_account_token = service_account_token

    @staticmethod
    def parse_response(response):
        if (
            "Content-Type" in response.headers
            and response.headers["Content-Type"] != "application/json"
        ):
            log.debug("Response is not application/json, returning raw response")
            return response.text

        try:
            return response.json()
        except ValueError:
            log.debug("Could not convert response to json, returning raw response")

        return response

    def make_request(
        self, method, endpoint, json_body=None, query=None, body=None, files=None
    ):

        request = requests.get

        match method:
            case "GET":
                request = requests.get
            case "POST":
                request = requests.post
            case "PUT":
                request = requests.put
            case "DELETE":
                request = requests.delete

        request_params = {
            "headers": {
                "Accept": "application/json",
            },
            "json": json_body,
            "params": query,
            "data": body,
            "files": files,
            "timeout": self.timeout,
        }

        endpoint = self.api + endpoint

        response = request(
            endpoint,
            auth=HTTPBasicAuth(self.service_account_id, self.service_account_token),
            **request_params,
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            log.exception(error)
            log.debug(response)
            raise error

        response = self.parse_response(response)

        return response

    def get(self, endpoint, query=None, json_body=None, body=None):
        return self.make_request(
            "GET", endpoint, query=query, json_body=json_body, body=body
        )

    def post(self, endpoint, json_body=None, query=None, body=None, files=None):
        return self.make_request(
            "POST", endpoint, json_body=json_body, query=query, body=body, files=files
        )

    def put(self, endpoint, json_body=None, query=None, body=None, files=None):
        return self.make_request(
            "PUT", endpoint, json_body=json_body, query=query, body=body, files=files
        )

    def delete(self, endpoint, json_body=None, query=None, body=None, files=None):
        return self.make_request(
            "DELETE", endpoint, json_body=json_body, query=query, body=body, files=files
        )
