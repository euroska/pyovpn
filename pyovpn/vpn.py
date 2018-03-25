import os
import asyncio
from jinja2 import Environment
from .ca import *


class VPN(object):
    '''
    '''
    RESTRICTED_CN = ['ca', 'server']

    @staticmethod
    def createConfig(manager, name):
        '''
        Create configuration for VPN based on global config and VPN name
        '''
        path = manager.config['data_path']
        root = os.path.join(path, 'vpns', name)
        return {
            'root': root,
            'keys': os.path.join(root, 'keys'),
            'csrs': os.path.join(root, 'csrs'),
            'certs': os.path.join(root, 'certs'),

            'server_template_path': os.path.join(root, 'server.ovpn.tpl'),
            'server_config_path': os.path.join(root, 'server.ovpn'),
            'user_template_path': os.path.join(root, 'user.ovpn.tpl'),

            'ca_key_password': None,
            'ca_cert_path': os.path.join(root, 'ca.pem'),
            'ca_key_path': os.path.join(root, 'ca.key'),
            'dh_path': os.path.join(root, 'dh.pem'),
            'crl_path': os.path.join(root, 'crl.pem'),
            'sequence_path': os.path.join(root, 'sequence'),

            'server_key_path': os.path.join(root, 'keys', 'server.key'),
            'server_csr_path': os.path.join(root, 'csrs', 'server.csr'),
            'server_cert_path': os.path.join(root, 'certs', 'server.pem'),
        }

    @staticmethod
    def inicialize(manager, name, subject={}):
        '''
        Create OpenVPN runtime environment
        '''
        config = VPN.createConfig(manager, name)

        root = os.path.join(manager.config['data_path'], 'vpns', name)
        paths = [
            root,
            config['keys'],
            config['csrs'],
            config['certs'],
        ]

        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path)

        ca = CA.inicialize(config=config, subject=subject)

        server_csr, server_key = Cert.genCsr(subject={'cn': 'server'})
        server_cert = ca.signCert(server_csr, server=True)

        saveKeyPem(server_key, config['server_key_path'])
        savePem(server_csr, config['server_csr_path'])
        savePem(server_cert, config['server_cert_path'])

        manager.config['vpns'][name] = {
            'enabled': False,
        }
        manager.config.save()
        return VPN(manager, name)

    def __init__(self, manager, name):
        '''
        inicialize VPN configuration
        '''
        self.manager = manager
        self.name = name
        self.jinja = Environment()
        self.config = VPN.createConfig(manager, name)
        self.enable = self.manager.config['vpns'][name].get('enabled', False)
        self.ca = CA(self.config)
        self.server_cert = None
        self.server_key = None

        self.server_template = None
        self.server_config = None
        self.user_template = None

        self.users = []
        self.log = []
        self.online = {}

        self.process = None
        self.loop = None

        self.keys = self.loadKeys()
        self.csrs = self.loadCsrs()
        self.certs = self.loadCerts()

        self.subject = self.ca.cert.parseSubject()
        self.ip = self.parseIp()
        self.manager.vpns[self.name] = self

    def loadKeys(self):
        '''
        Load all stored RSA keys
        '''
        keys = {}
        for root, dirnames, files in os.walk(self.config['keys']):
            for key in files:
                if key.endswith('.key'):
                    try:
                        cn = os.path.splitext(key)[0]
                        k = getKey(os.path.join(root, key))
                        keys[cn] = k
                        if cn == 'server':
                            self.server_key = k

                    except Exception as e:
                        pass

            return keys
        return {}

    def loadCsrs(self):
        '''
        Load all stored Certificate Sign Request
        '''
        csrs = {}
        for root, dirnames, files in os.walk(self.config['csrs']):
            for csr in files:
                if csr.endswith('.csr'):
                    with open(os.path.join(root, csr), 'rb'):
                        try:
                            c = getCsr(os.path.join(root, csr))
                            if c is not None:
                                csrs[os.path.splitext(csr)[0]] = c

                        except Exception as e:
                            pass
            return csrs
        return {}

    def loadCerts(self):
        '''
        Load all certificates
        '''
        crts = {}
        self.users = []
        for root, dirnames, files in os.walk(self.config['certs']):
            for crt in files:
                if crt.endswith('.pem'):
                    with open(os.path.join(root, crt), 'rb'):
                        try:
                            cn = os.path.splitext(crt)[0]
                            c = Cert(
                                os.path.join(root, crt),
                                self.keys.get(cn),
                                csr=self.csrs.get(cn)
                            )

                            if c.serial_number in self.ca.crl.revoked_numbers:
                                continue

                            if c is not None:
                                crts[cn] = c

                            if cn == 'server':
                                self.server_cert = c

                            elif cn not in self.RESTRICTED_CN:
                                self.users.append(cn)

                        except Exception as e:
                            print(e)
            return crts
        return {}

    def parseIp(self):
        '''
        '''
        return {}

    def hasUser(self, username):
        return username in self.users

    def cnAdd(self, cn, subject={}):
        if cn in self.RESTRICTED_CN:
            return

        if cn not in self.users:
            self.users.append(cn)

        s = self.subject
        s.update(subject)
        s['cn'] = cn
        csr, key = Cert.genCsr(subject=s)
        cert = self.ca.signCert(csr, server=False)

        saveKeyPem(key, os.path.join(self.config['keys'], '%s.key' % cn))
        savePem(csr, os.path.join(self.config['csrs'], '%s.csr' % cn))
        savePem(cert, os.path.join(self.config['certs'], '%s.pem' % cn))

        self.keys[cn] = key
        self.csrs[cn] = csr
        self.certs[cn] = cert

    def cnRevoke(self, cn, save=True):
        '''
        Revoke certificate witn CN
        '''
        if cn in self.certs:
            self.ca.crl.revoke(self.certs[cn], save=save)
            del self.certs[cn]

        if cn in self.users:
            self.users.remove(cn)

        self.reload()
        return True

    def cnRenew(self, cn):
        '''
        Renew certificate with CN
        '''
        subject = {}
        if cn in self.certs:
            subject = self.certs[cn].parseSubject()

        self.cnRevoke(cn, save=False)
        self.cnAdd(cn, subject=subject)
        self.normalize()

    def normalize(self):
        '''
        Normalize certificate revokation list
        There is posibility, that leak some revokation request.
        This method revoke all except active
        '''
        active = [
            cert.serial_number for cert in self.certs.values()
        ]
        if self.server_cert is not None:
            active += [self.server_cert.serial_number]

        self.ca.crl.normalize(active)

    def serverTemplateGet(self):
        '''
        Get server jinja template
        '''
        if self.server_template is not None:
            return self.server_template

        path = self.config['server_template_path']
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.server_template = f.read()
                return self.server_template

        return ''

    def serverTemplateSet(self, template, regenerate=False):
        '''
        Set server jinja template
        '''
        path = self.config['server_template_path']
        with open(path, 'w') as f:
            f.write(template)
            self.server_template = template

        if regenerate:
            self.configSet()

    def userTemplateGet(self):
        '''
        Get user jinja template
        '''
        if self.user_template is not None:
            return self.user_template

        path = self.config['user_template_path']
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.user_template = f.read()
                return self.user_template
        return ''

    def userTemplateSet(self, template):
        '''
        Set user jinja template
        '''
        path = self.config['user_template_path']

        with open(path, 'w') as f:
            f.write(template)
            self.user_template = template

    def userConfig(self, username):
        '''
        Generate user config with jinja
        '''
        template = self.jinja.from_string(
            self.userTemplateGet()
        )
        context = {
            'username': username,
            'ip': self.ip.get(username),
            'ca': serializePem(self.ca.cert.cert, str=True),
        }
        if username in self.certs:
            context['cert'] = serializePem(self.certs[username].cert, str=True)

        if username in self.keys:
            context['key'] = serializeKeyPem(self.keys[username], str=True)

        return template.render(
            context
        )

    def configGet(self, regenerate=False):
        '''
        Get current server config
        generated with jinja template
        '''
        if self.server_config is not None:
            return self.server_config

        path = self.config['server_config_path']
        if os.path.exists(path) and not regenerate:
            with open(path, 'r') as f:
                self.server_config = f.read()
                return self.server_config

        template = self.jinja.from_string(
            self.serverTemplateGet()
        )
        context = self.config.copy()
        context['name'] = self.name
        context['ca'] = serializePem(self.ca.cert.cert, str=True)

        if self.server_cert:
            context['cert'] = serializePem(self.server_cert.cert, str=True)

        if self.server_key:
            context['key'] = serializeKeyPem(self.server_key, str=True)

        return template.render(
            context
        )

    def configSet(self, config=None):
        if config is None:
            config = self.configGet(regenerate=True)

        self.server_config = config
        with open(self.config['server_config_path'], 'w') as f:
            f.write(self.server_config)

    def serializeList(self):
        return {
            'name': self.name,
            'enable': self.enable,
            'running': self.process is not None,
            'users': {
                user: {
                    'ip': self.ip.get(user),
                    'active': self.online.get(user, False)
                } for user in self.users
            }
        }

    def serializeDetail(self):
        return {
            'name': self.name,
            'enable': self.enable,
            'subject': self.subject,
            'users': {
                user: {
                    'ip': self.ip.get('user'),
                    'active': self.online.get(user, False)
                } for user in self.users
            }
        }

    def start(self):
        if self.process is None:
            self.await = self.run()
            asyncio.ensure_future(self.await)
            return True

        return False

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
        '''
        Running loop
        Read stdout and store log
        '''
        self.process = await asyncio.create_subprocess_exec(
            '/usr/bin/openvpn', self.config['server_config_path'],
            stdout=asyncio.subprocess.PIPE
        )

        async for raw_data in self.process.stdout:
            data = raw_data.decode('utf8')

            self.manager.notify({
                'message': 'pyovpn.vpn.log.diff',
                'body': {
                    'name': self.name,
                    'log': data,
                    'running': True,
                }
            })
            self.log = self.log[:100] + [data]

            if not data:
                break

        self.manager.notify({
            'message': 'pyovpn.vpn.log.diff',
            'body': {
                'name': self.name,
                'log': 'STOPED',
                'running': False,
            }
        })
        self.process = None
