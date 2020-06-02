# --
# Copyright (c) 2008-2020 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.admin import command


class Proxy(command.Command):
    DESC = 'Apache reverse proxy dispatch rules generation'
    WITH_STARTED_SERVICES = True
    DEFAULT_LOCATION_DIRECTIVE = ['Require all granted']
    DEFAULT_PROXY_DIRECTIVES = ['RequestHeader set X-Forwarded-Proto expr=%{REQUEST_SCHEME}']

    @staticmethod
    def generate_directives(directives):
        return directives

    def generate_location_directives(self, proxy_service, location, default_location_directives):
        location_directives = proxy_service.get_location_directives(location, default_location_directives)

        yield '<Location "{}">'.format(location)
        for directive in self.generate_directives(location_directives):
            yield '    ' + directive
        yield '</Location>\n'

    def generate_dir_directives(self, proxy_service, location, dirname, gzip):
        yield 'Alias "{}" "{}"'.format(location, dirname)

        directives = []
        if gzip:
            directives += [
                'AddEncoding gzip .gz',
                'RewriteEngine on',
                'RewriteCond %{REQUEST_FILENAME}.gz -f',
                r'RewriteRule ^(.*\.(css|js))$ $1.gz [QSA,L]',
                r'RewriteRule "\.js\.gz" "-" [T=text/javascript]',
                r'RewriteRule "\.css\.gz" "-" [T=text/css]'
            ]

        for directive in self.generate_location_directives(proxy_service, location, self.DEFAULT_LOCATION_DIRECTIVE + directives):
            yield directive

    def generate_proxy_pass_directives(self, proxy_service, location, protocol, url=None):
        is_socket, ssl, endpoint, app_url = proxy_service.endpoint
        proxy_directive = 'ProxyPass "{}{}{}://{}{}"'.format(
            (endpoint + '|') if is_socket else '',
            protocol,
            's' if ssl else '',
            'localhost' if is_socket else endpoint,
            url or app_url
        )

        for directive in self.generate_location_directives(
            proxy_service,
            location,
            self.DEFAULT_PROXY_DIRECTIVES + [proxy_directive]
        ):
            yield directive

    def generate_app_directives(self, proxy_service, location):
        for directive in self.generate_proxy_pass_directives(proxy_service, location, 'http'):
            yield directive

    def generate_ws_directives(self, proxy_service, location):
        for directive in self.generate_proxy_pass_directives(proxy_service, location, 'ws', location):
            yield directive

    def run(self, http_proxy_service, services_service):
        """
        """
        services_service(http_proxy_service.generate_directives, self)
