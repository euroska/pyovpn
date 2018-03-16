from aiohttp.web import json_response


class JsonRPC(object):

    def __init__(self, manager):
        self.manager = manager

    async def __call__(self, request):
        data = await request.json()

        message = data.get('message', '')
        body = data.get('body')

        return json_response(
            await self.manager.worker(message, body, self.manager.ANONYMOUSE)
        )
