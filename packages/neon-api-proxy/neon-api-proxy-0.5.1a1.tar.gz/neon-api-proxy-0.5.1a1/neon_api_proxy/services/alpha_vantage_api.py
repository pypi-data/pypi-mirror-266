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
from neon_api_proxy.cached_api import CachedAPI
from neon_utils.authentication_utils import find_neon_alpha_vantage_key


class QueryUrl(Enum):
    def __str__(self):
        return self.value
    SYMBOL = "https://www.alphavantage.co/query?function=SYMBOL_SEARCH"
    # keywords=, apikey=
    QUOTE = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE"
    # symbol=, apikey=


class AlphaVantageAPI(CachedAPI):
    """
    API for querying Alpha Vantage.
    """

    def __init__(self, api_key: str = None):
        super().__init__("alpha_vantage")
        self._api_key = api_key or find_neon_alpha_vantage_key()
        self.quote_timeout = timedelta(minutes=5)

    def _search_symbol(self, query: str) -> dict:
        if not query:
            raise ValueError(f"Query is None")
        elif not isinstance(query, str):
            raise TypeError(f"Query is not a str: {query} ({type(query)})")
        query_params = {"keywords": query,
                        "apikey": self._api_key}
        query_str = urllib.parse.urlencode(query_params)
        resp = self.get_with_cache_timeout(f"{QueryUrl.SYMBOL}&{query_str}")
        return {"status_code": resp.status_code,
                "content": resp.content,
                "encoding": resp.encoding}

    def _get_quote(self, symbol: str):
        if not symbol:
            raise ValueError(f"symbol is None")
        elif not isinstance(symbol, str):
            raise TypeError(f"symbol is not a str: {symbol} ({type(symbol)})")
        query_params = {"symbol": symbol,
                        "apikey": self._api_key}
        query_str = urllib.parse.urlencode(query_params)
        resp = self.get_with_cache_timeout(f"{QueryUrl.QUOTE}&{query_str}",
                                           self.quote_timeout)
        return {"status_code": resp.status_code,
                "content": resp.content,
                "encoding": resp.encoding}

    def handle_query(self, **kwargs) -> dict:
        """
        Handles an incoming query and provides a response
        :param kwargs:
          'symbol' - optional string stock symbol to query
          'company' - optional string company name to query
          'api' - optional string 'symbol' or 'quote'
        :return: dict containing stock data from URL response
        """
        symbol = kwargs.get('symbol')
        company = kwargs.get('company', kwargs.get('keywords'))
        search_term = symbol or company
        if not search_term:
            return {"status_code": -1,
                    "content": f"No search term provided",
                    "encoding": None}

        api = kwargs.get("api")
        if not api:
            query_type = QueryUrl.QUOTE
        elif api == "symbol":
            query_type = QueryUrl.SYMBOL
        elif api == "quote":
            query_type = QueryUrl.QUOTE
        else:
            return {"status_code": -1,
                    "content": f"Unknown api requested: {api}",
                    "encoding": None}

        try:
            if query_type == QueryUrl.SYMBOL:
                return self._search_symbol(search_term)
            elif query_type == QueryUrl.QUOTE:
                if not symbol:
                    return {"status_code": -1,
                            "content": f"No symbol provided",
                            "encoding": None}
                else:
                    return self._get_quote(symbol)
        except Exception as e:
            return {"status_code": -1,
                    "content": repr(e),
                    "encoding": None}
