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

from enum import Enum
from ovos_utils.log import LOG
from neon_utils.authentication_utils import find_neon_wolfram_key
from neon_api_proxy.cached_api import CachedAPI


class QueryUrl(Enum):
    def __str__(self):
        return self.value
    SIMPLE = "http://api.wolframalpha.com/v2/simple"
    SHORT = "http://api.wolframalpha.com/v2/result"
    SPOKEN = "http://api.wolframalpha.com/v2/spoken"
    FULL = "http://api.wolframalpha.com/v2/query"
    RECOGNIZE = "http://www.wolframalpha.com/queryrecognizer/query.jsp"
    CONVERSATION = "http://api.wolframalpha.com/v1/conversation.jsp"


class WolframAPI(CachedAPI):
    """
    API for querying Wolfram|Alpha.
    """

    def __init__(self, api_key: str = None):
        super().__init__("wolfram")
        self._api_key = api_key or find_neon_wolfram_key()
        self.session.allowable_codes = (200, 501)
        self.cache_time = timedelta(minutes=60)

    def _build_query_url(self, query_type: QueryUrl, query_arg: str) -> str:
        """
        Constructs a valid URL for the given query_type and query_arg
        :param query_type: QueryUrl to query
        :param query_arg: string args relating to question
        :return: valid URL to query for a response
        """
        if not query_type:
            raise ValueError(f"query_type not defined!")
        if not query_arg:
            raise ValueError(f"query_url not defined!")
        if not isinstance(query_type, QueryUrl):
            raise TypeError(f"Not a QueryUrl: {query_arg}")
        if not isinstance(query_arg, str):
            raise TypeError(f"Not a string: {query_arg}")
        if query_type == QueryUrl.RECOGNIZE:
            query_arg = f"{query_arg}&mode=Default"
        return f"{query_type}?appid={self._api_key}&{query_arg}"

    @staticmethod
    def _build_query_string(**kwargs) -> str:
        """
        Constructs a valid query string with the given arguments
        :param kwargs:
          'query' - string query to ask Wolfram|Alpha
          'units' - optional string "metric" or "nonmetric"
          'lat'+'lng' optional float or string lat/lng (separate keys)
          'ip' optional string origin IP Address for geolocation
        :return: URL encoded query string used to build a request URL
        """
        if not kwargs.get("query"):
            raise ValueError(f"No query in request: {kwargs}")
        query_params = dict()
        query_params['i'] = kwargs.get("query")
        query_params['units'] = kwargs.get("units") if \
            kwargs.get("units") == "metric" else "nonmetric"
        lat = kwargs.get("lat")
        lng = kwargs.get("lng")
        if kwargs.get("latlong"):
            query_params["latlong"] = kwargs.get("latlong")
        elif lat and lng:
            query_params["latlong"] = f"{lat},{lng}"
        else:
            query_params["ip"] = kwargs.get("ip")

        query_params = {k: v for k, v in query_params.items() if v}
        query_str = urllib.parse.urlencode(query_params)
        return query_str

    def handle_query(self, **kwargs) -> dict:
        """
        Handles an incoming query and provides a response
        :param kwargs:
          'query' - string query to ask Wolfram|Alpha
          'api' - string api to query
                (simple, short, spoken, full, recognize, conversation)
          'units' - optional string "metric" or "nonmetric"
          'latlong' - optional string lat/lng
          'lat'+'lng' - optional float or string lat/lng (separate keys)
          'ip' - optional string origin IP Address for geolocation
        :return: dict containing `status_code`, `content`, `encoding`
            from URL response
        """
        api = kwargs.get("api")
        if not api:
            query_type = QueryUrl.SHORT
        elif api == "simple":
            query_type = QueryUrl.SIMPLE
        elif api == "short":
            query_type = QueryUrl.SHORT
        elif api == "spoken":
            query_type = QueryUrl.SPOKEN
        elif api == "full":
            query_type = QueryUrl.FULL
        elif api == "recognize":
            query_type = QueryUrl.RECOGNIZE
        elif api == "conversation":
            query_type = QueryUrl.CONVERSATION
        else:
            return {"status_code": -1,
                    "content": f"Unknown api requested: {api}",
                    "encoding": None}

        try:
            query_str = self._build_query_string(**kwargs)
            return self._query_api(self._build_query_url(query_type, query_str))
        except Exception as e:
            return {"status_code": -1,
                    "content": repr(e),
                    "encoding": None}

    def _query_api(self, query: str) -> dict:
        """
        Queries the Wolfram|Alpha API and returns a dict with:
            status, content, and encoding
        :param query: URL to query
        :return: dict response containing:
            `status_code`, `content`, and `encoding`
        """
        result = self.get_with_cache_timeout(query, timeout=self.cache_time)
        if not result.ok:
            # 501 = Wolfram couldn't understand
            # 403 = Invalid API Key Provided
            LOG.warning(f"API Query error ({result.status_code}): {query}")
        return {"status_code": result.status_code,
                "content": result.content,
                "encoding": result.encoding}
