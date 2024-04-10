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

from typing import Union
from requests_cache import CachedSession, ExpirationTime, CachedResponse
from abc import abstractmethod
from requests import Response
from requests.adapters import HTTPAdapter


class CachedAPI:
    def __init__(self, cache_name):
        # TODO: Setup a database for this
        self.session = CachedSession(backend='memory', cache_name=cache_name,
                                     expire_after=-1)
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))

    def get_with_cache_timeout(self, url: str,
                               timeout: ExpirationTime = -1) -> \
            Union[Response, CachedResponse]:
        """
        Make a request with a specified time to cache the response
        :param url: URL to request
        :param timeout: Time to remain cached
        :return: Response or CachedResponse
        """
        if timeout == 0:
            return self.get_bypass_cache(url)
        return self.session.request("get", url, expire_after=timeout,
                                    timeout=10)
        # with self.session.request_expire_after(timeout):
        #     return self.session.get(url)

    def get_bypass_cache(self, url: str) -> Response:
        """
        Make a request without using any cached responses
        :param url: URL to request
        :return: Response
        """
        with self.session.cache_disabled():
            return self.session.get(url, timeout=10)

    @abstractmethod
    def handle_query(self, **kwargs) -> dict:
        """
        Handles an incoming query and provides a response
        :param kwargs: keyword arguments as required by APIs
        :return: dict response data
        """
