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
import os
import json
import csv
from screwdriver_cd_python_sdk.pipeline import create_pipeline
from screwdriver_cd_python_sdk.pipeline import search_pipelines_by_name
from screwdriver_cd_python_sdk.secrets import create_or_update_secret
from screwdriver_cd_python_sdk.events import start_build

def initialize(pipelines_config_path: str, screwdriver_api_url: str, token: str) -> None:
    with open(pipelines_config_path, 'r') as file:
        pipelines = json.load(file)

    for pipeline in pipelines:

        git_url = pipeline["git"]
        repo_name = git_url[git_url.find(":")+1 : git_url.find(".git")]

        pipeline_id=None
        for match in search_pipelines_by_name(name=repo_name, screwdriver_api_url=screwdriver_api_url, token=token):
            if match["name"] == repo_name:
                pipeline_id = match["id"]
                logging.debug("{} is already created.".format(repo_name))

                break

        if pipeline_id is None:
            logging.debug("Creating {}...".format(repo_name))
            pipeline_id = create_pipeline(checkout_url=pipeline["git"], screwdriver_api_url=screwdriver_api_url, token=token)["id"]

        if "awsCredentialFile" in pipeline:
            with open(pipeline["awsCredentialFile"], 'r') as file:
                lines = csv.reader(file)
                for i, row in enumerate(lines):
                    if i == 1:
                        create_or_update_secret(
                            secret_name="AWS_ACCESS_KEY_ID",
                            secret_value=row[0],
                            pipeline_id=pipeline_id,
                            screwdriver_api_url=screwdriver_api_url,
                            token=token
                        )
                        create_or_update_secret(
                            secret_name="AWS_SECRET_ACCESS_KEY",
                            secret_value=row[1],
                            pipeline_id=pipeline_id,
                            screwdriver_api_url=screwdriver_api_url,
                            token=token
                        )
        if pipeline["secrets"]:
            for secret in pipeline["secrets"]:
                if secret["type"] == "value":
                    create_or_update_secret(
                        secret_name=secret["name"],
                        secret_value=secret["value"],
                        pipeline_id=pipeline_id,
                        screwdriver_api_url=screwdriver_api_url,
                        token=token
                    )
                else:
                    create_or_update_secret(
                        secret_name=secret["name"],
                        secret_value=_file_content(secret["value"]),
                        pipeline_id=pipeline_id,
                        screwdriver_api_url=screwdriver_api_url,
                        token=token
                    )

        if pipeline["runOnCreate"]:
            start_build(pipeline_id=pipeline_id, screwdriver_api_url=screwdriver_api_url, token=token)


def _file_content(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read().rstrip('\n') # https://stackoverflow.com/a/70233945
