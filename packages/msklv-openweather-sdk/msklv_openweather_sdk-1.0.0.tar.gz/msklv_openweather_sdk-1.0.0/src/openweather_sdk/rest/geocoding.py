from openweather_sdk.exceptions import InvalidLocationException
from openweather_sdk.globals import _GEOCODING_API_VERSIONS
from openweather_sdk.rest.base import _APIRequest, _build_url
from openweather_sdk.validators import _validate_selected_attr


class _GeocodingAPI:
    """
    A class for creating data for path buildng to Geocoding API.
    See: https://openweathermap.org/api/geocoding-api.
    """

    def __init__(self, appid, location=None, zip_code=None, **kwargs):
        self.service_name = "geo"
        self.location = location or None
        self.zip_code = zip_code or None
        self.appid = appid
        self.version = kwargs.get("version", "1.0")
        self.limit = kwargs.get("limit", 1)

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = _validate_selected_attr(value, _GEOCODING_API_VERSIONS)

    def _direct(self):
        """Get geographical data by using name of the location (city name or area name)."""
        end_point = "direct"
        query_params = {"q": self.location, "limit": self.limit, "appid": self.appid}
        url = _build_url(self.service_name, self.version, end_point, query_params)
        try:
            result = _APIRequest(url)._get_data()
            return result[0]
        except IndexError as e:
            raise InvalidLocationException(
                "Check if the location is specified correctly."
            ) from e

    def _zip(self):
        """Get geographical coordinates (lon, lat) by using zip/post code"""
        end_point = "zip"
        query_params = {"zip": self.zip_code, "appid": self.appid}
        url = _build_url(self.service_name, self.version, end_point, query_params)
        try:
            return _APIRequest(url)._get_data()
        except Exception as e:
            raise InvalidLocationException(
                "Check if zip code is specified correctly."
            ) from e

    def _reverse(self):
        """Get name of the location (city name or area name) by using geografical coordinates (lon, lat)."""
        return NotImplemented
