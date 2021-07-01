# --
# Copyright (c) 2008-2021 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.admin import command
from nagare.services import plugin


class Commands(command.Commands):
    DESC = 'HTTP reverse proxy dispatch rules generation subcommands'


class HTTPProxyService(plugin.Plugin):
    CONFIG_SPEC = dict(
        plugin.Plugin.CONFIG_SPEC,
        server={'___many___': 'boolean'},
        __many__={'___many___': 'boolean'}
    )

    def __init__(self, name, dist, server, services_service, **locations):
        services_service(super(HTTPProxyService, self).__init__, name, dist, server=server, **locations)

        self.server = [v for v, activated in server.items() if activated]
        self.locations = locations
        self.endpoint = (False, '', '')

    def handle_start(self, app, publisher_service, application_service):
        publisher = publisher_service.service
        app = application_service.service

        tcp, ssl, endpoint, _ = publisher.endpoint
        self.endpoint = (not tcp, ssl, endpoint, app.url)

    @staticmethod
    def merge_directives(directives, default_directives):
        directives_on = [v for v, activated in directives.items() if activated]
        directives_off = {v for v, activated in directives.items() if not activated}

        return [directive for directive in default_directives if directive not in directives_off] + directives_on

    def get_server_directives(self, default_directives):
        return self.merge_directives(self.server, default_directives)

    def get_location_directives(self, location, default_direcives):
        return self.merge_directives(self.locations.pop(location, {}), default_direcives)

    def generate_directives(self, proxy, statics_service, services_service, reloader_service=None):
        if reloader_service is not None:
            services_service(reloader_service.start, None)

        print('\n'.join(proxy.generate_directives(self.server)))
        if self.server:
            print()

        print('\n'.join(statics_service.generate_proxy_directives(self, proxy)))
        if self.locations:
            print()

        for location, directives in list(self.locations.items()):
            directives = {v for v, activated in directives.items() if activated}
            print('\n'.join(proxy.generate_location_directives(self, location, directives)))
