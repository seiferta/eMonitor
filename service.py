import sys
import os
os.chdir(os.path.realpath(__file__)[:os.path.realpath(__file__).rfind(os.sep)])
sys.path.append('emonitor')  # do not remove to find wsgiserver2
import win32serviceutil
import win32service
import win32event
import cherrypy
from emonitor import app
from emonitor.webserver import webserver


class eMonitorService(win32serviceutil.ServiceFramework):
    """NT Service."""

    _svc_name_ = "eMonitorService"
    _svc_display_name_ = "eMonitor Service"
    _svc_description_ = "Service for eMonitor Application"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        # create an event that SvcDoRun can wait on and SvcStop
        # can set.
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def SvcDoRun(self):
        app.config['service'] = True  # activate service configuration
        webserver(app)
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        cherrypy.engine.exit()
        #cherrypy.server.stop()
        win32event.SetEvent(self.stop_event)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(eMonitorService)
