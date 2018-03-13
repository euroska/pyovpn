from functools import wraps

class Message(object):

    async def __call__(self, type, data, user=None):
        if type == 'pyovpn.vpn.list':
            if user.is_admin:
                return self.vpnList(data)

            elif user is not None:
                return

    def vpnList(self, data, user=None):
        pass

