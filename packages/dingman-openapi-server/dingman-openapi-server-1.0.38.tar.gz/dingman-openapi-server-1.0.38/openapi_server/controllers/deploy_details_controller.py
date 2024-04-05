import connexion
import six
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.deployment_detail import DeploymentDetail  # noqa: E501
from openapi_server.models.dingman_error import DingmanError  # noqa: E501
from openapi_server import util


def get_deployment_details(app_service_name):  # noqa: E501
    """Get Deployment Details under an app service

    This operation returns the Deployment detail list under the specified app-service # noqa: E501

    :param app_service_name: 
    :type app_service_name: str

    :rtype: Union[DeploymentDetail, Tuple[DeploymentDetail, int], Tuple[DeploymentDetail, int, Dict[str, str]]
    """
    return 'do some magic!'
