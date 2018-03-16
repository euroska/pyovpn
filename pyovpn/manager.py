# -*- coding: utf-8 -*-
import logging
import asyncio
from aiohttp.web import Application

from .config import Config
from .jsonrpc import JsonRPC
from .websocket import WebsocketProtocol
from .worker import Worker
from .vpn import VPN

logger = logging.getLogger(__name__)


class Manager(object):
    ANONYMOUSE = {
        'is_admin': True,
        'is_anonymouse': False,
        'password': '',
    }

    def __init__(self, config):
        self.loop = asyncio.get_event_loop()
        self.config = config
        self.vpns = {}
        self.worker = Worker(self)
        self.jsonrpc = JsonRPC(self)
        self.websock = WebsocketProtocol(self)

        self.app = Application()
        jsonrpc = self.config._data.get('web', {}).get('jsonrpc', '/api/jsonrpc')
        self.app.router.add_post(jsonrpc, self.jsonrpc)

        websock = jsonrpc = self.config._data.get('web', {}).get('websock', '/api/ws')
        self.app.router.add_get(websock, self.websock)

    async def login(self, username, password):
        if username in self.config['users']:
            data = self.config['users'][username]
            if password == data.get('password'):
                return True
        return False

    async def getToken(self, username):
        return '123'

    async def checkToken(self, token):
        return False

    async def delToken(self, token):
        return True

    async def clearTokens(self):
        return True

    async def run(self):
        self.webserver = await self.loop.create_server(
            self.app.make_handler(loop=self.loop),
            '127.0.0.1',
            8080
        )
        self.vpns = {
            vpn: VPN(self, vpn) for vpn in self.config['vpns'].keys()
        }

        await self.webserver.wait_closed()

    def start(self):
        '''
        Start asyncio loop
        '''
        return self.loop.run_until_complete(self.run())

    def stop(self):
        '''
        Stop asyncio loop
        '''
        for socket in self.webserver.sockets:
            socket.close()

        self.webserver.close()

        for vpn in self.vpns.values():
            vpn.stop()

