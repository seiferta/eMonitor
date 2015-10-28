import time
import logging
from emonitor.extensions import monitorserver
from emonitor.modules.monitors.monitor import Monitor
from emonitor.modules.events.eventhandler import Eventhandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


class Script:
    """Script class"""
    def __init__(self):
        pass

    @staticmethod
    def handleEvent(eventname, **kwargs):
        """
        Event handler for scripts class, adds own processing time

        :param eventname: *emonitor.modules.scripts.script.Script*
        :param kwargs: *time*
        :return: kwargs
        """
        stime = time.time()
        hdl = [hdl for hdl in Eventhandler.getEventhandlers(event=eventname) if hdl.handler == 'emonitor.modules.scripts.script.Script']

        scriptname = ""
        if len(hdl) == 1:
            if "in.scriptname" in hdl[0].getParameterList('in'):
                scriptname = hdl[0].getParameterValue("in.scriptname")

        for m in Monitor.getMonitors():
            for l in m.getLayouts():
                if l.trigger == eventname:  # find client id for defined event
                    if 'mode' in kwargs.keys() and kwargs['mode'] != 'test':
                        monitorserver.sendMessage(str(m.id), 'execute|%s' % scriptname)  # execute script on client
                    else:
                        logger.info('script started TESTMODE: %s' % scriptname)

        if 'time' not in kwargs.keys():
            kwargs['time'] = []
        kwargs['time'].append(u'scripts: script "{}" done in {} sec.'.format(scriptname, time.time() - stime))
        return kwargs
