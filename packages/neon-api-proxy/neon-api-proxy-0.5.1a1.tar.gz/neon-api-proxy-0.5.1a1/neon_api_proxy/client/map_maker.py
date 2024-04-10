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

from ovos_utils.log import LOG
from neon_api_proxy.client import NeonAPI, request_api


def get_coordinates(location: str) -> (float, float):
    """
    Get coordinates for the requested location
    @param location: Search term, i.e. City, Address, Landmark
    @returns: coordinate latitude, longitude
    """
    resp = _make_api_call({'address': location})
    if resp['status_code'] != 200:
        raise RuntimeError(f"API Request failed: {resp['content']}")
    coords = resp['content'][0]['lat'], resp['content'][0]['lon']
    LOG.info(f"Resolved: {coords}")
    return float(coords[0]), float(coords[1])


def get_address(lat: float, lon: float) -> dict:
    """
    Get a dict location for the specified coordinates
    @param lat: latitude of point to look up
    @param lon: longitude of point to look up
    @returns: dict location (equivalent to Geopy Location.raw)
    """
    resp = _make_api_call({'lat': lat, "lon": lon})
    if resp['status_code'] != 200:
        raise RuntimeError(f"API Request failed: {resp['content']}")
    address = resp['content']['address']
    if not address.get('city'):
        LOG.debug(f"Response missing city, trying to find alternate tag in: "
                  f"{address.keys()}")
        address['city'] = address.get('town') or address.get('village')
    LOG.info(f"Resolved: {address}")
    return address


def _make_api_call(request_data: dict) -> dict:
    resp = request_api(NeonAPI.MAP_MAKER, request_data)
    if resp['status_code'] == 200:
        resp['content'] = json.loads(resp['content'])
    return resp
