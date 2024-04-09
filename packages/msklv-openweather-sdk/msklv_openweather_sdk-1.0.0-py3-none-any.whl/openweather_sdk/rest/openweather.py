from openweather_sdk.globals import _API_DOMAIN
from openweather_sdk.rest.base import _APIRequest


class _OpenWeather:
    def _health_check(self):
        return _APIRequest(_API_DOMAIN)._health_check()
