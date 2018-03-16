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
        self.user = user

    async def __call__(self, msg):
        if msg.type == WSMsgType.TEXT:
            data = json.loads(msg.data)
            message = data.get('message', '')
            id = data.get('uuid', str(uuid.uuid4()))
            body = data.get('body')

            response = await self.manager.worker(message, body, self.manager.ANONYMOUSE)
            response['uuid'] = id
            await self.ws.send_json(response)

        elif msg.type == WSMsgType.ERROR:
            logger.error('ws connection closed with exception %s' % self.ws.exception())

    async def emit(self, message, body, id=None):
        if id is None:
            id = str(uuid.uuid4())

        data = {
            'message': message,
            'body': body,
            'uuid': id,
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
                asyncio.ensure_future(client.emit('test', {}))

        logger.info('websocket connection closed')

        if id in self.clients:
            del self.clients[id]

        return ws

