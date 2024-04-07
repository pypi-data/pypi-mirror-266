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

import requests
import sys, os

def start_build(pipeline_id: int, screwdriver_api_url: str, token: str) -> object:
    """
    Creates and starts a pipeline build.

    :param pipeline_id:  The ID of the pipeline to trigger the build
    :param screwdriver_api_url:  The URL of the Screwdriver API server. For example: http://192.168.7.2:9001 or https://mysd.com
    :param token:  The Screwdriver API token

    :return:  The exact same response body as the "POST /v4/events" Swagger API in JSON
    """
    return create_and_start_event(
        screwdriver_api_url,
        {
            'pipelineId': pipeline_id,
            'startFrom': '~commit',
            'causeMessage': 'Run on create',
        },
        token
    )

def create_and_start_event(screwdriver_api_url: str, body: object, token: str) -> object:
    """
    Creates and starts a specific event.

    If an error occurs, this function returns nothing but throws the causing error.

    :param screwdriver_api_url:  The URL of the Screwdriver API server. For example: http://192.168.7.2:9001 or https://mysd.com
    :param body:  The exact same body as the one used in "POST /v4/events" Swagger API
    :param token:  The Screwdriver API token

    :return:  The exact same response body as the "POST /v4/events" Swagger API in JSON
    """
    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json',
    }

    response = requests.post('{}/v4/events'.format(screwdriver_api_url), headers=headers, json=body)

    if response.status_code != 201:
        sys.exit(os.EX_CONFIG)

    return response.json()
