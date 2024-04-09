from maitai._eval_request import EvalRequest as EvalRequest
from maitai._loadable import Loadable as Loadable
from maitai._maitai_object import MaiTaiObject as MaiTaiObject
from maitai._evaluator import Evaluator as Evaluator

def initialize(api_key, application_id):
    from maitai._config import config
    config.initialize(api_key, application_id)