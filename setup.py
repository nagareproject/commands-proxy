# Encoding: utf-8

# --
# Copyright (c) 2008-2020 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from os import path

from setuptools import setup, find_packages


here = path.normpath(path.dirname(__file__))

with open(path.join(here, 'README.rst')) as long_description:
    LONG_DESCRIPTION = long_description.read()

setup(
    name='nagare-commands-proxy',
    author='Net-ng',
    author_email='alain.poirier@net-ng.com',
    description='HTTP reverse proxy dispatch rules generation',
    long_description=LONG_DESCRIPTION,
    license='BSD',
    keywords='',
    url='https://github.com/nagareproject/commands-proxy',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    install_requires=['nagare-services-statics', 'nagare-server-http'],
    entry_points='''
        [nagare.commands]
        proxy = nagare.admin.proxy:Commands

        [nagare.commands.proxy]
        nginx = nagare.admin.nginx_proxy:Proxy

        [nagare.services]
        http_proxy = nagare.admin.proxy:HTTPProxyService
    '''
)
