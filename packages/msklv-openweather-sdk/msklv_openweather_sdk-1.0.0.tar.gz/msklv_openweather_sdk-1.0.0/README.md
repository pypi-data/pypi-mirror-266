# OpenWeatherSDK

## Introduction

SDK for accessing to [OpenWeatherAPI](https://openweathermap.org/api) and
retrieving information about current weather conditions in a specified city.
The SDK can operate in two modes: *on-demand* and *polling*. In *on-demand*
mode (the default mode), API requests are made on user demand, while in the
*polling* mode, there is regular polling of the API for weather updates in the
saved (previously requested) cities.

## Contents

[Installation](#installation)

[Prerequisites](#prerequisites)

[Client initialization](#client-initialization)

[Cache](#cache)

[Polling mode](#polling-mode)

[Available requests (for versions from 1.0.0)](#available-requests)

[Weather request (for versions up to 1.0.0)](#weather-request)

[Logging](#logging)

[Errors](#errors)

## Installation

```python
pip install msklv-openweather-sdk
```

## Prerequisites

To work with the SDK, you need to obtain an access token for OpenWeatherAPI.
More information can be found on [FAQ page](https://openweathermap.org/faq)
("Get started" section -> "How to get an API key").

## Client initialization

The only required argument is [the access token](#prerequisites).

By default, the SDK operates in on-demand mode, returns information in English,
uses the metric system of measurements, has a cache size of 10 locations, and
the information remains valid for 10 minutes. You can modify this mode by
passing additional arguments during client initialization.

Additionally, if you need to modify the behavior of the SDK, you can pass
[additional arguments](#additional-arguments).

### Additional arguments

`mode` - determines the operating mode of the SDK. In on-demand mode, the SDK
makes requests to the API only upon client requests. In polling mode, the SDK
regularly polls the API. Defaults: on-demand. Available options: on-demand, [polling](#polling-mode).

`language` - determines the language for the output. Defaults: en. Available
options and more info see [here](https://openweathermap.org/current#multi).

`units` - determines the units of measurements for the output. Defaults:
metric. Available options and more info see
[here](https://openweathermap.org/current#data).

`cache_size` - determines the number of stored locations in cache. Defaults: 10.

`ttl` - determines the Time-To-Live of information in cache (in secs). Defaults:
600. 

## Cache

Each client has its own cache, defined by the number of stored locations and
the Time-To-Live (TTL) of the information. In polling mode, the TTL determines
the API polling interval.

## Polling mode

Note, that polling works only for current weather reaquests!
All other requests operate in 'on-demand' mode regardless of the mode selected
during client initialization.

## Available requests

This section is actual for versions from 1.0.0. For older versions, see the
[outdated weather requests](#outdated-weather-requests) section.

Starting from version 1.0.0, the following requests are available:

1. [current weather](#current-weather)
1. [5 days weather forecast data with 3-hour step](#5-days-weather-forecast)
1. [hourly weather forecast for 4 days](#hourly-weather-forecast)
1. [16 days weather forecast](#16-days-weather-forecast)
1. [30 days weather forecast](#30-days-weather-forecast)
1. [current air pollution](#current-air-pollution)
1. [hourly air pollution forecast for 4 days](#hourly-air-pollution-forecast)
1. [historical air pollution data](#historical-air-pollution-data)
1. [health check](#health-check)

### Current weather

Returns current weather in a specified location.
The location can be provided either as a combination of city name,
state code (for the US), and country code separated by commas, or
as a combination of zip/post code and country code separated by commas.

Please ensure the usage of ISO 3166 country codes.

Args:

`location` *(str, optional)*: city name, state code (only for the US) and country code divided by comma.

`zip_code` *(str, optional)*: zip/post code and country code divided by comma.

#### Request examples

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.current_weather(location="Paris")
```

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.current_weather(zip_code="75007,FR")
```

#### Response

See exemple on[openweathermap.org](https://openweathermap.org/current#example_JSON).

### 5 days weather forecast

Returns 5 days weather forecast data with 3-hour step at specified location.
The location can be provided either as a combination of city name,
state code (for the US), and country code separated by commas, or
as a combination of zip/post code and country code separated by commas.

Please ensure the usage of ISO 3166 country codes.

Args:

`location` *(str, optional)*: city name, state code (only for the US) and country code divided by comma.

`zip_code` *(str, optional)*: zip/post code and country code divided by comma.

#### Request examples

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.weather_forecast_5_days(location="Paris")
```

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.weather_forecast_5_days(zip_code="75007,FR")
```

#### Response

See exemple on [openweathermap.org](https://openweathermap.org/forecast5#example_JSON).

### Hourly weather forecast

Returns hourly weather forecast for 4 days (96 timestamps) at specified location.
The location can be provided either as a combination of city name,
state code (for the US), and country code separated by commas, or
as a combination of zip/post code and country code separated by commas.

Please ensure the usage of ISO 3166 country codes.

Accessible with a "Developer" subscription and higher. See: https://openweathermap.org/full-price.

Args:

`location` *(str, optional)*: city name, state code (only for the US) and country code divided by comma.

`zip_code` *(str, optional)*: zip/post code and country code divided by comma.

#### Request examples

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.weather_forecast_hourly(location="Paris")
```

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.weather_forecast_hourly(zip_code="75007,FR")
```

#### Response

See exemple on [openweathermap.org](https://openweathermap.org/api/hourly-forecast#example_JSON).

### 16 days weather forecast

Returns 16 days weather forecast data at specified location.
The location can be provided either as a combination of city name,
state code (for the US), and country code separated by commas, or
as a combination of zip/post code and country code separated by commas.

Please ensure the usage of ISO 3166 country codes.

Accessible with a "Startup" subscription and higher. See: https://openweathermap.org/full-price.

Args:

`location` *(str, optional)*: city name, state code (only for the US) and country code divided by comma.

`zip_code` *(str, optional)*: zip/post code and country code divided by comma.

#### Request examples

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.weather_forecast_daily_16_days(location="Paris")
```

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.weather_forecast_daily_16_days(zip_code="75007,FR")
```

#### Response

See exemple on [openweathermap.org](https://openweathermap.org/forecast16#example_JSON).

### 30 days weather forecast

Returns 30 days weather forecast data at specified location.
The location can be provided either as a combination of city name,
state code (for the US), and country code separated by commas, or
as a combination of zip/post code and country code separated by commas.

Please ensure the usage of ISO 3166 country codes.

Accessible with a "Developer" subscription and higher. See: https://openweathermap.org/full-price.

Args:

`location` *(str, optional)*: city name, state code (only for the US) and country code divided by comma.

`zip_code` *(str, optional)*: zip/post code and country code divided by comma.

#### Request examples

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.weather_forecast_daily_30_days(location="Paris")
```

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.weather_forecast_daily_30_days(zip_code="75007,FR")
```

#### Response

See exemple on [openweathermap.org](https://openweathermap.org/api/forecast30#resp-year).

### Current air pollution

Returns current air pollution in a specified location.
The location can be provided either as a combination of city name,
state code (for the US), and country code separated by commas, or
as a combination of zip/post code and country code separated by commas.

Please ensure the usage of ISO 3166 country codes.

Args:

`location` *(str, optional)*: city name, state code (only for the US) and country code divided by comma.

`zip_code` *(str, optional)*: zip/post code and country code divided by comma.

#### Request examples

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.current_air_pollution(location="Paris")
```

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.current_air_pollution(zip_code="75007,FR")
```

#### Response

See exemple on [openweathermap.org](https://openweathermap.org/api/air-pollution#descr).

### Hourly air pollution forecast

Returns hourly air_pollution forecast for 4 days (96 timestamps) at specified location.
The location can be provided either as a combination of city name,
state code (for the US), and country code separated by commas, or
as a combination of zip/post code and country code separated by commas.

Please ensure the usage of ISO 3166 country codes.

Args:

`location` *(str, optional)*: city name, state code (only for the US) and country code divided by comma.

`zip_code` *(str, optional)*: zip/post code and country code divided by comma.

#### Request examples

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.air_pollution_forecast_hourly(location="Paris")
```

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.air_pollution_forecast_hourly(zip_code="75007,FR")
```

#### Response

See exemple on [openweathermap.org](https://openweathermap.org/api/air-pollution#descr).
   
### Historical air pollution data

Returns historical air_pollution data at specified location from start data to end.
Historical data is accessible from 27th November 2020.
The location can be provided either as a combination of city name,
state code (for the US), and country code separated by commas, or
as a combination of zip/post code and country code separated by commas.

Please ensure the usage of ISO 3166 country codes.

Args:

`location` *(str, optional)*: city name, state code (only for the US) and country code divided by comma.

`zip_code` *(str, optional)*: zip/post code and country code divided by comma.

`start` *(int)*: start date (unix time, UTC time zone), e.g. start=1606488670.

`end` *(int)*: end date (unix time, UTC time zone), e.g. end=1606747870.

#### Request examples

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.current_weather(location="Paris")
```

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.current_weather(zip_code="75007,FR")
```

#### Response

See exemple on [openweathermap.org](https://openweathermap.org/api/air-pollution#descr).

### Health check

Returns HTTP response's status.

#### Request examples

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.health_check()
```

#### Response

```python
200
```

## Outdated weather requests

**Outdated. Relevant for versions up to 1.0.0!**

**Available requests for versions from 1.0.0 see [here](#available-requests).**

Currently, handling requests for current weather by location name or zip code is
implemented.

By default, the response is returned in a compact format. You can change this
behavior by passing an [additional argument](#additional-arguments-1).

Compact format has been be deprecated in
[version 1.0.0](https://github.com/maskalev/openweather_sdk/blob/master/CHANGELOG.md#unreleased)!

Also, refer to [the example queries](#usage-example).

### Weather request by location name

To request weather by location name, you need to pass the city name as an 
argument, and optionally the state code (only for the US) and country code, 
separated by commas. 

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.get_location_weather("Paris")
```

The `get_location_weather` method has been deprecated in
[version 1.0.0](https://github.com/maskalev/openweather_sdk/blob/master/CHANGELOG.md#unreleased).

Starting from version 0.3.2, it is recommended to use the `current_weather`
method with the city name as an `location` argument, and optionally the state
code (only for the US) and country code, separated by commas.

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.current_weather(location="Paris")
```

Please use
[ISO 3166](https://www.iso.org/iso-3166-country-codes.html) country codes.

### Weather request by zip code

To request weather by location name, you need to pass as an argument zip/post 
code and country code divided by comma.

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.get_zip_weather("75007,FR")
```

The `get_zip_weather` method has been deprecated in
[version 1.0.0](https://github.com/maskalev/openweather_sdk/blob/master/CHANGELOG.md#unreleased).

Starting from version 0.3.2, it is recommended to use the `current_weather`
method with an `zip_code` argument zip/post code and country code divided by
comma.

```python
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.current_weather(zip_code="75007,FR")
```

Please use
[ISO 3166](https://www.iso.org/iso-3166-country-codes.html) country codes.

### Additional arguments

`compact_mode` - determines whether to return the response in a compact format.
Defaults: True.

The `compact_mode` has been deprecated in
[version 1.0.0](https://github.com/maskalev/openweather_sdk/blob/master/CHANGELOG.md#unreleased).

### Description of response formats

#### Compact format (used by default)

The `compact_mode` has been deprecated in
[version 1.0.0](https://github.com/maskalev/openweather_sdk/blob/master/CHANGELOG.md#unreleased).


```json
{
    "weather": {
        "main": "Clear",
        "description": "clear sky"
    }, 
    "temperature": {
        "temp": 8.19,
        "feels_like": 7.03
    }, 
    "visibility": 10000, 
    "wind": {
        "speed": 2.06
    }, 
    "datatime": 1710099501, 
    "sys": {
        "sunrise": 1710051241,
        "sunset": 1710092882
    }, 
    "timezone": 3600, 
    "name": "Palais-Royal"
}
```

`weather.main` - group of weather parameters (Rain, Snow, Clouds etc.).

`weather.description` - weather condition within the group. More info see
[here](https://openweathermap.org/weather-conditions).

`temperature.temp` - temperature. Unit Standart: Kelvin, Metric: Celsius,
Imperial: Fahrenheit.

`temperature.feels_like` - temperature. This temperature parameter accounts for
the human perception of weather. Unit Standart: Kelvin, Metric: Celsius,
Imperial: Fahrenheit.

`visibility` - visibility, meter. The maximum value of the visibility is 10 km.

`wind.speed` - wind speed. Unit Standart: meter/sec, Metric: meter/sec,
Imperial: miles/hour.

`datatime` - time of data calculation, unix, UTC.

`sys.sunrise` - sunrise time, unix, UTC.

`sys.sunset` - sunset time, unix, UTC.

`timezone` - shift in seconds from UTC.

`name` - city name.

#### Full format

```json
{
    "coord": {
        "lon": 2.32,
        "lat": 48.858
    },
    "weather": [
        {
            "id": 800,
            "main": "Clear",
            "description": "clear sky",
            "icon": "01n"
        }
    ],
    "base": "stations",
    "main": {
        "temp": 8.19,
        "feels_like": 7.03,
        "temp_min": 6.07,
        "temp_max": 9.42,
        "pressure": 998,
        "humidity": 86
    },
    "visibility": 10000,
    "wind": {
        "speed": 2.06,
        "deg": 220
    },
    "clouds": {
        "all": 0
    },
    "dt": 1710099501,
    "sys": {
        "type": 2,
        "id": 2012208,
        "country": "FR",
        "sunrise": 1710051241,
        "sunset": 1710092882
    },
    "timezone": 3600,
    "id": 6545270,
    "name": "Palais-Royal",
    "cod": 200
}
```

Description of full format see
[here](https://openweathermap.org/current#fields_json)

### Usage example

```python
>>> from openweather_sdk import Client
>>> c = Client(token=<YOUR_TOKEN>)
>>> c.health_check()
200
>>> c.get_location_weather("Paris")  # request by location name
{
    "weather": {
        "main": "Clear",
        "description": "clear sky"
    }, 
    "temperature": {
        "temp": 8.19,
        "feels_like": 7.03
    }, 
    "visibility": 10000, 
    "wind": {
        "speed": 2.06
    }, 
    "datatime": 1710099501, 
    "sys": {
        "sunrise": 1710051241,
        "sunset": 1710092882
    }, 
    "timezone": 3600, 
    "name": "Palais-Royal"
}
>>> c.get_location_weather("Paris", compact_mode=False)
{
    "coord": {
        "lon": 2.32,
        "lat": 48.858
    },
    "weather": [
        {
            "id": 800,
            "main": "Clear",
            "description": "clear sky",
            "icon": "01n"
        }
    ],
    "base": "stations",
    "main": {
        "temp": 8.19,
        "feels_like": 7.03,
        "temp_min": 6.07,
        "temp_max": 9.42,
        "pressure": 998,
        "humidity": 86
    },
    "visibility": 10000,
    "wind": {
        "speed": 2.06,
        "deg": 220
    },
    "clouds": {
        "all": 0
    },
    "dt": 1710099501,
    "sys": {
        "type": 2,
        "id": 2012208,
        "country": "FR",
        "sunrise": 1710051241,
        "sunset": 1710092882},
    "timezone": 3600,
    "id": 6545270,
    "name": "Palais-Royal",
    "cod": 200
}
>>> c.get_zip_weather("75007,FR")  # request by zip code
{
    'weather': {
        'main': 'Clouds',
        'description': 'overcast clouds'
    },
    'temperature': {
        'temp': 10.69,
        'feels_like': 10.06
    },
    'visibility': 10000,
    'wind': {
        'speed': 4.63
    },
    'datatime': 1710577539,
    'sys': {
        'sunrise': 1710568880,
        'sunset': 1710611823
    },
    'timezone': 3600,
    'name': 'Paris'
}
>>> c.get_zip_weather("75007,FR", compact_mode=False)
{
    'coord': {
        'lon': 2.3486,
        'lat': 48.8534
    },
    'weather': [
        {
            'id': 804,
            'main': 'Clouds',
            'description': 'overcast clouds',
            'icon': '04d'
        }
    ],
    'base': 'stations',
    'main': {
        'temp': 10.69,
        'feels_like': 10.06,
        'temp_min': 10.1,
        'temp_max': 11.54,
        'pressure': 1021,
        'humidity': 86
    },
    'visibility': 10000,
    'wind': {
        'speed': 4.63,
        'deg': 270
    },
    'clouds': {
        'all': 100
    },
    'dt': 1710577539,
    'sys': {
        'type': 2,
        'id': 2041230,
        'country': 'FR',
        'sunrise': 1710568880,
        'sunset': 1710611823
    },
    'timezone': 3600,
    'id': 2988507,
    'name': 'Paris',
    'cod': 200
}
>>> c.remove()
```

## Logging

When using logging, be careful: the `urllib3` library logs sensitive
information (such as API access tokens) when the DEBUG level is enabled!

To disable logging from the `urllib3` library in your project, use this:

```python
import logging
logging.getLogger("urllib3").propagate = False
```

## Errors

Description of possible errors can be found on
[FAQ page](https://openweathermap.org/faq) ("API errors" section).
