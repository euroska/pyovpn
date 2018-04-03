import logging
from aiohttp.web import json_response


logger = logging.getLogger(__name__)


class JsonRPC(object):

    def __init__(self, manager):
        self.manager = manager

    async def __call__(self, request):
        user = self.manager.ANONYMOUSE
        data = await request.json()

        message = data.get('message', '')
        body = data.get('body')
        token = request.headers.get('X-Token', '_')
        username = await self.manager.auth.checkToken(
            token
        )

        if username in self.manager.config['users']:
            user = self.manager.config['users'][username]

        return json_response(
            await self.manager.api(message, body, user)
        )
