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

        self.token = await self.manager.checkToken('0a466aeb962b0ddabbe1780c67d8b3dad6fb3766330890d6d4f3fdbc6fb89ccf')
        self.user = self.manager.config['users'][self.token]

        print(self.user)
        if msg.type == WSMsgType.TEXT:
            data = json.loads(msg.data)
            message = data.get('message', '')
            id = data.get('id', str(uuid.uuid4()))
            body = data.get('body')

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

