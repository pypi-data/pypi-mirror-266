from openweather_sdk.globals import _FORECAST_API_VERSIONS, _PRO_DOMAIN
from openweather_sdk.rest.base import _APIRequest, _build_url
from openweather_sdk.validators import _validate_selected_attr


class _ForecastAPI:
    """
    A class for creating data for path buildng to Forecast API.
    See: https://openweathermap.org/forecast5,
    https://openweathermap.org/api/hourly-forecast,
    https://openweathermap.org/forecast16 or
    https://openweathermap.org/api/forecast30.
    """

    def __init__(self, lon, lat, appid, **kwargs):
        self.service_name = "data"
        self.lat = lat
        self.lon = lon
        self.appid = appid
        self.version = kwargs.get("version", "2.5")
        self.units = kwargs.get("units", "metric")
        self.language = kwargs.get("language", "en")

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = _validate_selected_attr(value, _FORECAST_API_VERSIONS)

    def _get_forecast_5_days(self):
        """Get 5 day forecast (3-hour step) at the specified point."""
        end_point = "forecast"
        query_params = {
            "lat": self.lat,
            "lon": self.lon,
            "appid": self.appid,
            "units": self.units,
            "lang": self.language,
        }
        url = _build_url(self.service_name, self.version, end_point, query_params)
        return _APIRequest(url)._get_data()

    def _get_forecast_hourly(self):
        """Get hourly forecast for 4 days (96 timestamps) at the specified point."""
        end_point = "forecast/hourly"
        query_params = {
            "lat": self.lat,
            "lon": self.lon,
            "appid": self.appid,
            "units": self.units,
            "lang": self.language,
        }
        url = _build_url(
            self.service_name, self.version, end_point, query_params, domain=_PRO_DOMAIN
        )
        return _APIRequest(url)._get_data()

    def _get_forecast_daily_16_days(self):
        """Get daily forecast for 16 days at the specified point."""
        end_point = "forecast/daily"
        query_params = {
            "lat": self.lat,
            "lon": self.lon,
            "appid": self.appid,
            "units": self.units,
            "lang": self.language,
        }
        url = _build_url(self.service_name, self.version, end_point, query_params)
        return _APIRequest(url)._get_data()

    def _get_forecast_daily_30_days(self):
        """Get daily forecast for 30 days at the specified point."""
        end_point = "forecast/climate"
        query_params = {
            "lat": self.lat,
            "lon": self.lon,
            "appid": self.appid,
            "units": self.units,
            "lang": self.language,
        }
        url = _build_url(
            self.service_name, self.version, end_point, query_params, domain=_PRO_DOMAIN
        )
        return _APIRequest(url)._get_data()
