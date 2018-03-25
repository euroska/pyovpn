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
            body['user'] = user['username']

        vpns = []
        u = body.get('user', False)
        if u:
            vpns = [vpn.serializeList() for vpn in self.manager.vpns.values() if vpn.hasUser(u)]

        else:
            vpns = [vpn.serializeList() for vpn in self.manager.vpns.values()]

        return vpns

    @isAdmin
    @api(
        'pyovpn.vpn.add',
        message_out='pyovpn.vpn.detail'
    )
    async def vpnAdd(self, body, user):
        name = body['name']
        if name in self.manager.config['vpns']:
            raise VpnExists()

        vpn = VPN.inicialize(
            self.manager,
            name,
            subject=body['subject']
        )
        return vpn.serializeDetail()

    @isAdmin
    @api('pyovpn.vpn.del')
    async def vpnDel(self, body, user):
        pass

    @isAutorized
    @api('pyovpn.vpn.detail')
    async def vpnDetail(self, body, user):
        pass

    @isAdmin
    @api('pyovpn.vpn.set')
    async def vpnSet(self, body, user):
        pass

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

    @api('pyovpn.vpn.config')
    async def vpnConfigGet(self, body, user):
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        return {
            'name': vpn.name,
            'config': vpn.configGet(),
        }

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
    @api('pyovpn.vpn.start')
    async def vpnStart(self, body, user):
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        vpn.start()
        return vpn.serializeDetail()

    @isAdmin
    @api('pyovpn.vpn.stop')
    async def vpnStop(self, body, user):
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        vpn.stop()
        return vpn.serializeDetail()

    @isAdmin
    @api('pyovpn.vpn.kill')
    async def vpnKill(self, body, user):
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        vpn.kill()
        return vpn.serializeDetail()

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
    @api('pyovpn.vpn.user.add', message_out='pyovpn.vpn.detail')
    async def vpnUserAdd(self, body, user):
        # TODO user is not admin
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        vpn.cnAdd(body['username'])
        return vpn.serializeDetail()

    @isAutorized
    @api('pyovpn.vpn.user.revoke')
    async def vpnUserRevoke(self, body, user):
        # TODO user is not admin
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        vpn.cnRevoke(body['username'])
        return vpn.serializeDetail()

    @isAutorized
    @api('pyovpn.vpn.user.renew')
    async def vpnUserRenew(self, body, user):
        # TODO user is not admin
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        vpn.cnRenew(body['username'])
        return vpn.serializeDetail()

    @api('pyovpn.vpn.user.template')
    async def vpnUserTemplateGet(self, body, user):
        if body['name'] not in self.manager.vpns:
            raise VpnDoesNotExist()

        vpn = self.manager.vpns[body['name']]
        return {
            'name': body['name'],
            'template': vpn.userTemplateGet(),
        }

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
