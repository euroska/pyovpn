import os
import shutil
from .decorators import isAdmin, isAutorized, api
from .errors import ApiError
from ..vpn import VPN


class VpnDoesNotExist(ApiError):

    def __init__(self):
        super(VpnDoesNotExist, self).__init__(
            code='pyovpn.error.vpn_does_not_exist',
            description='Vpn matching query does not exist',
        )


class VpnExists(ApiError):

    def __init__(self):
        super(VpnExists, self).__init__(
            code='pyovpn.error.vpn_exists',
            description='Vpn already exists',
        )


class VpnApi(object):
    @isAutorized
    @api('pyovpn.vpn.list')
    async def vpnList(self, body, user):
        if not user['is_admin']:
            body['username'] = user['username']

        vpns = []
        user = body.get('username', False)
        if user:
            vpns = [vpn.serializeUser(user) for vpn in self.manager.vpns.values() if vpn.hasUser(user)]

        else:
            vpns = [vpn.serializeAdmin() for vpn in self.manager.vpns.values()]

        return vpns

    @isAdmin
    @api('pyovpn.vpn.del')
    async def vpnDel(self, body, user):
        if body in self.manager.vpns:
            vpn = self.manager.vpns[body]
            vpn.kill()
            del self.manager.vpns[body]

        if body in self.manager.config['vpns']:
            del self.manager.config['vpns'][body]

        self.manager.config.save()

        path = os.path.join(
            self.manager.config['data_path'],
            'vpns',
            body
        )

        if os.path.exists(path):
            shutil.rmtree(path)

        return body

    @isAutorized
    @api('pyovpn.vpn.detail')
    async def vpnDetail(self, body, user):
        if body in self.manager.vpns:
            vpn = self.manager.vpns[body]
            if user['is_admin']:
                return vpn.serializeAdmin()

        return vpn.serializeUser(user['username'])

    @isAdmin
    @api(
        'pyovpn.vpn.set',
        schema_in={
            'title': 'Vpn set message',
            'type': 'object',
            'required': ['name'],
            'properties': {
                'name': {'type': 'string'},
                'autostart': {'type': 'boolean'},
                'subject': {
                    'type': 'object',
                    'properties': {
                        'cn': {'type': 'string'},
                        'o': {'type': 'string'},
                        'ou': {'type': 'string'},
                    },
                }
            }
        },
        message_out='pyovpn.vpn.detail'
    )
    async def vpnSet(self, body, user):
        vpn = None
        if body['name'] in self.manager.vpns:
            vpn = self.manager.vpns[body['name']]
            vpn.autostart = body['autostart']
            vpn.description = body['description']
            vpn.save()
        else:
            name = body['name']
            vpn = VPN.inicialize(
                self.manager,
                name,
                autostart=body.get('autostart', False),
                subject=body.get('subject', {})
            )

        if body.get('autostart', False) and not vpn.running:
            vpn.start()

        return vpn.serializeAdmin()

    @isAdmin
    @api('pyovpn.vpn.template')
    async def vpnServerTemplateGet(self, body, user):
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        return {
            'name': body['name'],
            'template': vpn.serverTemplateGet()
        }

    @isAdmin
    @api(
        'pyovpn.vpn.template.set',
        message_out='pyovpn.vpn.template'
    )
    async def vpnTemplateSet(self, body, user):
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        vpn.serverTemplateSet(
            body['template'],
            regenerate=body.get('regenerate', False)
        )

        return {
            'name': body['name'],
            'template': vpn.serverTemplateGet()
        }

    @isAdmin
    @api('pyovpn.vpn.config')
    async def vpnConfigGet(self, body, user):
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        return {
            'name': vpn.name,
            'config': vpn.configGet(),
        }

    @isAdmin
    @api('pyovpn.vpn.config.set', {})
    async def vpnConfigSet(self, body, user):
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        vpn.configSet(config=body.get('config'))
        return {
            'name': vpn.name,
            'config': vpn.configGet(),
        }

    @isAdmin
    @api(
        'pyovpn.vpn.start',
        message_out='pyovpn.vpn.detail'
    )
    async def vpnStart(self, body, user):
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        vpn.start()

        return vpn.serializeAdmin()

    @isAdmin
    @api(
        'pyovpn.vpn.reload',
        message_out='pyovpn.vpn.detail'
    )
    async def vpnReload(self, body, user):
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        vpn.reload()

        return vpn.serializeAdmin()

    @isAdmin
    @api(
        'pyovpn.vpn.stop',
        message_out='pyovpn.vpn.detail'
    )
    async def vpnStop(self, body, user):
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        vpn.stop()
        return vpn.serializeAdmin()

    @isAdmin
    @api(
        'pyovpn.vpn.kill',
        message_out='pyovpn.vpn.detail'
    )
    async def vpnKill(self, body, user):
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        vpn.kill()
        return vpn.serializeAdmin()

    @isAdmin
    @api('pyovpn.vpn.log')
    async def vpnLog(self, body, user):
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()
        vpn = self.manager.vpns[body['name']]
        return {
            'name': vpn.name,
            'log': vpn.log
        }

    @isAdmin
    @api(
        'pyovpn.vpn.user.add',
        message_out='pyovpn.vpn.detail'
    )
    async def vpnUserAdd(self, body, user):
        # TODO user is not admin
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        vpn.cnAdd(body['username'])
        return vpn.serializeAdmin()

    @isAutorized
    @api(
        'pyovpn.vpn.user.revoke',
        message_out='pyovpn.vpn.detail'
    )
    async def vpnUserRevoke(self, body, user):
        # TODO user is not admin
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        vpn.cnRevoke(body['username'])

        if user['is_admin']:
            return vpn.serializeAdmin()
        return vpn.serializeUser(user['username'])

    @isAutorized
    @api(
        'pyovpn.vpn.user.renew',
        message_out='pyovpn.vpn.detail'
    )
    async def vpnUserRenew(self, body, user):
        # TODO user is not admin
        if not user['is_admin']:
            body['username'] = user['username']

        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        vpn.cnRenew(body['username'])

        if user['is_admin']:
            return vpn.serializeAdmin()
        return vpn.serializeUser(user['username'])

    @isAdmin
    @api('pyovpn.vpn.user.template')
    async def vpnUserTemplateGet(self, body, user):
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        return {
            'name': body['name'],
            'template': vpn.userTemplateGet(),
        }

    @isAdmin
    @api(
        'pyovpn.vpn.user.template.set',
        message_out='pyovpn.vpn.user.template'
    )
    async def vpnUserTemplateSet(self, body, user):
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        vpn.userTemplateSet(body['template'])
        return {
            'name': body['name'],
            'template': vpn.userTemplateGet(),
        }

    @isAutorized
    @api(
        'pyovpn.vpn.user.config'
    )
    async def vpnUserConfig(self, body, user):
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        if not vpn.hasUser(body['username']):
            raise VpnDoesNotExist()

        return {
            'name': body['name'],
            'config': vpn.userConfig(body['username']),
        }
