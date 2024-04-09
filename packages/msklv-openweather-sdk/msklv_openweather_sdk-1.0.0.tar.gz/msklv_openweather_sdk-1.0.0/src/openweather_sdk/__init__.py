__version__ = "1.0.0"

import logging
import time
import warnings
from threading import Lock, Thread

from openweather_sdk.cache import _ClientCache
from openweather_sdk.exceptions import (
    ClientAlreadyExistsException,
    ClientDoesntExistException,
    InvalidLocationException,
)
from openweather_sdk.globals import _LANGUAGES, _SPECIFIC_CACHES, _UNITS, _WORK_MODES
from openweather_sdk.rest.airpollution import _AirPollutionAPI
from openweather_sdk.rest.forecast import _ForecastAPI
from openweather_sdk.rest.geocoding import _GeocodingAPI
from openweather_sdk.rest.openweather import _OpenWeather
from openweather_sdk.rest.weather import _WeatherAPI
from openweather_sdk.validators import (
    _validate_non_negative_integer_attr,
    _validate_selected_attr,
    _validate_time,
)

warnings.filterwarnings("always", category=DeprecationWarning, module="openweather_sdk")

logging.getLogger(__name__).addHandler(logging.NullHandler())

logger = logging.getLogger(__name__)


class Client:
    """
    A client for acessing to OpenWeather API.
    Client can works in 'on-demand' or 'polling' mode.
    In 'on-demand' mode, the client updates weather information solely upon
    user requests. In 'polling' mode, the SDK proactively requests fresh
    weather information for all stored locations, ensuring a zero-latency
    response for user requests.
    """

    _active_tokens = set()

    def __init__(
        self,
        token,
        mode="on-demand",
        language="en",
        units="metric",
        cache_size=10,
        ttl=600,
        **kwargs,
    ):
        """
        Сlient initialization.

        Args:
            token (str): unique OpenWeather API key. See on https://home.openweathermap.org/api_keys
            mode (str, optional): 'on-demand' or 'polling' mode.  Defaults to "on-demand".
            language (str, optional): language of the output. Current list see on https://openweathermap.org/current#multi. Defaults to "en".
            units (str, optional): units of measurement. See on https://openweathermap.org/current#data. Defaults to "metric".
            cache_size (int, optional): max size of cache. Defaults to 10.
            ttl (int, optional): the time (in sec) during which the information is considered relevant. Defaults to 600.
        """
        logger.info(f"Client {token[:4]}...{token[-4:]} is being initialized...")
        self.mode = mode
        self.language = language
        self.units = units
        self.cache_size = cache_size
        self.ttl = ttl
        self.cache = {
            cache: _ClientCache(self.cache_size, self.ttl, self.mode)
            for cache in _SPECIFIC_CACHES
        }
        self.lock = Lock()
        self.token = (
            token  # must be last to be sure that all other attributes are valid
        )

        if self.mode == "polling":
            self.polling_thread = Thread(target=self._polling)
            self.polling_thread.start()

        logger.info(
            f"Client {self} was initialized with params: mode = {self.mode}, language = {self.language}, units = {self.units}, cache_size = {self.cache_size}, ttl = {self.ttl}."
        )

    def __str__(self):
        return f"{self.token[:4]}...{self.token[-4:]}"

    @property
    def token(self):
        return self._token

    @property
    def mode(self):
        return self._mode

    @property
    def language(self):
        return self._language

    @property
    def units(self):
        return self._units

    @property
    def cache_size(self):
        return self._cache_size

    @property
    def ttl(self):
        return self._ttl

    @token.setter
    def token(self, value):
        if hasattr(self, "_token"):
            Client._active_tokens.discard(self._token)
        self._token = self._validate_token(value)

    @mode.setter
    def mode(self, value):
        self._mode = _validate_selected_attr(value, _WORK_MODES)

    @language.setter
    def language(self, value):
        self._language = _validate_selected_attr(value, _LANGUAGES)

    @units.setter
    def units(self, value):
        self._units = _validate_selected_attr(value, _UNITS)

    @cache_size.setter
    def cache_size(self, value):
        self._cache_size = _validate_non_negative_integer_attr(value)

    @ttl.setter
    def ttl(self, value):
        self._ttl = _validate_non_negative_integer_attr(value)

    @property
    def is_alive(self):
        return self.token in Client._active_tokens

    def remove(self):
        """Remove the current client."""
        logger.info(f"The client {self} is being removed...")
        if self.is_alive:
            Client._active_tokens.discard(self.token)
        else:
            raise ClientDoesntExistException(self)
        if self.mode == "polling":
            self.polling_thread.join()
        logger.info(f"Client {self} was removed")

    def _validate_token(self, token):
        if token in Client._active_tokens:
            client_token = f"{token[:4]}...{token[-4:]}"
            raise ClientAlreadyExistsException(client_token)
        Client._active_tokens.add(token)
        return token

    def _get_location_coordinates(self, location):
        geocoding_api = _GeocodingAPI(location=location, appid=self.token)
        geo_info = geocoding_api._direct()
        return self._round_coordinates(geo_info["lon"], geo_info["lat"])

    def _get_zip_code_coordinates(self, zip_code):
        geocoding_api = _GeocodingAPI(zip_code=zip_code, appid=self.token)
        geo_info = geocoding_api._zip()
        return self._round_coordinates(geo_info["lon"], geo_info["lat"])

    def _round_coordinates(self, lon, lat):
        lat = round(lat, 3)
        lon = round(lon, 3)
        return lon, lat

    def _get_location_current_weather(self, location):
        lon, lat = self._get_location_coordinates(location)
        return self._get_current_weather(lon, lat)

    def _get_zip_code_current_weather(self, zip_code):
        lon, lat = self._get_zip_code_coordinates(zip_code)
        return self._get_current_weather(lon, lat)

    def _get_current_weather(self, lon, lat):
        if self.cache_size:
            with self.lock:
                if self.cache["current_weather"]._is_relevant_info(lon, lat):
                    return self.cache["current_weather"]._get_info(lon, lat)

        weather_api = _WeatherAPI(lon=lon, lat=lat, appid=self.token)
        weather = weather_api._get_current_wheather()

        if self.cache_size:
            with self.lock:
                self.cache["current_weather"]._add_info(lon, lat, weather)
                logger.info(
                    f"The client {self} has received data about the current weather: {weather}"
                )
                return weather

    def _polling(self):
        logger.info(f"The client {self} initiated the polling.")
        while self.is_alive:
            time.sleep(self.cache.ttl)
            if not self.cache["current_weather"]:
                continue
            coordinates = list(self.cache["current_weather"].keys())
            for lon, lat in coordinates:
                if (lon, lat) not in self.cache["current_weather"]:
                    continue
                weather_api = _WeatherAPI(lon=lon, lat=lat, appid=self.token)
                with self.lock:
                    weather = weather_api._get_current_wheather()
                    self.cache["current_weather"]._update_info(lon, lat, weather)
        logger.info(f"The client {self} has completed the polling.")

    def _get_location_forecast_5_days(self, location):
        lon, lat = self._get_location_coordinates(location)
        return self._get_forecast_5_days(lon, lat)

    def _get_zip_code_forecast_5_days(self, zip_code):
        lon, lat = self._get_zip_code_coordinates(zip_code)
        return self._get_forecast_5_days(lon, lat)

    def _get_forecast_5_days(self, lon, lat):
        if self.cache_size:
            with self.lock:
                if self.cache["forecast_5_days"]._is_relevant_info(lon, lat):
                    return self.cache["forecast_5_days"]._get_info(lon, lat)

        forecast_api = _ForecastAPI(lon=lon, lat=lat, appid=self.token)
        forecast = forecast_api._get_forecast_5_days()

        if self.cache_size:
            with self.lock:
                self.cache["forecast_5_days"]._add_info(lon, lat, forecast)
                logger.info(
                    f"The client {self} has received data about 5 day forecast: {forecast}"
                )
                return forecast

    def _get_location_forecast_hourly(self, location):
        lon, lat = self._get_location_coordinates(location)
        return self._get_forecast_hourly(lon, lat)

    def _get_zip_code_forecast_hourly(self, zip_code):
        lon, lat = self._get_zip_code_coordinates(zip_code)
        return self._get_forecast_hourly(lon, lat)

    def _get_forecast_hourly(self, lon, lat):
        if self.cache_size:
            with self.lock:
                if self.cache["forecast_hourly"]._is_relevant_info(lon, lat):
                    return self.cache["forecast_hourly"]._get_info(lon, lat)

        forecast_api = _ForecastAPI(lon=lon, lat=lat, appid=self.token)
        forecast = forecast_api._get_forecast_hourly()

        if self.cache_size:
            with self.lock:
                self.cache["forecast_hourly"]._add_info(lon, lat, forecast)
                logger.info(
                    f"The client {self} has received data about hourly forecast: {forecast}"
                )
                return forecast

    def _get_location_forecast_daily_16_days(self, location):
        lon, lat = self._get_location_coordinates(location)
        return self._get_forecast_daily_16_days(lon, lat)

    def _get_zip_code_forecast_daily_16_days(self, zip_code):
        lon, lat = self._get_zip_code_coordinates(zip_code)
        return self._get_forecast_daily_16_days(lon, lat)

    def _get_forecast_daily_16_days(self, lon, lat):
        if self.cache_size:
            with self.lock:
                if self.cache["forecast_16_days"]._is_relevant_info(lon, lat):
                    return self.cache["forecast_16_days"]._get_info(lon, lat)

        forecast_api = _ForecastAPI(lon=lon, lat=lat, appid=self.token)
        forecast = forecast_api._get_forecast_daily_16_days()

        if self.cache_size:
            with self.lock:
                self.cache["forecast_16_days"]._add_info(lon, lat, forecast)
                logger.info(
                    f"The client {self} has received data about 16 days forecast: {forecast}"
                )
                return forecast

    def _get_location_forecast_daily_30_days(self, location):
        lon, lat = self._get_location_coordinates(location)
        return self._get_forecast_daily_30_days(lon, lat)

    def _get_zip_code_forecast_daily_30_days(self, zip_code):
        lon, lat = self._get_zip_code_coordinates(zip_code)
        return self._get_forecast_daily_30_days(lon, lat)

    def _get_forecast_daily_30_days(self, lon, lat):
        if self.cache_size:
            with self.lock:
                if self.cache["forecast_30_days"]._is_relevant_info(lon, lat):
                    return self.cache["forecast_30_days"]._get_info(lon, lat)

        forecast_api = _ForecastAPI(lon=lon, lat=lat, appid=self.token)
        forecast = forecast_api._get_forecast_daily_30_days()

        if self.cache_size:
            with self.lock:
                self.cache["forecast_30_days"]._add_info(lon, lat, forecast)
                logger.info(
                    f"The client {self} has received data about 30 days forecast: {forecast}"
                )
                return forecast

    def _get_location_current_air_pollution(self, location):
        lon, lat = self._get_location_coordinates(location)
        return self._get_current_air_pollution(lon, lat)

    def _get_zip_code_current_air_pollution(self, zip_code):
        lon, lat = self._get_zip_code_coordinates(zip_code)
        return self._get_current_air_pollution(lon, lat)

    def _get_current_air_pollution(self, lon, lat):
        if self.cache_size:
            with self.lock:
                if self.cache["current_air_pollution"]._is_relevant_info(lon, lat):
                    return self.cache["current_air_pollution"]._get_info(lon, lat)

        air_pollution_api = _AirPollutionAPI(lon=lon, lat=lat, appid=self.token)
        air_pollution = air_pollution_api._get_current_air_pollution()

        if self.cache_size:
            with self.lock:
                self.cache["current_air_pollution"]._add_info(lon, lat, air_pollution)
                logger.info(
                    f"The client {self} has received data about current air pollution: {air_pollution}"
                )
                return air_pollution

    def _get_location_forecast_air_pollution(self, location):
        lon, lat = self._get_location_coordinates(location)
        return self._get_forecast_air_pollution(lon, lat)

    def _get_zip_code_forecast_air_pollution(self, zip_code):
        lon, lat = self._get_zip_code_coordinates(zip_code)
        return self._get_forecast_air_pollution(lon, lat)

    def _get_forecast_air_pollution(self, lon, lat):
        if self.cache_size:
            with self.lock:
                if self.cache["forecast_air_pollution"]._is_relevant_info(lon, lat):
                    return self.cache["forecast_air_pollution"]._get_info(lon, lat)

        air_pollution_api = _AirPollutionAPI(lon=lon, lat=lat, appid=self.token)
        forecast = air_pollution_api._get_forecast_air_pollution()

        if self.cache_size:
            with self.lock:
                self.cache["forecast_air_pollution"]._add_info(lon, lat, forecast)
                logger.info(
                    f"The client {self} has received data about forecast air pollution: {forecast}"
                )
                return forecast

    def _get_location_history_air_pollution(self, location, start, end):
        lon, lat = self._get_location_coordinates(location)
        return self._get_history_air_pollution(lon, lat, start, end)

    def _get_zip_code_history_air_pollution(self, zip_code, start, end):
        lon, lat = self._get_zip_code_coordinates(zip_code)
        return self._get_history_air_pollution(lon, lat, start, end)

    def _get_history_air_pollution(self, lon, lat, start, end):
        air_pollution_api = _AirPollutionAPI(
            lon=lon, lat=lat, appid=self.token, start=start, end=end
        )
        history = air_pollution_api._get_history_air_pollution()
        logger.info(
            f"The client {self} has received historical air pollution data: {history}"
        )
        return history

    def current_weather(self, location=None, zip_code=None):
        """
        Returns current weather in a specified location.
        The location can be provided either as a combination of city name,
        state code (for the US), and country code separated by commas, or
        as a combination of zip/post code and country code separated by commas.
        Please ensure the usage of ISO 3166 country codes.

        Args:
            location (str, optional): city name, state code (only for the US) and country code divided by comma.
            zip_code (str, optional): zip/post code and country code divided by comma.
        """
        logger.info(
            f"The client {self} is being requested the current weather in the location {location or zip_code}..."
        )
        if not self.is_alive:
            raise ClientDoesntExistException(self)
        if not location and not zip_code:
            raise InvalidLocationException(
                "You need to specify the location or postal code."
            )
        if location:
            if not isinstance(location, str):
                raise InvalidLocationException(
                    "You need to specify the location as a string."
                )
            return self._get_location_current_weather(location)
        if zip_code:
            if not isinstance(zip_code, str):
                raise InvalidLocationException(
                    "You need to specify zip code as a string"
                )
            return self._get_zip_code_current_weather(zip_code)

    def health_check(self):
        """Check if available API service."""
        logger.info(f"The client {self} is being health checking...")
        if not self.is_alive:
            raise ClientDoesntExistException(self)
        return _OpenWeather()._health_check()

    def weather_forecast_5_days(self, location=None, zip_code=None):
        """
        Returns 5 days weather forecast data with 3-hour step at specified location.
        The location can be provided either as a combination of city name,
        state code (for the US), and country code separated by commas, or
        as a combination of zip/post code and country code separated by commas.
        Please ensure the usage of ISO 3166 country codes.

        Args:
            location (str, optional): city name, state code (only for the US) and country code divided by comma.
            zip_code (str, optional): zip/post code and country code divided by comma.
        """
        logger.info(
            f"The client {self} is being requested 5 day weather forecast in the location {location or zip_code}..."
        )
        if not self.is_alive:
            raise ClientDoesntExistException(self)
        if not location and not zip_code:
            raise InvalidLocationException(
                "You need to specify the location or postal code."
            )
        if location:
            if not isinstance(location, str):
                raise InvalidLocationException(
                    "You need to specify the location as a string."
                )
            return self._get_location_forecast_5_days(location)
        if zip_code:
            if not isinstance(zip_code, str):
                raise InvalidLocationException(
                    "You need to specify zip code as a string"
                )
            return self._get_zip_code_forecast_5_days(zip_code)

    def weather_forecast_hourly(self, location=None, zip_code=None):
        """
        Returns hourly weather forecast for 4 days (96 timestamps) at specified location.
        The location can be provided either as a combination of city name,
        state code (for the US), and country code separated by commas, or
        as a combination of zip/post code and country code separated by commas.
        Please ensure the usage of ISO 3166 country codes.

        Accessible with a "Developer" subscription and higher. See: https://openweathermap.org/full-price.

        Args:
            location (str, optional): city name, state code (only for the US) and country code divided by comma.
            zip_code (str, optional): zip/post code and country code divided by comma.
        """
        logger.info(
            f"The client {self} is being requested hourly weather forecast in the location {location or zip_code}..."
        )
        if not self.is_alive:
            raise ClientDoesntExistException(self)
        if not location and not zip_code:
            raise InvalidLocationException(
                "You need to specify the location or postal code."
            )
        if location:
            if not isinstance(location, str):
                raise InvalidLocationException(
                    "You need to specify the location as a string."
                )
            return self._get_location_forecast_hourly(location)
        if zip_code:
            if not isinstance(zip_code, str):
                raise InvalidLocationException(
                    "You need to specify zip code as a string"
                )
            return self._get_zip_code_forecast_hourly(zip_code)

    def weather_forecast_daily_16_days(self, location=None, zip_code=None):
        """
        Returns 16 days weather forecast data at specified location.
        The location can be provided either as a combination of city name,
        state code (for the US), and country code separated by commas, or
        as a combination of zip/post code and country code separated by commas.
        Please ensure the usage of ISO 3166 country codes.

        Accessible with a "Startup" subscription and higher. See: https://openweathermap.org/full-price.

        Args:
            location (str, optional): city name, state code (only for the US) and country code divided by comma.
            zip_code (str, optional): zip/post code and country code divided by comma.
        """
        logger.info(
            f"The client {self} is being requested 16 days weather forecast in the location {location or zip_code}..."
        )
        if not self.is_alive:
            raise ClientDoesntExistException(self)
        if not location and not zip_code:
            raise InvalidLocationException(
                "You need to specify the location or postal code."
            )
        if location:
            if not isinstance(location, str):
                raise InvalidLocationException(
                    "You need to specify the location as a string."
                )
            return self._get_location_forecast_daily_16_days(location)
        if zip_code:
            if not isinstance(zip_code, str):
                raise InvalidLocationException(
                    "You need to specify zip code as a string"
                )
            return self._get_zip_code_forecast_daily_16_days(zip_code)

    def weather_forecast_daily_30_days(self, location=None, zip_code=None):
        """
        Returns 30 days weather forecast data at specified location.
        The location can be provided either as a combination of city name,
        state code (for the US), and country code separated by commas, or
        as a combination of zip/post code and country code separated by commas.
        Please ensure the usage of ISO 3166 country codes.

        Accessible with a "Developer" subscription and higher. See: https://openweathermap.org/full-price.

        Args:
            location (str, optional): city name, state code (only for the US) and country code divided by comma.
            zip_code (str, optional): zip/post code and country code divided by comma.
        """
        logger.info(
            f"The client {self} is being requested 30 days weather forecast in the location {location or zip_code}..."
        )
        if not self.is_alive:
            raise ClientDoesntExistException(self)
        if not location and not zip_code:
            raise InvalidLocationException(
                "You need to specify the location or postal code."
            )
        if location:
            if not isinstance(location, str):
                raise InvalidLocationException(
                    "You need to specify the location as a string."
                )
            return self._get_location_forecast_daily_30_days(location)
        if zip_code:
            if not isinstance(zip_code, str):
                raise InvalidLocationException(
                    "You need to specify zip code as a string"
                )
            return self._get_zip_code_forecast_daily_30_days(zip_code)

    def current_air_pollution(self, location=None, zip_code=None):
        """
        Returns current air pollution in a specified location.
        The location can be provided either as a combination of city name,
        state code (for the US), and country code separated by commas, or
        as a combination of zip/post code and country code separated by commas.
        Please ensure the usage of ISO 3166 country codes.

        Args:
            location (str, optional): city name, state code (only for the US) and country code divided by comma.
            zip_code (str, optional): zip/post code and country code divided by comma.
        """
        logger.info(
            f"The client {self} is being requested the current air pollution in the location {location or zip_code}..."
        )
        if not self.is_alive:
            raise ClientDoesntExistException(self)
        if not location and not zip_code:
            raise InvalidLocationException(
                "You need to specify the location or postal code."
            )
        if location:
            if not isinstance(location, str):
                raise InvalidLocationException(
                    "You need to specify the location as a string."
                )
            return self._get_location_current_air_pollution(location)
        if zip_code:
            if not isinstance(zip_code, str):
                raise InvalidLocationException(
                    "You need to specify zip code as a string"
                )
            return self._get_zip_code_current_air_pollution(zip_code)

    def air_pollution_forecast_hourly(self, location=None, zip_code=None):
        """
        Returns hourly air_pollution forecast for 4 days (96 timestamps) at specified location.
        The location can be provided either as a combination of city name,
        state code (for the US), and country code separated by commas, or
        as a combination of zip/post code and country code separated by commas.
        Please ensure the usage of ISO 3166 country codes.

        Args:
            location (str, optional): city name, state code (only for the US) and country code divided by comma.
            zip_code (str, optional): zip/post code and country code divided by comma.
        """
        logger.info(
            f"The client {self} is being requested the air pollution forecast in the location {location or zip_code}..."
        )
        if not self.is_alive:
            raise ClientDoesntExistException(self)
        if not location and not zip_code:
            raise InvalidLocationException(
                "You need to specify the location or postal code."
            )
        if location:
            if not isinstance(location, str):
                raise InvalidLocationException(
                    "You need to specify the location as a string."
                )
            return self._get_location_forecast_air_pollution(location)
        if zip_code:
            if not isinstance(zip_code, str):
                raise InvalidLocationException(
                    "You need to specify zip code as a string"
                )
            return self._get_zip_code_forecast_air_pollution(zip_code)

    def air_pollution_history(self, location=None, zip_code=None, start=None, end=None):
        """
        Returns historical air_pollution data at specified location from start data to end.
        Historical data is accessible from 27th November 2020.
        The location can be provided either as a combination of city name,
        state code (for the US), and country code separated by commas, or
        as a combination of zip/post code and country code separated by commas.
        Please ensure the usage of ISO 3166 country codes.

        Args:
            location (str, optional): city name, state code (only for the US) and country code divided by comma.
            zip_code (str, optional): zip/post code and country code divided by comma.
            start (int): start date (unix time, UTC time zone), e.g. start=1606488670.
            end (int): end date (unix time, UTC time zone), e.g. end=1606747870.
        """
        logger.info(
            f"The client {self} is being requested the forecast air histoty in the location {location or zip_code}... from {start} to {end}"
        )
        if not self.is_alive:
            raise ClientDoesntExistException(self)
        if not location and not zip_code:
            raise InvalidLocationException(
                "You need to specify the location or postal code."
            )
        start, end = _validate_time(start, end)
        if location:
            if not isinstance(location, str):
                raise InvalidLocationException(
                    "You need to specify the location as a string."
                )
            return self._get_location_history_air_pollution(location, start, end)
        if zip_code:
            if not isinstance(zip_code, str):
                raise InvalidLocationException(
                    "You need to specify zip code as a string"
                )
            return self._get_zip_code_history_air_pollution(zip_code, start, end)
