__author__ = 'matth'


import win32service
import win32serviceutil
import win32api
import win32con
import win32event
import win32evtlogutil
import os, sys, string, time
from warden import WardenServer

class WardenService(win32serviceutil.ServiceFramework):
    _svc_name_ = "PythonWarden"
    _svc_display_name_ = "Python Warden"
    _svc_description_ = "The windows service for the Python Warden monitoring and metrics framework"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

def HandleCustomOptions(*args, **kwargs):
    print "Custom args=%s, kwargs=%s" % (args[0], kwargs)

def usage():
    try:
        fname = os.path.split(sys.argv[0])[1]
    except:
        fname = sys.argv[0]
    print "Usage: '%s [options] install|update|remove|start [...]|stop|restart [...]|debug [...]'" % fname
    print "Options for 'install' and 'update' commands only:"
    print " --username domain\\username : The Username the service is to run under"
    print " --password password : The password for the username"
    print " --startup [manual|auto|disabled|delayed] : How the service starts, default = manual"
    print " --interactive : Allow the service to interact with the desktop."
    print " --perfmonini file: .ini file to use for registering performance monitor data"
    print " --perfmondll file: .dll file to use when querying the service for"
    print "   performance data, default = perfmondata.dll"
    print "Options for 'start' and 'stop' commands only:"
    print " --wait seconds: Wait for the service to actually start or stop."
    print "                 If you specify --wait with the 'stop' option, the service"
    print "                 and all dependent services will be stopped, each waiting"
    print "                 the specified period."
    print "Common option: -h <warden home dir>"
    sys.exit(1)

def HandleCommandLine(argv=None):
    customInstallOptions='h:'
    if argv is None: argv = sys.argv

    if len(argv)<=1:
        usage()

    # Pull apart the command line
    import getopt
    try:
        opts, args = getopt.getopt(argv[1:], customInstallOptions,["password=","username=","startup=","perfmonini=", "perfmondll=", "interactive", "wait="])
    except getopt.error, details:
        print details
        usage()

    if len(args)<1:
        usage()

    if args[0] in ("install", "update") and '-h' not in dict(opts):
        print 'ERROR: -h option required'
        usage()

    win32serviceutil.HandleCommandLine(WardenService, customInstallOptions=customInstallOptions, customOptionHandler=HandleCustomOptions)

if __name__ == '__main__':
    HandleCommandLine()