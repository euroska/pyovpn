import os
import asyncio
from .ca import CA


class VPN(object):
    '''
    '''

    def __init__(self, manager, name):
        '''
        '''
        self.manager = manager
        self.name = name
        self.config = VPN.createConfig(manager, name)

        self.enable = self.manager.config['vpns'][name]
        self.ca = CA(self.config)

        self.users = self.manager.config['vpns'][name]['users']
        self.certs = self.loadCerts()
        self.csrs = self.loadCsrs()
        self.output = []
        self.ips = self.parseIp()
        self.names = self.parseNames()
        self.active = {}
        self.process = None
        self.loop = None

    @staticmethod
    def createConfig(manager, name):
        '''
        Create configuration for VPN based on global config and VPN name
        '''
        path = manager.config['data_path']

        return {
            'ca_key_password': None,

            'ca_cert_path': os.path.join(path, name, 'ca.pem'),
            'ca_key_path': os.path.join(path, name, 'ca.key'),
            'dh_path': os.path.join(path, name, 'dh.pem'),
            'crl_path': os.path.join(path, name, 'crl.pem'),
            'server_cert_path': os.path.join(path, name, 'server.pem'),
            'server_key_path': os.path.join(path, name, 'server.key'),
            'sequence_path': os.path.join(path, name, 'sequence'),
        }

    @staticmethod
    def inicialize(manager, name, names={}):
        '''
        Create OpenVPN runtime environment
        '''
        config = VPN.createConfig(manager, name)
        names['cn'] = 'ca'
        path = '%s/%s' % (manager.config['data_path'], name)
        if not os.path.exists(path):
            os.makedirs(path)

        ca = CA.create(confif=config, names=names)

        server_csr, server_key = ca.genCsr(names={'cn': 'server'})
        server_cert = ca.sign(server_csr, server=True)

    def loadCerts(self):
        {}

    def loadCsrs(self):
        {}

    def parseIp(self):
        '''
        '''
        return {}

    def parseNames(self):
        return {}

    def hasUser(self, username):
        return username in self.users

    def userAdd(self, username):
        if username not in self.users:
            self.users.append(username)

    def userDel(self, username):
        pass

    def userRevoke(self, username):
        pass

    def userRenew(self, username):
        pass

    def serverTemplateGet(self):
        pass

    def serverTemplateSet(self):
        pass

    def userTemplateGet(self):
        pass

    def configGet(self):
        pass

    def serializeList(self):
        return {
            'name': self.name,
            'enable': self.enable,
            'users': {
                user: {
                    'ip': self.ips.get(user),
                    'active': self.active.get(user, False)
                } for user in self.users
            }
        }

    def serializeDetail(self):
        return {
            'name': self.name,
            'enable': self.enable,
            'names': self.names,
            'users': {
                user: {
                    'ip': self.ips.get('user'),
                    'active': self.active.get(user, False)
                } for user in self.users
            }
        }

    def start(self):
        self.await = self.run()

    def reload(self):
        if self.process is None:
            return False

        self.process.send_signal(1)
        return True

    def kill(self):
        if self.process is None:
            return False

        self.process.kill()
        return True

    def stop(self):
        if self.process is None:
            return False

        self.process.terminate()
        return True

    async def run(self):
        self.process = await asyncio.create_subprocess_exec(
            '/usr/bin/openvpn', 'sourcelab.conf',
            stdout=asyncio.subprocess.PIPE
        )

        async for data in self.process.stdout:
            if not data:
                break

            self.output = self.output[:100] + [data]

        self.process = None
