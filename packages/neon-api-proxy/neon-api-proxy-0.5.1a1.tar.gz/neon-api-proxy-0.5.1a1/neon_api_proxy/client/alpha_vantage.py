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

from json import JSONDecodeError
from ovos_utils.log import LOG
from neon_api_proxy.client import NeonAPI, request_api


def _get_response_data(resp: dict) -> dict:
    """
    Safely parse the API response data into a dict that can be safely parsed.
    :param resp: dict HTTP response from the API
    :returns: parsed dict data
    """
    if resp["status_code"] == -1:
        data = {"error": resp["content"]}
    else:
        try:
            data = json.loads(resp["content"])
        except JSONDecodeError:
            data = {"error": "Error decoding response",
                    "response": resp}
    if data.get("Information"):
        LOG.warning(data.get("Information"))
        # TODO: Handle API Errors DM
    return data


def search_stock_by_name(company: str, **kwargs) -> list:
    """
    Queries Alpha Vantage for stocks matching the specified company
    :param company: Company name/stock search term
    :param kwargs:
      'api_key' - optional str api_key to use for query
      'region' - optional preferred region (default `United States`)
    :return: list of dict matched stock data
    """
    region = kwargs.get("region") or "United States"
    query_params = {**kwargs, **{"api": "symbol", "company": company}}
    resp = request_api(NeonAPI.ALPHA_VANTAGE, query_params)
    data = _get_response_data(resp)

    if not data.get("bestMatches"):
        LOG.warning(f"No matches found for {company}")
        return []
    filtered_data = [stock for stock in data.get("bestMatches") if
                     stock.get("4. region") == region]
    if not filtered_data:
        filtered_data = data.get("bestMatches")
    data = [{"symbol": stock.get("1. symbol"),
             "name": stock.get("2. name"),
             "region": stock.get("4. region"),
             "currency": stock.get("8. currency")} for stock in filtered_data]
    return data


def get_stock_quote(symbol: str, **kwargs) -> dict:
    """
    Queries Alpha Vantage for stock information for the specified company
    :param symbol: Stock ticker symbol
    :param kwargs:
      'api_key' - optional str api_key to use for query
    :return: dict stock data
    """
    query_params = {**kwargs, **{"api": "quote", "symbol": symbol}}
    resp = request_api(NeonAPI.ALPHA_VANTAGE, query_params)
    data = _get_response_data(resp)

    if not data.get("Global Quote"):
        LOG.warning(f"No data found for {symbol}")
        data["error"] = data.get("error") or "No data found"
        LOG.error(data)
        return data
    return {"symbol": data.get("Global Quote")["01. symbol"],
            "price": data.get("Global Quote")["05. price"],
            "close": data.get("Global Quote")["08. previous close"]}
