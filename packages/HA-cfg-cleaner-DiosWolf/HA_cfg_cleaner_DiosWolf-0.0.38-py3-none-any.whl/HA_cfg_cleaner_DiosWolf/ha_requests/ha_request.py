from requests import post, Response
from HA_cfg_cleaner_DiosWolf.data_classes_json.file_config import HostInfo


class HARequests:
    def __init__(self, configuration: HostInfo, api_key: str):
        self.configuration = configuration
        self.api_key = api_key

    def __set_header_auth(self, headers: dict[str, any]) -> dict[str, any]:
        auth_headers = {"Authorization": self.api_key}
        auth_headers = auth_headers | headers
        return auth_headers

    def post_requests(
        self, url: str, data: dict[str, any], headers: dict[str, any] = {}
    ) -> Response:
        auth_headers = self.__set_header_auth(headers)
        with post(url, headers=auth_headers, json=data) as resp:
            return resp
