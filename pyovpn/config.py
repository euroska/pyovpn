# -*- coding: utf-8 -*-
import yaml
import os


class Config(object):

    DEFAULT = {
        'data_path': '/etc/pyovpn/data',
        'general': {
            'default_names': {
                'common_name': 'OpenVPN cert',
                'organizational_unit_name': 'Some unit',
                'organization_name': 'Some company',
            },
            'openvpn_binary': '/usr/bin/openvpn',
            'log_length': 100,
        },
        'users': {
            'admin': {
                'is_admin': True,
                'is_anonymouse': False,
                'password': 'heslo',
            },
            'test': {
                'is_admin': False,
                'is_anonymouse': False,
                'password': 'test',
            }
        },
        'vpns': {
            'test': {
                'enable': True,
                'users': ['admin', 'test']
            }
        },
        'web': {
            'jsonrpc': '/api/jsonrpc',
            'websock': '/api/ws',
            'port': 8584,
        }
    }

    def __init__(self, path, data={}):
        self.path = path
        self._data = data

    @staticmethod
    def load(path):
        with open(path, 'r') as f:
            return Config(path, yaml.load(f.read()))

    @staticmethod
    def generate():
        return yaml.dump(Config.DEFAULT, default_flow_style=False)

    def save(self):
        with open(self.path, 'w') as f:
            f.write(yaml.dump(self._data, default_flow_style=False))

    def __getitem__(self, key):
        return self._data[key]

    def generateStructure(self):
        paths = [
            '/templates/client',
            '/templates/server',
            '/tokens',
            '/vpns'
        ]

        for rel_path in paths:
            path = self._data['data_path'] + rel_path
            if not os.path.exists(path):
                os.makedirs(path)

