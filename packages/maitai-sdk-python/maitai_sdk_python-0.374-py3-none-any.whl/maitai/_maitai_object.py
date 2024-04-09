from maitai.config import global_config
from maitai import Loadable


class MaiTaiObject(Loadable):

    def __init__(self):
        super().__init__()
        self.api_key = global_config.api_key
        self.application_id = global_config.application_id
