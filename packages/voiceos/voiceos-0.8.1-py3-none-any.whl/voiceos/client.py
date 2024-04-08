from voiceos.configuration import Configuration
from voiceos.api_client import ApiClient
from voiceos.api.agents_api import AgentsApi
from voiceos.api.calls_api import CallsApi
from voiceos.api.phone_numbers_api import PhoneNumbersApi

class VoiceOS:
    def __init__(self, api_key):
        self.configuration = Configuration(
            host="https://api.wako.ai",
        )

        self.client = ApiClient(
            configuration=self.configuration,
            header_name="X-API-KEY",
            header_value=api_key,
        )

        self.agents = AgentsApi(self.client)

        self.calls = CallsApi(self.client)

        self.phone_numbers = PhoneNumbersApi(self.client)