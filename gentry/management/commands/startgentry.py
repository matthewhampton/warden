"""
sentry.management.commands.start
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from optparse import make_option
import sys

from cherrypy import wsgiserver
from sentry.services.base import Service
import sentry.wsgi


class Command(BaseCommand):
    args = '<service>'
    help = 'Starts the specified service'

    option_list = BaseCommand.option_list + (
        make_option('--debug',
            action='store_true',
            dest='debug',
            default=False),
        make_option('--noupgrade',
            action='store_false',
            dest='upgrade',
            default=True),
        make_option('--workers', '-w',
            dest='workers',
            type=int,
            default=None),
    )

    def handle(self, service_name='http', address=None, upgrade=True, **options):
        from sentry.services import http, udp
        if address:
            if ':' in address:
                host, port = address.split(':', 1)
                port = int(port)
            else:
                host = address
                port = None
        else:
            host, port = None, None

        if upgrade:
            # Ensure we perform an upgrade before starting any service
            print "Performing upgrade before service startup..."
            call_command('upgrade', verbosity=0)

        sys.argv = sys.argv[:1]

        service = GentryHTTPServer(debug=options.get('debug'), host=host, port=port, workers=options.get('workers'))

        service.run()

class GentryHTTPServer(Service):
    name = 'http'

    def __init__(self, host=None, port=None, debug=False, workers=None):
        from sentry.conf import settings

        self.host = host or settings.WEB_HOST
        self.port = port or settings.WEB_PORT

        self.workers = workers
        self.server = None

        options = (settings.WEB_OPTIONS or {}).copy()
        options['bind'] = '%s:%s' % (self.host, self.port)
        options['debug'] = debug
        options.setdefault('daemon', False)
        options.setdefault('timeout', 30)
        if workers:
            options['workers'] = workers

        self.options = options

    def run(self):

        self.server = wsgiserver.CherryPyWSGIServer((self.host, self.port), sentry.wsgi.application, numthreads=self.options['workers'])
        try:
            self.server.start()
        except KeyboardInterrupt:
            self.server.stop()
