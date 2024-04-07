# Copyright Jiaqi Liu
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import requests
import sys, os

logging.basicConfig(level=logging.DEBUG)

def _headers(token: str) -> object:
    return {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json',
    }


def create_or_update_secret(secret_name: str, secret_value: str, pipeline_id: int, screwdriver_api_url: str, token: str) -> None:
    """
    "allowInPR" is set to be false by default

    :param secret_name:
    :param secret_value:
    :param pipeline_id:
    :param token:
    """

    response = requests.get(
        "{}/v4/pipelines/{}/secrets".format(screwdriver_api_url, pipeline_id),
        headers={
            'accept': 'application/json',
            'Authorization': token,
        }
    )
    if secret_name in str(response.content):
        logging.debug("Updating secret '{}'".format(secret_name))

        for secrete in response.json():
            if secrete["name"] == secret_name:
                json_data = {
                    'value': secret_value,
                    'allowInPR': False,
                }

                if requests.put('{}/v4/secrets/{}'.format(screwdriver_api_url, secrete["id"]), headers=_headers(token), json=json_data).status_code != 200:
                    sys.exit(os.EX_CONFIG)
    else:
        logging.debug("Creating secret '{}'".format(secret_name))

        json_data = {
            'pipelineId': pipeline_id,
            'name': secret_name,
            'value': secret_value,
            'allowInPR': False,
        }

        if requests.post('{}/v4/secrets'.format(screwdriver_api_url), headers=_headers(token), json=json_data).status_code != 201:
            sys.exit(os.EX_CONFIG)
