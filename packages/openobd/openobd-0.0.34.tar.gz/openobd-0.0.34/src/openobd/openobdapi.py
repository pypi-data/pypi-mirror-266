import requests


class OpenObdApiClientConfiguration:

    _endpoint_url = None            # type:str
    _api_key = None                 # type: str
    _client_id = None               # type: str
    _client_secret = None           # type: str
    _access_token = None

    def __init__(self, endpoint_url: str, api_key: str, client_id=None, client_secret=None):
        self._endpoint_url = endpoint_url
        self._api_key = api_key
        self._client_id = client_id
        self._client_secret = client_secret

    @property
    def endpoint_url(self):
        return self._endpoint_url

    @property
    def api_key(self):
        return self._api_key

    @property
    def client_id(self):
        return self._client_id

    @property
    def client_secret(self):
        return self._client_secret

    @endpoint_url.setter
    def endpoint_url(self, value):
        self._endpoint_url = value

    @api_key.setter
    def api_key(self, value):
        self._api_key = value

    @client_id.setter
    def client_id(self, value):
        self._client_id = value

    @client_secret.setter
    def client_secret(self, value):
        self._client_secret = value

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        self._access_token = value


class OpenObdApi:

    _client_configuration = None

    def __init__(self, endpoint_url: str, api_key: str):
        self.client_configuration = OpenObdApiClientConfiguration(endpoint_url, api_key)

    @property
    def client_configuration(self) -> OpenObdApiClientConfiguration:
        return self._client_configuration

    @client_configuration.setter
    def client_configuration(self, value: OpenObdApiClientConfiguration) -> None:
        self._client_configuration = value

    def get_openobd_credentials(self, connection_uuid: str, provider_uuid: str, content_type=None) -> requests.Response:
        api_key = self.client_configuration.api_key
        access_token = self.client_configuration.access_token
        if not access_token:
            access_token = "AVOsdoghadpPIENPodhvihbai"  # temporary arbitrary value
        url = self.client_configuration.endpoint_url
        if not content_type:
            content_type = "application/json"

        # @TODO: when partner api is available add the functionality to update bearer token
        response = requests.post(url, json=self._create_body(connection_uuid, provider_uuid), headers=self._create_header(content_type, api_key, access_token))
        return response

    @staticmethod
    def _create_header(content_type: str, api_key: str, access_token: str) -> dict:
        return {
            "x-api-key": api_key,
            "content-type": content_type,
            "Authorization": "Bearer {}".format(access_token)
        }

    @staticmethod
    def _create_body(connection_uuid: str, provider_uuid: str) -> dict:
        return {
            "connection_uuid": connection_uuid,
            "provider_uuid": provider_uuid
        }
