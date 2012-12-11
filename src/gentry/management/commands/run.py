from django.core.management.base import BaseCommand
from gentry import settings
from gentry.wsgi import application
from cherrypy import wsgiserver


class Command(BaseCommand):
    args = '<service>'
    help = 'Starts the specified service'

    def handle(self, *args, **options):

        host = settings.SENTRY_WEB_HOST
        port = settings.SENTRY_WEB_PORT

        server = wsgiserver.CherryPyWSGIServer((host, port), application)

        try:
            print "Starting CherryPy server on %s:%s" % (host, port)
            server.start()
        except KeyboardInterrupt:
            print "Shutting down CherryPy server..."
            server.stop()

