import asyncio

def isAdmin(fn):
    pass

def isAutorized(fn):
    pass


class Worker(object):

    ERROR_CODE_PERMISSION_DENIED = 1001
    ERROR_CODE_NOT_IMPLEMENTED = 1002
    ERROR_CODE_UNKNOWN = 1003

    ERROR_CODE_INSUFFICIENT_PERMISSION = 1004


    def __init__(self, manager):
        '''
        '''
        self.UNAUTHORIZED = self.error(
            code=self.ERROR_CODE_PERMISSION_DENIED,
            title='UnAuthorized',
            description='You must by authorized to call operation'
        )
        self.REQUIRED_ADMIN = self.error(
            code=self.ERROR_CODE_INSUFFICIENT_PERMISSION,
            title='Insufficient permission',
            description='Insufficient permission',
        )

        self.manager = manager
        self.messages = {
            # authorization
            'pyovpn.login': self.login,
            'pyovpn.logout': self.logout,

            # template messages
            'pyovpn.template.client.list': self.templateClientList,
            'pyovpn.template.client.set': self.templateClientSet,
            'pyovpn.template.client.del': self.templateClientDel,

            'pyovpn.template.server.list': self.templateServerList,
            'pyovpn.template.server.set': self.templateServerSet,
            'pyovpn.template.server.del': self.templateServerDel,

            # VPN messages
            'pyovpn.vpn.list': self.vpnList,
            'pyovpn.vpn.create': self.vpnCreate,
            'pyovpn.vpn.delete': self.vpnDelete,
            'pyovpn.vpn.detail': self.vpnDetail,

            'pyovpn.vpn.user.add': self.vpnUserAdd,
            'pyovpn.vpn.user.del': self.vpnUserDel,
            'pyovpn.vpn.user.revoke': self.vpnUserRevoke,
            'pyovpn.vpn.user.renew': self.vpnUserRenew,

            'pyovpn.vpn.usertemplate.get': self.vpnUserTemplateGet,
            'pyovpn.vpn.usertemplate.set': self.vpnUserTemplateSet,

            'pyovpn.vpn.servertemplate.get': self.vpnServerTemplateGet,
            'pyovpn.vpn.servertemplate.set': self.vpnServerTemplateSet,

            'pyovpn.vpn.config.get': self.vpnConfigGet,

            # User messages
            'pyovpn.user.list': self.userList,
            'pyovpn.user.create': self.userCreate,
            'pyovpn.user.delete': self.userDelete,
            'pyovpn.user.detail': self.userDetail,
        }

    async def __call__(self, message, body, user):
        '''
        Router method
        '''
        if message in self.messages:
            return await self.messages[message](body, user)

        return {}

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
                    'token': await self.manager.getToken(username),
                    'username': username,
                    'is_admin': self.manager.config['users'][username].get('is_admin', False),
                    'is_anonymouse': self.manager.config['users'][username].get('is_anonymouse', False),
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

    async def logout(self, body, user):
        return {
            'message': 'pyovpn.logout',
            'body': await self.manager.delToken(body)
        }

    async def templateServerList(self, body, user):
        pass

    async def templateServerSet(self, body, user):
        pass

    async def templateServerDel(self, body, user):
        pass

    async def templateClientList(self, body, user):
        pass

    async def templateClientSet(self, body, user):
        pass

    async def templateClientDel(self, body, user):
        pass

    async def vpnList(self, body, user):
        if user['is_anonymouse']:
            return self.UNAUTHORIZED

        if not user['is_admin']:
            body['user'] = user['username']

        vpns = []
        u = body.get('user', False)
        if u:
            vpns = [vpn.serialize() for vpn in self.manager.vpns if vpn.hasUser(u)]

        else:
            vpns = [vpn.serialize() for vpn in self.manager.vpns]

        return {
            'message': 'pyovpn.vpn.list',
            'body': vpns,
        }

    async def vpnCreate(self, body, user):
        pass

    async def vpnDelete(self, body, user):
        pass

    async def vpnDetail(self, body, user):
        pass

    async def vpnUpdate(self, body, user):
        pass

    async def vpnUserAdd(self, body, user):
        pass

    async def vpnUserDel(self, body, user):
        pass

    async def vpnUserRevoke(self, body, user):
        pass

    async def vpnUserRenew(self, body, user):
        pass

    async def vpnServerTemplateSet(self, body, user):
        pass

    async def vpnServerTemplateGet(self, body, user):
        pass

    async def vpnUserTemplateSet(self, body, user):
        pass

    async def vpnUserTemplateGet(self, body, user):
        pass

    async def vpnConfigGet(self, body, user):
        pass

    async def userList(self, body, user):
        if not user['is_admin']:
            return self.REQUIRED_ADMIN

        users = []
        for username, attr in self.manager.config['users'].keys():
            user = {
                'name': username,
                'is_admin': attr.get('is_admin', False),
                'is_anonymouse': attr.get('is_anonymouse', False),
                'vpns': [vpn.name for vpn in self.vpns if vpn.hasUser(username)],
            }
        return users

    async def userCreate(self, body, user):
        if not user['is_admin']:
            return self.REQUIRED_ADMIN

    async def userDelete(self, body, user):
        pass

    async def userDetail(self, body, user):
        pass

    async def userUpdate(self, body, user):
        pass

    async def userPassword(self, body, user):
        pass
