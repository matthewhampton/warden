__author__ = 'matth'


import win32service
import win32serviceutil
import win32api
import win32con
import win32event
import win32evtlogutil
import os, sys, string, time
import servicemanager
from warden import WardenServer, AutoConf

class WardenService(win32serviceutil.ServiceFramework):
    _svc_name_ = "WardenPython"
    _svc_display_name_ = "Warden Service"
    _svc_description_ = "The windows service for the Warden monitoring and metrics framework"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        home = win32serviceutil.GetServiceCustomOption(WardenService._svc_name_, 'WARDEN_HOME', defaultValue=None)
        home = AutoConf.get_home(home)
        servicemanager.LogInfoMsg("Starting Warden with home directory: %s" % home)
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

def HandleCustomOptions(*args, **kwargs):
    opts = dict(args[0]) if args else {}
    home = AutoConf.get_home(opts.get('-h', None))
    win32serviceutil.SetServiceCustomOption(WardenService._svc_name_, 'WARDEN_HOME', home)

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

    win32serviceutil.HandleCommandLine(WardenService, serviceClassString='warden.Win32Service.WardenService', customInstallOptions=customInstallOptions, customOptionHandler=HandleCustomOptions)

if __name__ == '__main__':
    HandleCommandLine()