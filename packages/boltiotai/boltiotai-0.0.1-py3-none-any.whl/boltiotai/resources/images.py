import json
from .._request import RequestAPI, HttpMethod

class ImageResponse:
    def __init__(self, response):
        self.data = response.get("data", [])
        self.message = response.get("message", "")
        self.error = response.get("error", "")

class Images:


    URL = 'https://trainings.boltiot.com/api/aitools/v1/images/generations'

    request_api = RequestAPI()
    def __init__(self, api_key=None):
        self.api_key = api_key

    def generate(self, model, prompt, n=1, size="256x256", response_format="url"):
        data = {
            "model":model,
            "prompt":prompt,
            "n":n,
            "size":size,
            "response_format": response_format
        }
        response = self.request_api._make_request(self.URL, HttpMethod.POST, data)
        return ImageResponse(response)
        
    
