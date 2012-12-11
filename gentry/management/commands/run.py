"""
sentry.management.commands.start
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from django.core.management.base import BaseCommand, CommandError
import sys


class Command(BaseCommand):
    args = '<service>'
    help = 'Starts the specified service'


    def handle(self, *args, **options):

        from cherrypy import wsgiserver
        import gentry.wsgi

        server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 8000), gentry.wsgi.application)
        try:
            print "Starting CherryPy server..."
            server.start()
        except KeyboardInterrupt:
            print "Shutting down CherryPy server..."
            server.stop()

