# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='pyovpn',
    version='1.0',
    description='OpenVPN orchestrate util',
    author='Martin Miksanik, Jiri Peterek',
    author_email='miksanik@gmail.com, jiri.peterek@gmail.com',
    url='https://github.com/euroska/pyovpn',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'aiohttp',
        'pyyaml',
        'jsonschema',
        'jinja2',
        'cryptography',
        'pytz'
    ],
    scripts=[
        'bin/pyovpn',
        'bin/pyovpnctl',
    ],
)
