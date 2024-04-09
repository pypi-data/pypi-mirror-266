import json
import threading

import requests

from maitai._eval_request import EvalRequestEncoder
from maitai._config import config
from maitai import MaiTaiObject, EvalRequest


class Evaluator(MaiTaiObject):

    # MAITAI_HOST = 'https://maitai.ai.yewpay.com'
    MAITAI_HOST = 'https://api.dev.yewpay.com'

    def __init__(self):
        super().__init__()

    @classmethod
    def evaluate(cls, session_id, reference_id, content):
        eval_request: EvalRequest = cls.create_eval_request(session_id, reference_id, content)
        cls.send_evaluation_request(eval_request)

    @classmethod
    def create_eval_request(cls, session_id, reference_id, action_type, content):
        if type(content) != str:
            raise Exception('Content must be a string')
        eval_request: EvalRequest = EvalRequest()
        eval_request.application_id = config.application_id
        eval_request.session_id = session_id
        eval_request.reference_id = reference_id
        eval_request.action_type = action_type
        eval_request.evaluation_content = content
        eval_request.evaluation_content_type = 'text'
        return eval_request

    @classmethod
    def update_session_context(cls, session_id, context):
        if type(context) != dict:
            raise Exception('Context must be a dictionary')
        session_context = {
            'application_id': config.application_id,
            'session_id': session_id,
            'context': context
        }
        cls.send_session_context_update(session_context)

    @classmethod
    def append_session_context(cls, session_id, context):
        if type(context) != dict:
            raise Exception('Context must be a dictionary')
        session_context = {
            'application_id': config.application_id,
            'session_id': session_id,
            'context': context
        }
        cls.send_session_context_append(session_context)

    @classmethod
    def update_application_context(cls, context):
        if type(context) != dict:
            raise Exception('Context must be a dictionary')
        session_context = {
            'application_id': config.application_id,
            'context': context
        }
        cls.send_application_context_update(session_context)

    @classmethod
    def append_application_context(cls, context):
        if type(context) != dict:
            raise Exception('Context must be a dictionary')
        session_context = {
            'application_id': config.application_id,
            'context': context
        }
        cls.send_application_context_append(session_context)

    @classmethod
    def send_evaluation_request(cls, eval_request):
        def send_request():
            host = cls.MAITAI_HOST
            url = f'{host}/evaluation/request'
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': config.api_key
            }
            response = requests.post(url, headers=headers, data=json.dumps(eval_request, cls=EvalRequestEncoder))
            if response.status_code != 200:
                error_text = response.text
                print(f"Failed to send evaluation request. Status code: {response.status_code}. Error: {error_text}")
            else:
                print(f"Successfully sent evaluation request. Status code: {response.status_code}")

        # Start a new thread to send the request without waiting for the response
        threading.Thread(target=send_request).start()

    @classmethod
    def send_session_context_update(cls, session_context):
        def send_context():
            host = cls.MAITAI_HOST
            url = f'{host}/context/session'
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': config.api_key
            }
            response = requests.put(url, headers=headers, data=json.dumps(session_context))
            if response.status_code != 200:
                error_text = response.text
                print(f"Failed to send session context update. Status code: {response.status_code}. Error: {error_text}")
            else:
                print(f"Successfully sent session context update. Status code: {response.status_code}")

        # Start a new thread to send the request without waiting for the response
        threading.Thread(target=send_context()).start()

    @classmethod
    def send_session_context_append(cls, session_context):
        def send_context():
            host = cls.MAITAI_HOST
            url = f'{host}/context/session/append'
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': config.api_key
            }
            response = requests.put(url, headers=headers, data=json.dumps(session_context))
            if response.status_code != 200:
                error_text = response.text
                print(f"Failed to send session context for append. Status code: {response.status_code}. Error: {error_text}")
            else:
                print(f"Successfully sent session context for append. Status code: {response.status_code}")

        threading.Thread(target=send_context()).start()

    @classmethod
    def send_application_context_update(cls, application_context):
        def send_context():
            host = cls.MAITAI_HOST
            url = f'{host}/context/application'
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': config.api_key
            }
            response = requests.put(url, headers=headers, data=json.dumps(application_context))
            if response.status_code != 200:
                error_text = response.text
                print(f"Failed to send application context update. Status code: {response.status_code}. Error: {error_text}")
            else:
                print(f"Successfully sent application context update. Status code: {response.status_code}")

        # Start a new thread to send the request without waiting for the response
        threading.Thread(target=send_context()).start()

    @classmethod
    def send_application_context_append(cls, application_context):
        def send_context():
            host = cls.MAITAI_HOST
            url = f'{host}/context/application/append'
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': config.api_key
            }
            response = requests.put(url, headers=headers, data=json.dumps(application_context))
            if response.status_code != 200:
                error_text = response.text
                print(f"Failed to send application context for append. Status code: {response.status_code}. Error: {error_text}")
            else:
                print(f"Successfully sent application context for append. Status code: {response.status_code}")

        threading.Thread(target=send_context()).start()
