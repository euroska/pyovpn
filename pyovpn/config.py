# -*- coding: utf-8 -*-
import datetime
import yaml
import os
import hashlib
import collections


class Config(object):

    DEFAULT = {
        'debug': False,
        'data_path': '/etc/pyovpn/data',
        'secret': hashlib.sha256(
            datetime.datetime.now().isoformat().encode('utf-8')
        ).hexdigest(),
        'static_path': os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'static'
        ),
        'general': {
            'default_names': {
                'cn': 'OpenVPN cert',
                'o': 'Some company',
                'ou': 'Some unit',
            },
            'openvpn_binary': os.popen('which openvpn').read().strip(),
            'log_length': 100,
        },
        'users': {},
        'vpns': {},
        'web': {
            'jsonrpc': '/api/jsonrpc',
            'websock': '/api/ws',
            'listen': '127.0.0.1',
            'port': 8080,
        }
    }

    def __init__(self, path, data={}):
        self.path = path
        self._data = Config.update(self.DEFAULT.copy(), data)

    @staticmethod
    def update(d, u):
        for k, v in u.items():
            if isinstance(v, collections.Mapping):
                d[k] = Config.update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    @staticmethod
    def load(path):
        with open(path, 'r') as f:
            return Config(path, yaml.load(f.read()))

    @staticmethod
    def generate(data=DEFAULT):
        return yaml.dump(data, default_flow_style=False)

    def save(self):
        with open(self.path, 'w') as f:
            f.write(Config.generate(self._data))

    def __getitem__(self, key):
        return self._data[key]

    def generateStructure(self):
        paths = [
            '/templates/user',
            '/templates/server',
            '/tokens',
            '/vpns'
        ]

        for rel_path in paths:
            path = self._data['data_path'] + rel_path
            if not os.path.exists(path):
                os.makedirs(path)

