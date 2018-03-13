from aiohttp.web import WebSocketResponse
from aiohttp import WSMsgType

class WebSock(object):

    def __init__(self, manager):
        self.manager = manager

    async def __call__(self, request):
        ws = WebSocketResponse()

        await ws.prepare(request)

        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    await ws.send_str(msg.data + '/answer')

            elif msg.type == WSMsgType.ERROR:
                print('ws connection closed with exception %s' %
                    ws.exception())

        print('websocket connection closed')

        return ws
