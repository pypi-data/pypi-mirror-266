from openweather_sdk.globals import _AIR_POLLUTION_API_VERSIONS
from openweather_sdk.rest.base import _APIRequest, _build_url
from openweather_sdk.validators import _validate_selected_attr


class _AirPollutionAPI:
    """
    A class for creating data for path buildng to Air Pollution API.
    See: https://openweathermap.org/api/air-pollution.
    """

    def __init__(self, lon, lat, appid, start=None, end=None, **kwargs):
        self.service_name = "data"
        self.lat = lat
        self.lon = lon
        self.appid = appid
        self.start = start
        self.end = end
        self.version = kwargs.get("version", "2.5")
        self.units = kwargs.get("units", "metric")
        self.language = kwargs.get("language", "en")

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = _validate_selected_attr(value, _AIR_POLLUTION_API_VERSIONS)

    def _get_current_air_pollution(self):
        """Get current air pollution at the specified point."""
        end_point = "air_pollution"
        query_params = {"lat": self.lat, "lon": self.lon, "appid": self.appid}
        url = _build_url(self.service_name, self.version, end_point, query_params)
        return _APIRequest(url)._get_data()

    def _get_forecast_air_pollution(self):
        """Get hourly air pollution forecast for 4 days (96 timestamps) at the specified point."""
        end_point = "air_pollution/forecast"
        query_params = {"lat": self.lat, "lon": self.lon, "appid": self.appid}
        url = _build_url(self.service_name, self.version, end_point, query_params)
        return _APIRequest(url)._get_data()

    def _get_history_air_pollution(self):
        """Get historical air pollution data at the specified point."""
        end_point = "air_pollution/history"
        query_params = {
            "lat": self.lat,
            "lon": self.lon,
            "appid": self.appid,
            "start": self.start,
            "end": self.end,
        }
        url = _build_url(self.service_name, self.version, end_point, query_params)
        return _APIRequest(url)._get_data()
