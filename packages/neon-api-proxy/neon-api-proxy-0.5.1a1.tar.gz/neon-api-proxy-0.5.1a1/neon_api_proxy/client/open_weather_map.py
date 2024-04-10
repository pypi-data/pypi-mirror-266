# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json
from enum import Enum
from json import JSONDecodeError
from typing import Union
from ovos_utils.log import LOG
from neon_api_proxy.client import NeonAPI, request_api


class OpenWeatherMapApi(Enum):
    def __repr__(self):
        return self.value
    CURRENT = "weather"
    ONECALL = "onecall"


def get_current_weather(lat: Union[str, float], lng: Union[str, float],
                        units: str = "metric", **kwargs) -> dict:
    """
    Queries Open Weather Map for current weather at the specified location
    :param lat: latitude
    :param lng: longitude
    :param units: Units of measure "metric", "imperial", or "standard"
    :param kwargs:
      'api_key' - optional str api_key to use for query
      'language' - optional language param (default english)
    :return: dict weather data (https://openweathermap.org/current#current_JSON)
    """
    forecast = _make_api_call(lat, lng, units,
                              OpenWeatherMapApi.CURRENT, **kwargs)
    if not forecast.get("weather"):
        LOG.warning("Outdated backend API return. Reformatting into current")
        forecast = {"main": forecast["current"],
                    "weather": forecast["current"]["weather"]}
    return forecast


def get_forecast(lat: Union[str, float], lng: Union[str, float],
                 units: str = "metric", **kwargs) -> dict:
    """
    Queries Open Weather Map for weather data at the specified location
    :param lat: latitude
    :param lng: longitude
    :param units: Units of measure "metric", "imperial", or "standard"
    :param kwargs:
      'api_key' - optional str api_key to use for query
      'language' - optional language param (default english)
    :return: dict weather data
        (https://openweathermap.org/api/one-call-api#hist_example)
    """
    return _make_api_call(lat, lng, units, OpenWeatherMapApi.ONECALL, **kwargs)


def _make_api_call(lat: Union[str, float], lng: Union[str, float],
                   units: str, target_api: OpenWeatherMapApi,
                   **kwargs) -> dict:
    """
    Common wrapper for API calls to OWM
    :param lat: latitude
    :param lng: longitude
    :param units: Temperature and Speed units "metric", "imperial", "standard"
    :param target_api: API to query
    :param kwargs:
      'api_key' - optional str api_key to use for query
      'language' - optional language param (default english)
    :return: dict weather data
    """
    query_params = {"lat": lat,
                    "lng": lng,
                    "units": units,
                    "api": repr(target_api),
                    **kwargs}
    resp = request_api(NeonAPI.OPEN_WEATHER_MAP, query_params)

    try:
        data = json.loads(resp["content"])
    except JSONDecodeError:
        data = {"error": "Error decoding response",
                "response": resp}
    if data.get('cod'):
        data['cod'] = str(data['cod'])
        # TODO: Handle failures
    return data
