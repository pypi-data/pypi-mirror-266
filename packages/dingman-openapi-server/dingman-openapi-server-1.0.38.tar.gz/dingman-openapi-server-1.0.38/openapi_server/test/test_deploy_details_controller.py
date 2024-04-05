# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.deployment_detail import DeploymentDetail  # noqa: E501
from openapi_server.models.dingman_error import DingmanError  # noqa: E501
from openapi_server.test import BaseTestCase


class TestDeployDetailsController(BaseTestCase):
    """DeployDetailsController integration test stubs"""

    def test_get_deployment_details(self):
        """Test case for get_deployment_details

        Get Deployment Details under an app service
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/v1/app-service/{app_service_name}/deployment-details'.format(app_service_name='demo-app.gss'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
