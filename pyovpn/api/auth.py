import asyncio
from .decorators import isAdmin, isAutorized, api


class AuthApi(object):
    @api(
        'pyovpn.login',
        schema_in={
            'title': 'Login message',
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'password': {'type': 'string'},
            },
        },
        schema_out={
            'title': 'Login response',
            'type': 'object',
            'properties': {
                'logged': {'type': 'boolean'},
                'token': {'type': 'string'},
                'is_admin': {'type': 'boolean'},
                'is_anonymouse': {'type': 'boolean'},
            }
        }
    )
    async def login(self, body, user):
        '''
        Login method
        '''
        username = body['username']
        password = body['password']

        # TODO: password hashesh
        logged = await self.manager.login(username, password)
        if logged:
            return {
                'logged': True,
                'token': await self.manager.getToken(username),
                'username': username,
                'is_admin': self.manager.config['users'][username].get('is_admin', False),
                'is_anonymouse': self.manager.config['users'][username].get('is_anonymouse', False),
            }

        # sleep for bad request
        # check, if there is right place
        await asyncio.sleep(3)

        return {
            "logged": False,
        }

    @api('pyovpn.logout')
    async def logout(self, body, user):
        return await self.manager.delToken(body)

    @api('pyovpn.current')
    async def token(self, body, user):
        return user

    @isAutorized
    @api('pyovpn.token.list')
    async def tokens(self, body, user):
        return [key for key, value in self.manager.tokens.items() if value == user['username']]
