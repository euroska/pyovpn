from aiohttp.web import json_response


class JsonRPC(object):

    def __init__(self, manager):
        self.manager = manager

    async def __call__(self, request):
        user = self.manager.ANONYMOUSE
        data = await request.json()

        message = data.get('message', '')
        body = data.get('body')

        username = await self.manager.checkToken(
            request.headers.get('X-Token', '_')
        )
        if username in self.manager.config['users']:
            user = self.manager.config['users'][username]

        return json_response(
            await self.manager.api(message, body, user)
        )
