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

import urllib.parse
from datetime import timedelta

from requests import Response

from neon_api_proxy.cached_api import CachedAPI
from ovos_utils.log import LOG
from neon_utils.authentication_utils import find_neon_owm_key


class OpenWeatherAPI(CachedAPI):
    """
    API for querying Open Weather Map.
    """

    def __init__(self, api_key: str = None, cache_seconds=180):
        super().__init__("open_weather_map")
        self._api_key = api_key or find_neon_owm_key()
        self.cache_timeout = timedelta(seconds=cache_seconds)

    def handle_query(self, **kwargs) -> dict:
        """
        Handles an incoming query and provides a response
        :param kwargs:
          'lat' - str latitude
          'lng' - str longitude
          'units' - optional string "metric" or "imperial"
          'base_url' - base URL to target
        :return: dict containing `status_code`, `content`, `encoding`
            from URL response
        """
        lat = kwargs.get("lat")
        lng = kwargs.get("lng", kwargs.get("lon"))
        api = kwargs.get('api') or "onecall"
        lang = kwargs.get('lang') or "en"
        units = "metric" if kwargs.get("units") == "metric" else "imperial"

        if not all((lat, lng, units)):
            return {"status_code": -1,
                    "content": f"Missing required args in: {kwargs}",
                    "encoding": None}
        try:
            resp = self._get_api_response(lat, lng, units, api, lang)
        except Exception as e:
            return {"status_code": -1,
                    "content": repr(e),
                    "encoding": None}
        if not resp.ok:
            LOG.error(f"Bad response code: {resp.status_code}")
        return {"status_code": resp.status_code,
                "content": resp.content,
                "encoding": resp.encoding}

    def _get_api_response(self, lat: str, lng: str, units: str,
                          api: str = "onecall", lang: str = "en") -> Response:
        str(float(lat))
        str(float(lng))
        assert units in ("metric", "imperial", "standard")
        query_params = {"lat": lat,
                        "lon": lng,
                        "appid": self._api_key,
                        "units": units,
                        "lang": lang}
        query_str = urllib.parse.urlencode(query_params)
        base_url = "http://api.openweathermap.org/data/2.5"
        resp = self.get_with_cache_timeout(f"{base_url}/{api}?{query_str}",
                                           self.cache_timeout)
        return resp
