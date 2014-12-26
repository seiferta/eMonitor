import time
from emonitor.extensions import monitorserver, classes


class Script:
    """Script class"""
    def __init__(self):
        pass

    @staticmethod
    def handleEvent(eventname, *kwargs):
        """
        Event handler for scripts class, adds own processing time

        :param eventname: *emonitor.modules.scripts.script.Script*
        :param kwargs: *time*
        :return: kwargs
        """
        stime = time.time()
        hdl = [hdl for hdl in classes.get('eventhandler').getEventhandlers(event=eventname) if hdl.handler == 'emonitor.modules.scripts.script.Script']

        scriptname = ""
        if len(hdl) == 1:
            if "in.scriptname" in hdl[0].getParameterList('in'):
                scriptname = hdl[0].getParameterValue("in.scriptname")

        for m in classes.get('monitor').getMonitors():
            for l in m.getLayouts():
                if l.trigger == eventname:  # find client id for defined event
                    if 'mode' in kwargs[0].keys() and kwargs[0]['mode'] != 'test':
                        monitorserver.sendMessage(str(m.id), 'execute|%s' % scriptname)  # execute script on client

        if 'time' not in kwargs[0]:
            kwargs[0]['time'] = []
        kwargs[0]['time'].append('scripts: script "%s" done in %s sec.' % (scriptname, time.time() - stime))
        return kwargs
