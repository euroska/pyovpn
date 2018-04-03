import asyncio
import logging
import json
import uuid
from aiohttp.web import WebSocketResponse
from aiohttp import WSMsgType

logger = logging.getLogger(__name__)


class WebsocketClient(object):

    def __init__(self, manager, ws, user):
        self.manager = manager
        self.ws = ws
        self.token = ''
        self.user = self.manager.ANONYMOUSE

    async def __call__(self, msg):

        if msg.type == WSMsgType.TEXT:
            data = json.loads(msg.data)
            message = data.get('message', '')
            id = data.get('id', str(uuid.uuid4()))
            body = data.get('body')

            # custom messages
            if message == 'pyovpn.token':
                self.token = body
                username = await self.manager.auth.checkToken(self.token)
                if username in self.manager.config['users']:
                    self.user = self.manager.config['users'][username]

                response = {
                    'id': id,
                    'message': 'pyovpn.current',
                    'body': self.user
                }
                await self.ws.send_json(response)

            # api messages
            else:
                response = await self.manager.api(message, body, self.user)
                response['id'] = id
                await self.ws.send_json(response)

        elif msg.type == WSMsgType.ERROR:
            logger.error('ws connection closed with exception %s' % self.ws.exception())

    async def emit(self, message, body, id=None):
        if id is None:
            id = str(uuid.uuid4())

        data = {
            'message': message,
            'body': body,
            'id': id,
        }
        await self.ws.send_json(data)


class WebsocketProtocol(object):

    def __init__(self, manager):
        self.manager = manager
        self.clients = {}

    async def __call__(self, request):

        user = self.manager.ANONYMOUSE
        id = str(uuid.uuid4())
        ws = WebSocketResponse()
        await ws.prepare(request)

        client = WebsocketClient(self.manager, ws, user)
        self.clients[id] = client

        async for msg in ws:
            asyncio.ensure_future(client(msg))

        logger.info('websocket connection closed')

        if id in self.clients:
            del self.clients[id]

        return ws

