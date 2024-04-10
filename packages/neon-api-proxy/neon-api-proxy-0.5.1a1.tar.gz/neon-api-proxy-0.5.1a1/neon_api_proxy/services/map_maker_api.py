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
from os import getenv
from time import time, sleep
from requests import Response
from ovos_utils.log import LOG

from neon_api_proxy.cached_api import CachedAPI


class MapMakerAPI(CachedAPI):
    """
    API for querying My Maps API (geocoder.maps.co).
    """

    def __init__(self, api_key: str = None, cache_seconds=604800):  # Cache week
        super().__init__("map_maker")
        self._api_key = api_key or getenv("MAP_MAKER_KEY")
        if not self._api_key:
            raise RuntimeError(f"No API key provided for Map Maker")
        self._rate_limit_seconds = 1
        self._last_query = time()
        self.cache_timeout = timedelta(seconds=cache_seconds)
        self.geocode_url = "https://geocode.maps.co/search"
        self.reverse_url = "https://geocode.maps.co/reverse"

    def handle_query(self, **kwargs) -> dict:
        """
        Handles an incoming query and provides a response
        :param kwargs:
          'lat' - optional str latitude
          'lon' - optional str longitude
          'address' - optional string address/place to resolve
        :return: dict containing `status_code`, `content`, `encoding`
            from URL response
        """
        lat = kwargs.get("lat")
        lon = kwargs.get("lon", kwargs.get("lng"))
        address = kwargs.get('address')

        if not (address or (lat and lon)):
            # Missing data for lookup
            return {"status_code": -1,
                    "content": f"Incomplete request data: {kwargs}",
                    "encoding": None}

        if self._rate_limit_seconds:
            sleep_time = round(self._rate_limit_seconds -
                               (time() - self._last_query), 3)
            if sleep_time > 0:
                LOG.info(f"Waiting {sleep_time}s before next API query")
                sleep(sleep_time)

        if lat and lon:
            # Lookup address for coordinates
            try:
                response = self._query_reverse(float(lat), float(lon))
            except ValueError as e:
                return {"status_code": -1,
                        "content": repr(e),
                        "encoding": None}
        else:
            # Lookup coordinates for search term/address
            response = self._query_geocode(address)
        self._last_query = time()
        return {"status_code": response.status_code,
                "content": response.content,
                "encoding": response.encoding}

    def _query_geocode(self, address: str) -> Response:
        query_str = urllib.parse.urlencode({"q": address,
                                            "api_key": self._api_key})
        request_url = f"{self.geocode_url}?{query_str}"
        return self.get_with_cache_timeout(request_url, self.cache_timeout)

    def _query_reverse(self, lat: float, lon: float):
        query_str = urllib.parse.urlencode({"lat": lat, "lon": lon,
                                            "api_key": self._api_key})
        request_url = f"{self.reverse_url}?{query_str}"
        return self.get_with_cache_timeout(request_url, self.cache_timeout)
