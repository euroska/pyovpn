# -*- coding: utf-8 -*-
import asyncio
from aiohttp.web import Application

from .config import Config
from .jsonrpc import JsonRPC
from .websock import WebSock
from .message import Message

class Manager(object):

    def __init__(self, config_path):
        self.loop = asyncio.get_event_loop()
        self.config = Config.load(config_path)
        self.vpns = []
        self.message = Message(self)
        self.jsonrpc = JsonRPC(self)
        self.websock = WebSock(self)

        self.app = Application()
        jsonrpc = self.config._data.get('web', {}).get('jsonrpc', '/api/jsonrpc')
        self.app.router.add_get(jsonrpc, self.jsonrpc)

        websock = jsonrpc = self.config._data.get('web', {}).get('websock', '/api/ws')
        self.app.router.add_get(websock, self.websock)

    def start(self):

        return self.loop.run_until_complete(self.run())

    def stop(self):
        for socket in self.webserver.sockets:
            socket.close()

        self.webserver.close()

        for vpn in self.vpns:
            vpn.stop()


    async def run(self):
        self.webserver = await self.loop.create_server(
            self.app.make_handler(loop=self.loop),
            '127.0.0.1',
            8080
        )

        await self.webserver.wait_closed()






