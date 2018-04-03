# -*- coding: utf-8 -*-
import os
import logging
import asyncio
import hashlib
import datetime
from aiohttp import web

from .config import Config
from .jsonrpc import JsonRPC
from .websocket import WebsocketProtocol
from .api import Api
from .vpn import VPN
from .plugins.auth import SimpleAuth

logger = logging.getLogger(__name__)


class Manager(object):
    ANONYMOUSE = {
        'username': 'Anonymouse',
        'is_admin': False,
        'is_anonymouse': True,
        'password': '',
    }

    def __init__(self, config):
        '''
        Inicialize VPN orchestrate server
        '''
        self.loop = asyncio.get_event_loop()
        self.config = config
        self.vpns = {}
        self.auth = SimpleAuth(self)
        self.api = Api(self)
        self.jsonrpc = JsonRPC(self)
        self.websock = WebsocketProtocol(self)

        self.server = None

        self.app = web.Application()
        self.app.router.add_post(
            self.config['web']['jsonrpc'],
            self.jsonrpc
        )
        self.app.router.add_get(
            self.config['web']['websock'],
            self.websock
        )

        if self.config['debug']:
            self.app.router.add_static('/', self.config['static_path'])

    async def run(self):
        if self.config['web']['listen'].find('/') == -1:
            self.config['web']['port'] = self.config['web'].get('port', 8080)
            self.server = await self.loop.create_server(
                self.app.make_handler(loop=self.loop),

                self.config['web']['listen'],
                self.config['web'].get('port', 8080)
            )
        else:
            self.server = await self.loop.create_unix_server(
                self.app.make_handler(loop=self.loop),
                self.config['web']['listen'],
            )
        self.vpns = {
            vpn: VPN(self, vpn) for vpn in self.config['vpns'].keys()
        }

        await self.server.wait_closed()

    def start(self):
        '''
        Start asyncio loop
        '''
        return self.loop.run_until_complete(self.run())

    def stop(self):
        '''
        Stop asyncio loop
        '''
        for socket in self.server.sockets:
            socket.close()

        self.webserver.close()

        for vpn in self.vpns.values():
            vpn.stop()

    def reload(self):
        '''
        Reload config
        '''
        pass

    def notify(self, message):
        pass
        #print(message, flush=True)

