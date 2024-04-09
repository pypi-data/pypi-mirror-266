import httpx
import os
from pprint import pprint


class OpenAIChat:
    def __init__(self, model: str = 'gpt3', env: str = 'test'):
        self.auth = httpx.BasicAuth(os.environ['OPENAI_USER'], os.environ['OPENAI_PASSWORD'])
        model_name = 'openai_v1_gpt_35_turbo' if model == 'gpt3' else 'openai_gpt_4'
        self.domain = f'http://gateway.mpi.{env}.shopee.io/ufs/v1'
        self.url = f'{self.domain}/{model_name}/chat/completions'

    def get_model_list(self):
        url = f'{self.domain}/openai_v1_models'
        resp = httpx.get(url, auth=self.auth)
        return resp.json()

    def chat(self, message_json: dict):
        resp = httpx.post(self.url, auth=self.auth, json=message_json)
        return resp.json()


a = OpenAIChat().get_model_list()
pprint(a)
