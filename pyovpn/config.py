# -*- coding: utf-8 -*-
import yaml


class Config(object):

    def __init__(self, path, data={}):
        self.path = path
        self._data = data

    @staticmethod
    def load(path):
        with open(path, 'r') as f:
            return Config(path, yaml.load(f.read()))

    def save(self):
        with open(self.path, 'w') as f:
            f.write(yaml.dump(self._data, default_flow_style=False))

