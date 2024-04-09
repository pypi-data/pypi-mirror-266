import json
import logging
from urllib.parse import urlencode

import requests

from openweather_sdk.exceptions import BadResponseException, UnexpectedException
from openweather_sdk.globals import _API_DOMAIN
from openweather_sdk.logger_filters import TokenFilter

logger = logging.getLogger(__name__)
logger.addFilter(TokenFilter())


def _create_params(query_params):
    params = json.dumps(query_params)
    return urlencode(eval(params))


def _create_path(*segments, domain):
    path = "/".join(segments)
    return f"{domain}{path}"


def _assemble_full_path(path_data):
    path = path_data["path"]
    params = _create_params(path_data["query_params"])
    return f"{path}?{params}"


def _build_url(service_name, version, end_point, query_params, domain=_API_DOMAIN):
    path = _create_path(service_name, version, end_point, domain=domain)
    path_data = {"path": path, "query_params": query_params}
    return _assemble_full_path(path_data)


class _APIRequest:
    """Base class to API requests."""

    def __init__(self, path):
        self.path = path

    def _get(self):
        try:
            response = requests.get(self.path)
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            raise BadResponseException(
                response.status_code, json.loads(response.content)["message"]
            ) from e
        except requests.Timeout as e:
            logger.warning(e)
            raise
        except requests.ConnectionError as e:
            logger.warning(e)
            raise
        except requests.RequestException as e:
            logger.warning(e)
            raise
        except Exception as e:
            logger.warning(e)
            raise UnexpectedException(e) from e

    def _get_data(self):
        response = self._get()
        content = response.content
        return json.loads(content)

    def _health_check(self):
        response = self._get()
        status_code = response.status_code
        logger.info(f"Health checking's status: {status_code}")
        return status_code
