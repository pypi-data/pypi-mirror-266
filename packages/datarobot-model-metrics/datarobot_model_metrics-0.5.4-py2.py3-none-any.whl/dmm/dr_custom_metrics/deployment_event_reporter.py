#
# Copyright 2022-2024 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import logging

import datarobot as dr
from requests.exceptions import ConnectionError, HTTPError
from urllib3.exceptions import MaxRetryError

from dmm.datarobot_api_client import DataRobotApiClient


class DeploymentEventReporter:
    def __init__(
        self,
        deployment_id: str,
        dr_client: dr.Client = None,
        dr_url: str = None,
        dr_api_key: str = None,
    ):
        """
        :param dr_url: DataRobot app url
        :param dr_api_key: API Key to access public API
        :param deployment_id: Deployment ID to report custom metrics for
        """
        self._logger = logging.getLogger(__name__)

        self._api = (
            DataRobotApiClient(token=dr_api_key, base_url=dr_url)
            if (dr_api_key and dr_url)
            else DataRobotApiClient(client=dr_client)
        )
        self._deployment_id = deployment_id

    def report_deployment(self, title: str, message: str) -> None:
        """
        Report deployment event
        :param title: str
        :param message: str
        """

        try:
            response = self._api.report_deployment_event(
                deployment_id=self._deployment_id, title=title, message=message
            )
            response.raise_for_status()
        except (ConnectionError, HTTPError, MaxRetryError) as e:
            raise Exception(f"Deployment event can not be reported to MLOPS: {str(e)}")
