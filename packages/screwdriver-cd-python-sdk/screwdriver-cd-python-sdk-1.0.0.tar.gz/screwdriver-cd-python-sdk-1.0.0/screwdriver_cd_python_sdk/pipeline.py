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

def search_pipelines_by_name(name: str, screwdriver_api_url: str, token: str) -> list[object]:
    """
    Returns, at most 50 entries, all pipelines whose name contains a specified pipeline name

    :param name:  The pipeline name to search. e.g. "QubitPi/my-project"
    :param screwdriver_api_url:  The URL of the Screwdriver API server
    :param token:  The Screwdriver API token

    :return: the native API response body object with the following fields:

    .. code-block:: json

        [
            {
                "id":6,
                "name":"QubitPi/theresa",
                "scmUri":"github.com:631185801:master",
                "scmContext":"github:github.com",
                "scmRepo":{
                    "branch":"master",
                    "name":"QubitPi/theresa",
                    "url":"https://github.com/QubitPi/theresa/tree/master",
                    "rootDir":"",
                    "private":true
                },
                "createTime":"2024-02-17T11:00:30.036Z",
                "admins":{
                    "QubitPi":true
                },
                "workflowGraph":{
                    "nodes":[
                        ...
                    ],
                    "edges":[
                        ...
                    ]
                },
                "annotations":{

                },
                "prChain":false,
                "parameters":{

                },
                "settings":{

                },
                "state":"ACTIVE",
                "subscribedScmUrlsWithActions":[

                ]
            }
        ]
    """
    headers = {
        'accept': 'application/json',
        'Authorization': token
    }

    params = {
        'page': '1',
        'count': '50',
        'search': name,
        'sort': 'descending',
    }

    response = requests.get('{}/v4/pipelines'.format(screwdriver_api_url), params=params, headers=headers)

    if response.status_code != 200:
        sys.exit(os.EX_CONFIG)

    return response.json()

def create_pipeline(checkout_url: str, screwdriver_api_url: str, token: str, source_directory: object = None) -> object:
    """
    Creates a new Screwdriver pipeline for a particular repo and an optional source directory.

    If the source_directory is not specified, it defaults to the repo root.

    :param checkout_url:  The URL of the repository containing the screwdriver.yaml file of the pipeline created
    :param screwdriver_api_url:  The URL of the Screwdriver API server
    :param token:  The Screwdriver API token
    :param source_directory:  The custom directory that this pipeline is based upon. See
    https://qubitpi.github.io/screwdriver-cd-guide/user-guide/configuration/sourceDirectory for more details

    :return: the native API response body object with the following fields:

    .. code-block:: json

        {
            "id":1,
            "name":"QubitPi/screwdriver-cd-python-sdk",
            "scmUri":"github.com:746187061:master",
            "scmContext":"github:github.com",
            "scmRepo":{
                "branch":"master",
                "name":"QubitPi/screwdriver-cd-python-sdk",
                "url":"https://github.com/QubitPi/screwdriver-cd-python-sdk/tree/master",
                "rootDir":"",
                "private":false
            },
            "createTime":"2024-02-17T09:55:32.632Z",
            "admins":{
                "QubitPi":true
            },
            "workflowGraph":{
                "nodes":[
                    ...
                ],
                "edges":[
                    ...
                ]
            },
            "annotations":{

            },
            "prChain":false,
            "state":"ACTIVE",
            "subscribedScmUrlsWithActions":[

            ]
        }
    """
    logging.debug("Creating pipeline '{}/{}'".format(checkout_url, source_directory if source_directory else "root"))

    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json',
    }

    json_data = {
        'checkoutUrl': checkout_url,
        'rootDir': source_directory,
        'autoKeysGeneration': True,
    } if source_directory else {
        'checkoutUrl': checkout_url,
        'autoKeysGeneration': True,
    }

    response = requests.post('{}/v4/pipelines'.format(screwdriver_api_url), headers=headers, json=json_data)

    if response.status_code != 201:
        sys.exit(os.EX_CONFIG)

    return response.json()
