import asyncio


class Worker(object):

    ERROR_CODE_PERMISSION_DENIED = 1001
    ERROR_CODE_NOT_IMPLEMENTED = 1002
    ERROR_CODE_UNKNOWN = 1003


    def __init__(self, manager):
        '''
        '''
        self.UNAUTHORIZED = self.error(
            code=self.ERROR_CODE_PERMISSION_DENIED,
            title='UnAuthorized',
            description='You must by authorized to call operation'
        )
        self.manager = manager
        self.messages = {
            'pyovpn.login': self.login,
            'pyovpn.vpn.list': self.vpnList,
        }

    async def __call__(self, message, body, user):
        '''
        Router method
        '''
        if message in self.messages:
            return await self.messages[message](body, user)

        return

    def ok(self, uuid):
        return {
            'message': 'pyovpn.ok',
            'body': None,
            'uuid': uuid,
        }

    def error(self, code=ERROR_CODE_UNKNOWN, title='Unknown', description='Unknown'):
        return {
            'message': 'pyovpn.error',
            'body': {
                'code': code,
                'title': title,
                'description': description,
            }
        }

    async def login(self, body, user):
        '''
        Login method
        '''
        username = body.get('username')
        password = body.get('password')

        # TODO: password hashesh
        logged = await self.manager.login(username, password)
        if logged:
            return {
                'message': 'pyovpn.login',
                'body': {
                    'logged': True,
                    'token': 123,
                    'username': username,
                }
            }

        # sleep for bad request
        # check, if there is right place
        await asyncio.sleep(3)

        return {
            'message': 'pyovpn.login',
            'body': {
                "logged": False,
            }
        }

    async def vpnList(self, body, user):
        if user['is_anonymouse']:
            return self.UNAUTHORIZED

        if not user['is_admin']:
            body['user'] = user['username']

        vpns = []
        u = body.get('user', False)
        if u:
            vpns = list(
                filter(
                    lambda v: v.hasUser(u),
                    self.manager.vpns.values()
                )
            )

        else:
            vpns = [vpn.serialize() for vpn in self.manager.vpns]

        return {
            'message': 'pyovpn.vpn.list',
            'body': vpns,
        }

