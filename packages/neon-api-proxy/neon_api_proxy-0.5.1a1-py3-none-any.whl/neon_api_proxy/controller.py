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

from os.path import join, isfile
from ovos_utils.log import LOG
from ovos_config.config import Configuration
from neon_utils.configuration_utils import NGIConfig
from ovos_config.locations import get_xdg_config_save_path

from neon_api_proxy.services.map_maker_api import MapMakerAPI
from neon_api_proxy.services.owm_api import OpenWeatherAPI
from neon_api_proxy.services.alpha_vantage_api import AlphaVantageAPI
from neon_api_proxy.services.wolfram_api import WolframAPI
from neon_api_proxy.services.test_api import TestAPI


class NeonAPIProxyController:
    """
    Resolves a service name to an instance to provide external API access
    """

    # Mapping between string service name and actual class
    service_class_mapping = {
        'wolfram_alpha': WolframAPI,
        'alpha_vantage': AlphaVantageAPI,
        'open_weather_map': OpenWeatherAPI,
        'map_maker': MapMakerAPI,
        'api_test_endpoint': TestAPI
    }

    def __init__(self, config: dict = None):
        """
            @param config: configurations dictionary
        """
        self.config = config or self._init_config()
        self.service_instance_mapping = self.init_service_instances(
            self.service_class_mapping)

    @staticmethod
    def _init_config() -> dict:
        from neon_api_proxy.config import get_proxy_config
        legacy_config = get_proxy_config()
        if legacy_config:
            return legacy_config.get("SERVICES") or legacy_config
        legacy_config_file = join(get_xdg_config_save_path(),
                                  "ngi_auth_vars.yml")
        if isfile(legacy_config_file):
            LOG.warning(f"Legacy configuration found at: {legacy_config_file}")
            return NGIConfig("ngi_auth_vars").get("api_services", {})
        else:
            return Configuration().get("keys", {}).get("api_services", {})

    def init_service_instances(self, service_class_mapping: dict) -> dict:
        """
        Maps service classes to their instances
        @param service_class_mapping: dictionary containing mapping between
            service string name and python class representing it

        @return dictionary containing mapping between service string name
                and instance of python class representing it
        """
        service_mapping = dict()
        for item in service_class_mapping:
            api_key = self.config.get(item, {}).get("api_key") if self.config \
                else None
            try:
                if api_key is None:
                    LOG.warning(f"No API key for {item} in {self.config}")
                service_mapping[item] = \
                    service_class_mapping[item](api_key=api_key)
            except Exception as e:
                LOG.error(e)
        return service_mapping

    def resolve_query(self, query: dict) -> dict:
        """
        Generically resolves input query dictionary by mapping its "service"
        @param query: dictionary with query parameters
        @return: response from the destination service
        """
        target_service = query.get('service')
        message_id = query.pop('message_id', None)
        if target_service and target_service in \
                list(self.service_instance_mapping):
            resp = self.service_instance_mapping[target_service].\
                handle_query(**query)
        else:
            resp = {
                "status_code": 401,
                "content": f"Unresolved service name: {target_service}",
                "encoding": "utf-8"
            }
        resp['message_id'] = message_id
        return resp
