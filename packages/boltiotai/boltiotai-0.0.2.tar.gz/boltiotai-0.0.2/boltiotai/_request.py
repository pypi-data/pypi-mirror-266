import json
import requests

class HttpMethod:
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class RequestAPI:
    api_key = None

    @classmethod
    def update_api_key(cls, api_key):
        cls.api_key = api_key

    def _make_request(self, url, method, data):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, data=json.dumps(data), headers=headers)

        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return json.loads(response.text)
