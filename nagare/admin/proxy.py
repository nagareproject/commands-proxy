# --
# Copyright (c) 2008-2022 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import re

from nagare.admin import command
from nagare.services import plugin


class Commands(command.Commands):
    DESC = 'HTTP reverse proxy dispatch rules generation subcommands'


class HTTPProxyService(plugin.Plugin):
    CONFIG_SPEC = dict(
        plugin.Plugin.CONFIG_SPEC,
        ___many___='boolean',
        __many__={'___many___': 'boolean'}
    )

    def __init__(self, name, dist, services_service, **directives):
        proxy_directives = {
            directive: directives[directive] for directive in set(directives) - set(plugin.Plugin.CONFIG_SPEC)
        }

        self.directives = {
            directive: value
            for directive, value
            in proxy_directives.items()
            if not isinstance(value, dict)
        }

        self.locations = {
            re.sub('//+', '/', location).rstrip('/') or '/': values
            for location, values
            in proxy_directives.items()
            if isinstance(values, dict)
        }
        self.endpoint = (False, '', '')

        plugin_config = {
            directive: directives[directive]
            for directive in plugin.Plugin.CONFIG_SPEC
            if directive in directives
        }
        plugin_config.update(self.directives)
        plugin_config.update(self.locations)

        services_service(super(HTTPProxyService, self).__init__, name, dist, **plugin_config)

    def handle_start(self, app, publisher_service, application_service):
        publisher = publisher_service.service
        app = application_service.service

        tcp, ssl, endpoint, _ = publisher.endpoint
        self.endpoint = (not tcp, ssl, endpoint, app.url)

    @staticmethod
    def merge_directives(directives, default_directives):
        directives_on = {directive for directive, activated in directives.items() if activated} - set(default_directives)
        directives_off = {directive for directive, activated in directives.items() if not activated}

        return list(directives_on) + [directive for directive in default_directives if directive not in directives_off]

    def get_server_directives(self, default_directives):
        return self.merge_directives(self.server, default_directives)

    def get_location_directives(self, location, default_direcives):
        has_directive = location in self.locations
        location_directives = self.locations.pop(location, {})
        if has_directive and not location_directives:
            return None

        return self.merge_directives(location_directives, default_direcives)

    def generate_directives(self, proxy, statics_service, services_service, reloader_service=None):
        if reloader_service is not None:
            services_service(reloader_service.start, None)

        print('\n'.join(proxy.generate_server_directives(self, self.directives)))
        if self.directives:
            print('')

        print('\n'.join(statics_service.generate_proxy_directives(self, proxy)))
        if self.locations:
            print('')

        for location, directives in list(self.locations.items()):
            directives = {v for v, activated in directives.items() if activated}
            print('\n'.join(proxy.generate_location_directives(self, location, directives)))
