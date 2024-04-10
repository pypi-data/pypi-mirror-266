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

from enum import Enum
from typing import Union
from ovos_utils.log import LOG
from neon_api_proxy.client import NeonAPI, request_api
from neon_utils.net_utils import get_ip_address


class QueryApi(Enum):
    def __repr__(self):
        return self.value

    SIMPLE = "simple"
    SHORT = "short"
    SPOKEN = "spoken"
    FULL = "full"
    RECOGNIZE = "recognize"
    CONVERSATION = "conversation"


def get_wolfram_alpha_response(query: str, api: QueryApi,
                               units: str = "metric",
                               **kwargs) -> Union[str, bytes]:
    """
    Queries Wolfram|Alpha for a response from the specified API with the
        specified parameters
    :param query: Question to submit to Wolfram|Alpha
    :param api: API to target
    :param units: "metric" or "nonmetric" units
    :param kwargs:
      'lat' - optional str latitude
      'lng' - optional str longitude
      'ip' - optional str public IP for geolocation
      'app_id' - optional str app_id to use for query
    :return: str text response or bytes response for 'full'
    """
    query_params = get_geolocation_params(**kwargs)
    query_params["units"] = units
    query_params["query"] = query
    query_params["api"] = repr(api)
    resp = request_api(NeonAPI.WOLFRAM_ALPHA, query_params)

    if resp["status_code"] != 200:
        LOG.error(f"Non-success response: {resp}")  # TODO: Handle failures
        if resp["status_code"] == 403:
            LOG.error(f"Invalid credential provided.")
    if isinstance(resp.get("content"), str):
        return resp["content"]
    elif resp.get("encoding"):
        try:
            return resp["content"].decode(resp["encoding"])
        except Exception as e:
            LOG.exception(e)
            return resp.get("content")
    else:
        LOG.info("Returning bytes content")
        return resp["content"]


def api_to_url(api: QueryApi) -> str:
    """
    Translates a wolfram API to a URL
    :param api: QueryApi to call
    :return: base URL
    """
    if not api:
        raise ValueError("api is null")
    if not isinstance(api, QueryApi):
        raise TypeError(f"Not a QueryApi: {api}")
    url_map = {
        QueryApi.SIMPLE: "http://api.wolframalpha.com/v2/simple",
        QueryApi.SHORT: "http://api.wolframalpha.com/v2/result",
        QueryApi.SPOKEN: "http://api.wolframalpha.com/v2/spoken",
        QueryApi.FULL: "http://api.wolframalpha.com/v2/query",
        QueryApi.RECOGNIZE: "http://www.wolframalpha.com/queryrecognizer/"
                            "query.jsp",
        QueryApi.CONVERSATION: "http://api.wolframalpha.com/v1/"
                               "conversation.jsp"}
    return url_map[api]


def get_geolocation_params(**kwargs) -> dict:
    """
    Returns a valid dict of data for geolocation (lat/lng or ip)
    :param kwargs:
      'lat' - optional str latitude
      'lng' - optional str longitude
      'ip' - optional str public IP for geolocation
    :return: dict with latlong or ip
    """
    if kwargs.get("lat") and kwargs.get("lng"):
        return {"latlong": f'{kwargs.get("lat")},{kwargs.get("lng")}'}
    elif kwargs.get("ip"):
        return {"ip": kwargs.get("ip")}
    else:
        return {"ip": get_ip_address()}
