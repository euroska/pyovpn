from .decorators import isAdmin, isAutorized, api
from .errors import ApiError


class UserDoesNotExist(ApiError):

    def __init__(self):
        super(UserDoesNotExist, self).__init__(
            code='pyovpn.error.user_does_not_exist',
            description='User matching query does not exist',
        )


class UserExists(ApiError):

    def __init__(self):
        super(UserExists, self).__init__(
            code='pyovpn.error.user_exists',
            description='User already exists',
        )


SCHEMA_USER_DETAIL = {
    'title': 'User detail message',
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
        'is_admin': {'type': 'boolean'},
        'is_anonymouse': {'type': 'boolean'},
        'vpns': {
            'type': 'array',
            'items': {'type': 'string'},
        }
    }
}


class UserApi(object):
    @isAutorized
    @api(
        'pyovpn.user.list',
        schema_out={
            'title': 'List of users',
            'type': 'array',
            'items': SCHEMA_USER_DETAIL
        }
    )
    async def userList(self, body, user):

        userlist = self.manager.config['users'].items()

        if not user['is_admin']:
            userlist = {user['username']: user}.items()

        users = [
            {
                'username': username,
                'is_admin': attr.get('is_admin', False),
                'is_anonymouse': attr.get('is_anonymouse', False),
                'vpns': [vpn.name for vpn in self.manager.vpns.values() if vpn.hasUser(username)],
            } for username, attr in userlist
        ]
        return users

    @isAdmin
    @api(
        'pyovpn.user.add',
        message_out='pyovpn.user.detail',
        schema_in={
            'title': 'Add user message',
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'is_admin': {'type': 'boolean'},
                'is_anonymouse': {'type': 'boolean'},
                'password': {'type': 'string'},
            }
        },
        schema_out=SCHEMA_USER_DETAIL,
    )
    async def userAdd(self, body, user):
        if body['username'] in self.manager.config['users']:
            raise UserExists()

        username = body['username']
        new_user = {
            'username': username,
            'password': self.manager.auth.hashPassword(body['password']),
            'is_admin': body.get('is_admin', False),
            'is_anonymouse': body.get('is_anonymouse', False),
        }

        self.manager.config['users'][username] = new_user
        self.manager.config.save()
        return body

    @isAdmin
    @api('pyovpn.user.del')
    async def userDelete(self, body, user):
        if body not in self.manager.config['users']:
            raise UserDoesNotExist()

        del self.manager.config['users'][body]

        for vpn in self.manager.vpns.values():
            if vpn.hasUser(body):
                vpn.cnRevoke(body)

        self.manager.config.save()
        return body

    @isAutorized
    @api(
        'pyovpn.user.detail',
        schema_out=SCHEMA_USER_DETAIL,
    )
    async def userDetail(self, body, user):
        username = user['username']

        if user['is_admin'] and body:
            username = body

        if username not in self.manager.config['users']:
            raise UserDoesNotExist()

        user = self.manager.config['users'][username]
        return {
            'username': user['username'],
            'is_admin': user['is_admin'],
            'is_anonymouse': user['is_anonymouse'],
            'vpns': [vpn.name for vpn in self.manager.vpns.values() if vpn.hasUser(username)]
        }

    @isAdmin
    @api(
        'pyovpn.user.set',
        message_out='pyovpn.user.detail',
        schema_out=SCHEMA_USER_DETAIL,
    )
    async def userSet(self, body, user):
        username = body['username']
        if username not in self.manager.config['users']:
            raise UserDoesNotExist()

        user = self.manager.config['users'][username]
        user['is_admin'] = body['is_admin']
        user['is_anonymouse'] = body['is_anonymouse']
        self.manager.config.save()
        return {
            'username': user['username'],
            'is_admin': user['is_admin'],
            'is_anonymouse': user['is_anonymouse'],
            'vpns': [vpn.name for vpn in self.manager.vpns.values() if vpn.hasUser(username)]
        }

    @isAutorized
    @api('pyovpn.user.password', message_out='pyovpn.ok')
    async def userPassword(self, body, user):
        username = user['username']

        if user['is_admin'] and 'username' in body:
            username = body['username']

        user = self.manager.config['users'][username]
        user['password'] = self.manager.auth.hashPassword(body['password'])
        self.manager.config.save()
