from django.core.management.base import BaseCommand, CommandError
from gentry import settings
from cherrypy import wsgiserver
import gentry.wsgi


class Command(BaseCommand):
    args = '<service>'
    help = 'Starts the specified service'

    def handle(self, *args, **options):

        host = settings.SENTRY_WEB_HOST
        port = settings.SENTRY_WEB_PORT

        server = wsgiserver.CherryPyWSGIServer((host, port), gentry.wsgi.application)

        try:
            print "Starting CherryPy server on %s:%s" % (host, port)
            server.start()
        except KeyboardInterrupt:
            print "Shutting down CherryPy server..."
            server.stop()

