import os

from . import resources
from ._request import RequestAPI


class OpenAI:


    chat = resources.Chat
    images = resources.Images
    request_api = RequestAPI()

    def __init__(self, api_key=None, base_url=None):
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")

        if api_key is None:
            print("The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable") #TODO raise exception

        self.api_key = api_key
        self.request_api.update_api_key(api_key)

        if base_url is None:
            base_url = os.environ.get("OPENAI_BASE_URL")
        if base_url is None:
            base_url = "https://trainings.boltiot.com/api/aitools/" #TODO

        self.images = resources.Images()
