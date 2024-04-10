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

import pika.channel

from typing import Optional
from ovos_utils.log import LOG
from neon_mq_connector.utils.network_utils import b64_to_dict, dict_to_b64
from neon_mq_connector.connector import MQConnector

from neon_api_proxy.controller import NeonAPIProxyController


class NeonAPIMQConnector(MQConnector):
    """Adapter for establishing connection between Neon API and MQ broker"""

    def __init__(self, config: Optional[dict], service_name: str,
                 proxy: NeonAPIProxyController):
        """
            Additionally accepts message bus connection properties

            :param config: dictionary containing MQ configuration data
            :param service_name: name of the service instance
        """
        super().__init__(config, service_name)

        self.vhost = '/neon_api'
        self.proxy = proxy

    def handle_api_input(self,
                         channel: pika.channel.Channel,
                         method: pika.spec.Basic.Deliver,
                         _: pika.spec.BasicProperties,
                         body: bytes):
        """
            Handles input requests from MQ to Neon API

            :param channel: MQ channel object (pika.channel.Channel)
            :param method: MQ return method (pika.spec.Basic.Deliver)
            :param _: MQ properties (pika.spec.BasicProperties)
            :param body: request body (bytes)
        """
        message_id = None
        try:
            if body and isinstance(body, bytes):
                request = b64_to_dict(body)
                tokens = self.extract_agent_tokens(request)

                message_id = tokens.pop('message_id', request.get("message_id",
                                                                  None))
                LOG.info(f"request={request}")

                respond = self.proxy.resolve_query(request)
                LOG.debug(f"response message={message_id} "
                          f"status={respond.get('status_code')}")

                try:
                    respond['content'] = bytes(respond.get('content', b'')).\
                        decode(encoding='utf-8')
                except Exception as e:
                    LOG.error(e)
                respond = {**respond, **tokens}
                LOG.debug(f"respond={respond}")
                data = dict_to_b64(respond)

                routing_key = request.get('routing_key', 'neon_api_output')
                # queue declare is idempotent, just making sure queue exists
                channel.queue_declare(queue=routing_key)
                channel.basic_publish(
                    exchange='',
                    routing_key=routing_key,
                    body=data,
                    properties=pika.BasicProperties(expiration='1000')
                )
                channel.basic_ack(method.delivery_tag)
            else:
                raise TypeError(f'Invalid body received, expected bytes string;'
                                f' got: {type(body)}')
        except Exception as e:
            LOG.error(f"message_id={message_id}")
            LOG.error(e)

    @staticmethod
    def extract_agent_tokens(msg_data: dict) -> dict:
        """
            Extracts tokens from msg data based on received "agent"

            :param msg_data: desired message data
            :return: dictionary containing tokens dedicated to resolved agent
        """
        tokens = dict()
        request_agent = msg_data.pop('agent', 'undefined')
        if 'klatchat' in request_agent:
            LOG.info('Resolved agent is "klatchat"')
            tokens['cid'] = msg_data.pop("cid", None)
            tokens['message_id'] = tokens['replied_message'] = \
                msg_data.get('messageID', None)
        else:
            LOG.debug('No valid agent specified in the message data')
        return tokens

    def handle_error(self, thread, exception):
        LOG.error(f"{exception} occurred in {thread}")
        LOG.info(f"Restarting Consumers")
        self.stop()
        self.run()

    def pre_run(self, **kwargs):
        self.register_consumer("neon_api_consumer", self.vhost,
                               'neon_api_input', self.handle_api_input,
                               auto_ack=False)
        self.register_consumer("neon_api_consumer_targeted",
                               self.vhost,
                               f'neon_api_input_{self.service_id}',
                               self.handle_api_input, auto_ack=False)
