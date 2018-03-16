# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='pyovpn',
    version='1.0',
    description='Config for OpenVPN',
    author='Martin Miksanik',
    author_email='miksanik@gmail.com',
    url='https://github.com/euroska/pyovpn',
    packages=['pyovpn'],
    install_requires=[
    ],
    scripts=[
        'bin/pyovpn'
    ],
)
