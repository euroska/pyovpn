# -*- coding: utf-8 -*-
import os
import logging
import asyncio
import hashlib
import datetime
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
        self.tokens = {}

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
        path = ''
        while True:
            hash =  hashlib.sha256(
                (username + datetime.datetime.now().isoformat()).encode('utf-8')
            )
            path = os.path.join(self.config['data_path'], 'tokens', hash.hexdigest())
            if not os.path.exists(path):
                break

        with open(path, 'w') as f:
            f.write(username)

        return hash.hexdigest()

    async def checkToken(self, token):

        if token in self.tokens:
            return self.tokens[token]

        path = os.path.join(self.config['data_path'], 'tokens', token)
        if os.path.exists(path):
            with open(path, 'r') as f:
                return f.read()

        return False

    async def delToken(self, token):
        path = os.path.join(self.config['data_path'], 'tokens', token)

        if os.path.exists(path):
            os.unlink(path)

        if token in self.tokens:
            del self.tokens[token]

        return True

    async def clearTokens(self, delta):
        arbitrary = datetime.datetime.now() - delta
        for root, dirs, tokens in os.walk(os.path.join(
            self.config['data_path'], 'tokens'
        )):
            for token in tokens:
                path = os.path.join(root, f)
                if arbitrary > os.path.getctime(path):
                    os.unlink(path)
                    if token in self.tokens:
                        del self.tokens[token]

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

