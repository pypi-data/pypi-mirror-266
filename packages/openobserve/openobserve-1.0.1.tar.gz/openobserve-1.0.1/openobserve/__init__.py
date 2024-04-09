import os
import requests
import logging
import json
import openobserve.generate
from requests.auth import HTTPBasicAuth
from typing import Any
from jsonex import JsonEx

username = ''
password = ''
host = 'http://127.0.0.1:5080'
stream_global = 'default'
organization_global = 'default'
ssl_verify = False
timeout = 3
additional_info = False
logs_dir = os.path.join(os.path.expanduser('~'), '.openobserve', 'logs')

if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

logging.basicConfig(filename=logs_dir + '/log.log', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')


def send(
    job: Any = '',
    level: str = 'INFO',
    _stream: str = None,
    _organization: str = None,
    _return_data: bool = False,
    **kwargs
) -> Any:
    global host, username, password, stream_global, organization_global, ssl_verify, timeout, additional_info

    _stream = _stream if _stream is not None else stream_global
    _organization = _organization if _organization is not None else organization_global
    url = host + '/api/' + _organization + '/' + _stream + '/_json'
    debug = {} if additional_info is False else openobserve.generate.debug_data()

    try:
        data = {
            **{
                'job': job,
                'level': level
            },
            **debug,
            **kwargs
        }

        if _return_data:
            return data

        response = requests.post(
            url=url,
            data=JsonEx.dump([data]),
            auth=HTTPBasicAuth(username, password),
            verify=ssl_verify,
            timeout=timeout
        )

        response_data = json.loads(response.content)

        if response_data['status'][0]['failed'] > 0:
            logging.error("Failed to send data: %s", str(response.content))
            return False

        return response
    except Exception as e:
        logging.error("Error during sending data: %s", str(e))
        return False
