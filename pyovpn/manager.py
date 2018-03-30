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

logger = logging.getLogger(__name__)


class Manager(object):
    ANONYMOUSE = {
        'username': 'Anonymouse',
        'is_admin': False,
        'is_anonymouse': True,
        'password': '',
    }

    def __init__(self, config):
        self.loop = asyncio.get_event_loop()
        self.config = config
        self.vpns = {}
        self.api = Api(self)
        self.jsonrpc = JsonRPC(self)
        self.websock = WebsocketProtocol(self)
        self.tokens = {}

        self.app = web.Application()
        jsonrpc = self.config._data.get('web', {}).get('jsonrpc', '/api/jsonrpc')
        self.app.router.add_post(jsonrpc, self.jsonrpc)

        websock = jsonrpc = self.config._data.get('web', {}).get('websock', '/api/ws')
        self.app.router.add_get(websock, self.websock)

        if self.config['debug']:
            self.app.router.add_get(
                '/',
                lambda request: web.FileResponse(
                    os.path.join(self.config['static_path'], 'index.html')
                )
            )
            self.app.router.add_static('/*', self.config['static_path'])

    def hashPassword(self, password):
        return hashlib.sha256(password.encode('utf8')).hexdigest()

    def checkPassword(self, username, password):
        user = self.config['users'][username]
        return self.hashPassword(password) == user['password']

    async def login(self, username, password):
        if username in self.config['users']:
            return self.checkPassword(username, password)
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

        token = hash.hexdigest()
        self.tokens[token] = username
        return token

    async def checkToken(self, token):

        if token in self.tokens:
            return self.tokens[token]

        path = os.path.join(self.config['data_path'], 'tokens', token)
        if os.path.exists(path):
            with open(path, 'r') as f:
                username = f.read()
                self.tokens[token] = username
                return username

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
            '0.0.0.0',
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

    def notify(self, message):
        print(message, flush=True)

