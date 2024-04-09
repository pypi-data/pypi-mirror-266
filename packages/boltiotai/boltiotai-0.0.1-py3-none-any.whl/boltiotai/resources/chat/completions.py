from ..._request import HttpMethod, RequestAPI

class Completions:

    URL = 'https://trainings.boltiot.com/api/aitools/v1/chats/completions'
    request_api = RequestAPI()
    def __init__(self, api_key=None):
        self.api_key = api_key

    def create(self, model, messages):
        return self.call_openai_chat(model, messages)

    def call_openai_chat(self, model, messages):
        data = {
            "model":model,
            "messages":messages
        }

        response = self.request_api._make_request(self.URL, HttpMethod.POST, data)
        return response

