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


def search_stock_by_name(company: str, **kwargs) -> list:
    """
    Queries FMP for stocks matching the specified company
    :param company: Company name/stock search term
    :param kwargs:
      'api_key' - optional str api_key to use for query
      'exchange' - optional preferred exchange (default None)
    :return: list of dict matched stock data (`name`, `symbol`)
    """
    raise NotImplementedError("API Not implemented")
    # resp = query_fmp_api(f"https://financialmodelingprep.com/api/v3/search?
    # {urllib.parse.urlencode(query_params)}")
    # query_params = {**kwargs, **{"api": "symbol",
    #                              "query": company,
    #                              "limit": 10}}
    # resp = request_api(NeonAPI.FINANCIAL_MODELING_PREP, query_params)
    # data = json.loads(resp["content"])
    # return data


def get_stock_quote(symbol: str, **kwargs) -> dict:
    """
    Queries FMP for stock information for the specified company
    :param symbol: Stock ticker symbol
    :param kwargs:
      'api_key' - optional str api_key to use for query
    :return: dict stock data
    """
    raise NotImplementedError("API Not implemented")
    # resp = query_fmp_api(f"https://financialmodelingprep.com/api/v3/
    # company/profile/{symbol}?"
    #                      f"{urllib.parse.urlencode(query_params)}")
    # query_params = {**kwargs, **{"api": "quote",
    #                              "symbol": symbol}}
    # resp = request_api(NeonAPI.FINANCIAL_MODELING_PREP, query_params)
    # data = json.loads(resp["content"])
    # return data.get("profile")
