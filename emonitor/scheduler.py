import logging
import random
import datetime, time
from apscheduler.scheduler import Scheduler as ApScheduler
from emonitor.extensions import signal
from emonitor.sockethandler import SocketHandler

logging.basicConfig()
logger = logging.getLogger('apscheduler.scheduler')
logger.setLevel(50)  # critical


class MyScheduler(ApScheduler):
    
    app = None

    def __init__(self, gconfig=None, **options):
        if not gconfig: gconfig = {}
        ApScheduler.__init__(self, gconfig, **options)
        self.misfire_grace_time = 10  # 10 seconds
        self.coalesce = True

        signal.connect('scheduler', 'process', handleScheduleSignals.doHandle)
    
    def initJobs(self, app):
        MyScheduler.app = app

        self.add_listener(MyScheduler.mylogger, 128)  # 128: job_error
        self.add_listener(MyScheduler.myDone, 64)  # 64: executed

        from emonitor.observer import observeFolder
        self.add_interval_job(observeFolder, seconds=app.config.get('OBSERVERINTERVAL', 2), kwargs={'path': app.config.get('PATH_INCOME', app.config.get('PATH_DATA'))})
        app.logger.info('scheduler: job added "observer"')

    @staticmethod
    def mylogger(event):
        if event.exception:
            MyScheduler.app.logger.error('scheduler: %s' % event.exception)
            print event.__dict__
        else:
            MyScheduler.app.logger.error('error in scheduler event')

    @staticmethod
    def myDone(event):
        if event.job.id:
            signal.send('scheduler', 'process', jid=event.job.id, state='done')

    # delete all future jobs for monitors with given id
    def deleteJobForMonitor(self, monitorid):
        for j in self.get_jobs():
            if "'monitorid', %s" % monitorid in str(j.args):
                self.unschedule_job(j)
        return 1

    def add_single_job(self, func, args=None, kwargs=None, **options):
        jid = random.random()
        i = 0.1
        while i < 10.0:
            try:
                j = self.add_date_job(func, datetime.datetime.fromtimestamp(time.time() + i), args, kwargs, **options)
                j.id = jid
                break
            except ValueError:
                i += 1.0
        return jid

    def deleteJobForEvent(self, event):
        """
        delete all jobs for given event
        :class:`~MyScheduler` class.

        :rtype: :int:1 if done
        """
        for j in self.get_jobs():
            if j.name == event:
                self.unschedule_job(j)
        return 1


class handleScheduleSignals(SocketHandler):
    @staticmethod
    def doHandle(sender, **extra):
        if 'jid' in extra:
            SocketHandler.send_message(str(extra['jid']))
        else:
            SocketHandler.send_message('scheduler.process', **extra)