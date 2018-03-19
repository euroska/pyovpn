from aiohttp.web import json_response


class JsonRPC(object):

    def __init__(self, manager):
        self.manager = manager

    async def __call__(self, request):
        user = self.manager.ANONYMOUSE
        data = await request.json()

        message = data.get('message', '')
        body = data.get('body')

        token = await self.manager.checkToken(
            request.headers.get('X-Token', '_')
        )

        if token in self.manager.config['users']:
            user = self.manager.config['users'][token]

        return json_response(
            await self.manager.worker(message, body, user)
        )
