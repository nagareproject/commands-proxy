# --
# Copyright (c) 2008-2022 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.admin import command


class Proxy(command.Command):
    DESC = 'Nginx reverse proxy dispatch rules generation'
    WITH_STARTED_SERVICES = True
    DEFAULT_PROXY_DIRECTIVES = [
        'proxy_set_header Host $host',
        'proxy_set_header X-Forwarded-Proto $scheme',
        'proxy_set_header X-Forwarded-Port $server_port',
        'proxy_redirect off'
    ]
    DEFAULT_WEBSOCKET_DIRECTIVES = DEFAULT_PROXY_DIRECTIVES + [
        'proxy_http_version 1.1',
        'proxy_set_header Upgrade $http_upgrade',
        'proxy_set_header Connection "Upgrade"'
    ]

    @staticmethod
    def generate_directives(directives):
        return (directive + ';' for directive in directives)

    def generate_location_directives(self, proxy_service, location, default_location_directives):
        location_directives = proxy_service.get_location_directives(location, default_location_directives)

        yield 'location {}/ {{'.format(location)
        for directive in self.generate_directives(location_directives):
            yield '    ' + directive
        yield '}\n'

    def generate_dir_directives(self, proxy_service, location, dirname, gzip):
        default_dir_directives = ['alias {}/'.format(dirname)]
        if gzip:
            default_dir_directives.append('gzip_static on')

        for directive in self.generate_location_directives(proxy_service, location, default_dir_directives):
            yield directive

    def generate_proxy_pass_directives(self, proxy_service, location, default_directives, url=None):
        is_socket, ssl, endpoint, app_url = proxy_service.endpoint
        proxy_directive = 'proxy_pass http{}://{}{}{}/'.format(
            's' if ssl else '',
            endpoint, ':' if is_socket else '',
            url or app_url
        )

        for directive in self.generate_location_directives(
            proxy_service,
            location,
            default_directives + [proxy_directive]
        ):
            yield directive

    def generate_app_directives(self, proxy_service, location, url=None):
        for directive in self.generate_proxy_pass_directives(proxy_service, location, self.DEFAULT_PROXY_DIRECTIVES, url):
            yield directive

    def generate_ws_directives(self, proxy_service, location):
        for directive in self.generate_proxy_pass_directives(
            proxy_service,
            location,
            self.DEFAULT_WEBSOCKET_DIRECTIVES,
            location
        ):
            yield directive

    def run(self, http_proxy_service, services_service):
        """
        """
        services_service(http_proxy_service.generate_directives, self)
