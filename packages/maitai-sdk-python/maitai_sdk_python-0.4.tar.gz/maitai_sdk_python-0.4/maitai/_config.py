class Config:

    def __init__(self):
        self._api_key = None
        self._application_id = None

    @property
    def api_key(self):
        if self._api_key is None:
            raise ValueError("API Key has not been set.")
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value

    @property
    def application_id(self):
        if self._application_id is None:
            raise ValueError("Application ID has not been set.")
        return self._application_id

    @application_id.setter
    def application_id(self, value):
        self._application_id = value

    def initialize(self, api_key, application_id):
        self.api_key = api_key
        self.application_id = application_id

config = Config()
