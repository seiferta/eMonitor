import struct
import socket
import threading
import select
import time
import datetime
import traceback
import random
from .extensions import db, events, classes, signal


class MonitorServer():
    
    app = None
    clients = {'clients': {}, 'time': datetime.datetime.now()}

    def __init__(self):
        self.ANY = ""
        self.MCAST_ADDR = ""
        self.MCAST_PORT = ""
        self.messages = []
        self.currentLayout = {}
        self.results = {}
        self.host = ""
        self.port = ""
        self.sock = None

    def init_app(self, app):
        MonitorServer.app = app
        events.addHandlerClass('*', 'emonitor.monitorserver.MonitorServer', self.handleEvent, ['in.params', 'in.condition'])

        self.ANY = app.config.get('MONITORSERVER_ANY', "0.0.0.0")
        self.MCAST_ADDR = app.config.get('MONITORSERVER_MCAST_ADDR', "224.168.2.9")
        self.MCAST_PORT = app.config.get('MONITORSERVER_MCAST_PORT', 1600)
        self.host = app.config.get('HOST')

        ip = socket.gethostbyname(socket.gethostname())
        if ip:
            self.host = ip
        self.port = app.config.get('PORT')

        signal.addSignal('monitorserver', 'clientsearchstart')
        signal.addSignal('monitorserver', 'clientsearchdone')

    def sendMessage(self, clientid, operation, *parameters):
        parameters = dict((x, y) for x, y in parameters)

        params = ""
        for p in parameters:
            params += '&%s=%s' % (p, parameters[p])

        if len(params) > 0: _parameters = '?' + params
        else: _parameters = ''

        if operation == "load":  # load monitor
            if "layoutid" in parameters and parameters['layoutid'] == '-1':
                    _parameters = 'http://%s:%s/monitor' % (self.host, self.port)
            else:
                _parameters = 'http://%s:%s/monitor/%%s%s' % (self.host, self.port, _parameters)

        elif operation == "reset":  # reset monitor
            _parameters = 'http://%s:%s/monitor/%s' % (self.host, self.port, '%s')
        elif operation == "execute":  # run script
            _parameters = params

        message = '%s|%s' % (clientid, operation)
        if _parameters != "":
            message += '|%s' % _parameters

        self.messages.append(message)
        try:
            _id = str(random.random())[2:10]
            t = threading.Thread(target=self.run, args=(_id,))
            t.start()
        except:
            _id = ""
            MonitorServer.app.logger.error('monitorserver: %s' % traceback.format_exc())
        return _id

    def sendMessageWithReturn(self, clientid, operation, *parameters):
        if len(parameters) == 0:
            _id = self.sendMessage(clientid, operation)
        else:
            _id = self.sendMessage(clientid, operation, *parameters)

        while _id not in self.results.keys():
            pass

        if _id in self.results:
            res = self.results[_id]
            del self.results[_id]
            return res
            
        return ""
        
    def getClients(self):
        signal.send('monitorserver', 'clientsearchstart', clients=[])
        monitors = classes.get('monitor').getMonitors()
        message, results = self.sendMessageWithReturn('0', 'ping')
        
        clients = {}
        for res in results:
            _id = res['data'].split('|')[0]
            clients[_id] = [(res['from'][0], res['name'])]
            if _id not in [str(m.id) for m in monitors]:
                clients[_id].append(None)
        for monitor in monitors:
            if str(monitor.id) in clients.keys():
                clients[str(monitor.id)].append(monitor)
            else:
                clients[str(monitor.id)] = [None, monitor]
        MonitorServer.clients = {'clients': clients, 'time': datetime.datetime.now()}
        signal.send('monitorserver', 'clientsearchdone', clients=clients.keys())
        return clients

    @staticmethod
    def incomeData(eventname, kwargs):
        pass
        
    @staticmethod
    def handleIncome(eventname, *kwargs):
        pass

    @staticmethod
    def handleEvent(eventname, *kwargs):
        from emonitor.extensions import scheduler

        #def cleanSchedules(monitorid):
        #    for schedjob in scheduler.get_jobs():
        #        if schedjob.name == 'changeState' and schedjob.args[0] == monitorid:
        #            scheduler.unschedule_job(schedjob)

        if eventname == "client_income":
            return kwargs
        params = []
        
        try:
            hdl = [hdl for hdl in classes.get('eventhandler').getEventhandlers(event=eventname) if hdl.handler == 'emonitor.monitorserver.MonitorServer'][0]
            
            for p in [v[1] for v in hdl.getParameterValues('in') if v[1] != '']:  # required parameters for method
                if p in kwargs[0]:
                    params.append((p, kwargs[0][p]))
        except:
            hdl = []
            MonitorServer.app.logger.error('monitorserver: %s' % traceback.format_exc())

        if kwargs[0]['mode'] != 'test':
            for monitorlayout in classes.get('monitorlayout').getLayouts():
                try:
                    if monitorlayout.trigger == eventname:
                        for p in hdl.getParameterValues('in'):
                            if p[0] == 'in.condition' and p[1] == '!activealarm':
                                if classes.get('alarm').getActiveAlarms().count() == 0:
                                    MonitorServer.changeLayout(monitorlayout.mid, monitorlayout.id, params)

                        scheduler.deleteJobForEvent('changeLayout')
                        MonitorServer.changeLayout(monitorlayout.mid, monitorlayout.id, params)
                        if monitorlayout.nextid != 0:
                            scheduler.add_date_job(MonitorServer.changeLayout, datetime.datetime.fromtimestamp(time.time() + monitorlayout.maxtime), [monitorlayout.mid, monitorlayout.nextid, params])
                except:
                    #MonitorServer.app.logger.error('monitorserver.handleEvent: %s' %traceback.format_exc())
                    pass
                finally: pass
        
        if not 'time' in kwargs[0]:
            kwargs[0]['time'] = []
        kwargs[0]['time'].append('monitorserver: message sent')
        return kwargs

    @staticmethod
    def changeLayout(monitorid, layoutid, *params):
        from emonitor.extensions import monitorserver
        MonitorServer.app.logger.debug('monitorserver: changeLayout for monitor %s > %s' % (monitorid, layoutid))
        parameters = tuple((u'layoutid', u'%s' % layoutid))
        for p in params:
            parameters.append((p[0], p[1]))  # do not change!
        l = MonitorLog.addLog(monitorid, 0, 'change layout', parameters)
        if l: MonitorServer.app.logger.error('monitorserver.addLog: %s' % l)
        message, result = monitorserver.sendMessageWithReturn(monitorid, 'load', parameters)

        l = MonitorLog.addLog(int(message.split('|')[0]), 0, message.split('|')[1], '|'.join(message.split('|')[2:]))
        if l: MonitorServer.app.logger.error('monitorserver.addLog: %s' % l)
        return 1

    def run(self, id):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1.0)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))

        message = ""
        result = None
        try:
            if len(self.messages) > 0:
                # Send data to the multicast group
                message = self.messages.pop()
                self.sock.sendto(message, (self.MCAST_ADDR, self.MCAST_PORT))
                
                # Look for responses from all recipients
                result = []
                while True:
                    try:
                        if select.select([self.sock], [], [], 3)[0]:  # wait 5 seconds
                            try:
                                data, server = self.sock.recvfrom(8192)
                                result.append({'data': data, 'from': server, 'name': socket.gethostbyaddr(server[0])[0]})
                                MonitorLog.addLog(int(data.split('|')[0]), 1, 'income', data.split('|')[1])
                            except socket.timeout:
                                break
                            except:
                                pass
                        else:  # timeout reached
                            break
                    except socket.error:
                        break
        finally:
            self.sock.close()
            self.results[id] = (message, result)

    def stop(self):
        self.sock.close()


class MonitorLog(db.Model):
    __tablename__ = 'monitorlog'
    
    timestamp = db.Column(db.TIMESTAMP, primary_key=True)
    clientid = db.Column(db.Integer)
    direction = db.Column(db.Integer, default=0)  # 0: ->, 1: <-
    type = db.Column(db.String(16), default='info')
    operation = db.Column(db.Text, default='')
    
    def __init__(self, timestamp, clientid, direction, monitortype, operation):
        self.timestamp = timestamp
        self.clientid = clientid
        self.direction = direction
        self.type = monitortype
        self.operation = operation
    
    @staticmethod
    def addLog(clientid, direction, logtype, operation):
        try:
            db.session.add(MonitorLog(datetime.datetime.now(), clientid, direction, logtype, str(operation)))
            db.session.commit()
            return None
        except:
            return traceback.print_exc()
        
    @staticmethod
    def clearLog():  # not tested
        db.session.delete(MonitorLog)
        db.session.commit()
        
    @staticmethod
    def getMonitorLogs(timestamp=0, clientid=0):
        if timestamp == 0 and clientid == 0:
            return db.session.query(MonitorLog).order_by('timestamp')
        elif timestamp == 0 and clientid != 0:
            return db.session.query(MonitorLog).filter_by(clientid=clientid).order_by('timestamp')
        else:
            return db.session.query(MonitorLog).filter_by(timestamp=timestamp)[0]
            
    @staticmethod
    def getLogForClient(clientid):
        return db.session.query(MonitorLog).filter((MonitorLog.clientid == clientid) | (MonitorLog.clientid == 0)).order_by('timestamp desc')
