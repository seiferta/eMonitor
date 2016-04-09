import os
import time
import datetime
import shutil
import requests
import re
import yaml
from collections import OrderedDict
import logging

from flask import current_app, flash, render_template, abort
from flask.templating import TemplateNotFound
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.sql.functions import count
from emonitor.modules.alarms import alarmutils
from emonitor.modules.alarms.alarmtype import AlarmType
from emonitor.modules.alarmobjects.alarmobject import AlarmObject
from emonitor.modules.alarmkeys.alarmkey import Alarmkey
from emonitor.modules.alarms.alarmhistory import AlarmHistory
from emonitor.modules.alarms.alarmattribute import AlarmAttribute
from emonitor.modules.alarms.alarmfield import AlarmField, AFBasic
from emonitor.modules.maps.map import Map
from emonitor.modules.settings.settings import Settings
from emonitor.modules.streets.street import Street
from emonitor.modules.streets.city import City
from emonitor.modules.settings.department import Department
from emonitor.modules.cars.car import Car
from emonitor.extensions import babel, db, events, scheduler, signal

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

USE_NOMINATIM = 0
LASTALARM = 0.0  # timestamp ini millies


class Alarm(db.Model):
    """Alarm class"""
    __tablename__ = 'alarms'
    __table_args__ = {'extend_existing': True}

    ALARMSTATES = {'0': 'created', '1': 'active', '2': 'done'}
    """
    - 0: alarm *created*
    - 1: alarm *active*
    - 2: alarm *done*
    - 3: alarm *archived* (not in list, only for admin area)
    """
    ALARMTYPES = {'1': 'fax', '2': 'manual'}
    """
    - 1: alarm by *fax* created
    - 2: alarm *manual* created
    """
    ROUTEURL = "http://www.yournavigation.org/api/1.0/gosmore.php"
    """
    URL for routing webservice
    """

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DATETIME)
    _key = db.Column('key', db.Text)
    type = db.Column(db.Integer, default=0)
    state = db.Column(db.Integer, default=0)
    attributes = db.relationship("AlarmAttribute", collection_class=attribute_mapped_collection('name'), cascade="all, delete-orphan")
    history = db.relationship(AlarmHistory.__name__, backref="alarms", lazy='joined', cascade="all, delete-orphan")

    # additional properties defined in alarmutils
    endtimestamp = property(alarmutils.get_endtimestamp)
    cars1 = property(alarmutils.get_cars1)
    cars2 = property(alarmutils.get_cars2)
    material = property(alarmutils.get_material, alarmutils.set_material)
    city = property(alarmutils.get_city, alarmutils.set_city)
    key = property(alarmutils.get_key)
    street = property(alarmutils.get_street, alarmutils.set_street)
    street2 = property(alarmutils.get_street2)
    streetno = property(alarmutils.get_streetno)

    housenumber = property(alarmutils.get_housenumber)

    object = property(alarmutils.get_object, alarmutils.set_object)
    person = property(alarmutils.get_person)
    priority = property(alarmutils.get_priority)
    remark = property(alarmutils.get_remark)
    lat = property(alarmutils.get_lat)
    lng = property(alarmutils.get_lng)
    zoom = property(alarmutils.get_zoom)
    position = property(alarmutils.get_position, alarmutils.set_position)
    marker = property(alarmutils.get_marker)

    def __init__(self, timestamp, key, type, state):
        self.timestamp = timestamp
        self._key = key
        self.type = type  # 1:automatic/fax, 2: manual
        self.state = state  # 1: active, 0:created, 2:done, 3:archived

    def get(self, attrname, default=''):
        """
        Getter for attribute names

        :param attrname: name of attribute
        :param optional default: deliver default value if not stored in database
        :return: value of attribute
        """
        if attrname in self.attributes:
            return self.attributes[attrname].value
        return default

    def set(self, attrname, value):
        """
        Setter for attributes

        :param attrname: attribute name
        :param value: value
        """
        if attrname in self.attributes:
            self.attributes[attrname].value = value
        else:
            self.attributes[attrname] = AlarmAttribute(attrname, value)

    def addHistory(self, name, value, dtime=None):
        """
        Add history entry for alarm to store actions of alarm using
        :py:class:`emonitor.modules.alarms.alarmhistory.AlarmHistory`

        :param name: name of event
        :param value: value of history entry
        :param optional dtime: timestamp of history entry (now)
        """
        if not dtime:
            dtime = datetime.datetime.now()
        self.history.append(AlarmHistory(name, value, dtime))

    def getAdditionalLayers(self):
        """
        Get additional layers of default map definition of current alarm

        :return: list of :py:class:`emonitor.modules.mapitems.mapitem.MapItem` objects
        """
        cat = self.key.category
        items = []
        for itemtype in self.getMap().getMapItemDefinitions():
            for r in itemtype['key']:
                regex = re.compile(r)
                if regex.search(cat):
                    items.append(itemtype)
        return items

    def updateSchedules(self, reference=0):
        """
        set scheduler events for current alarm:

        * autoclose
        * autoarchive

        :param reference: 0 (default)= time.time()
                          1 = alarm.timestamp
        """
        for job in scheduler.get_jobs():  # remove schedules of current alarm
            if job.name.startswith('alarms_') and job.name.endswith('_{}'.format(self.id)):
                scheduler.remove_job(job.id)

        if reference == 0:
            reference = time.time()
        else:
            reference = time.mktime(self.timestamp.timetuple())

        # test autoclose
        if self.state == 1 and self.type == 1 and Settings.get('alarms.autoclose', '0') != '0':  # only for open alarms
            closingtime = reference + float(Settings.get('alarms.autoclose', 30)) * 60.0  # minutes -> seconds
            if closingtime > time.time():  # close alarm in future
                logger.debug("add close schedule in future for alarmid {}".format(self.id))
                scheduler.add_job(self.changeState, run_date=datetime.datetime.fromtimestamp(closingtime), args=[self.id, 2], name="alarms_close_{}".format(self.id))
            else:  # close alarm now
                logger.debug("add close schedule now for alarmid {}".format(self.id))
                scheduler.add_job(self.changeState, args=[self.id, 2], name="alarms_close_{}".format(self.id))
                self.state = 2

        # test autoarchive
        if self.state == 2 and Settings.get('alarms.autoarchive', '0') != '0':  # only closed alarms
            archivetime = reference + float(Settings.get('alarms.autoarchive', 12)) * 3600.0  # hours -> seconds
            if archivetime > time.time():  # archive alarm in future
                logger.debug("add archive schedule in future for alarmid {}".format(self.id))
                scheduler.add_job(self.changeState, run_date=datetime.datetime.fromtimestamp(archivetime), args=[self.id, 3], name="alarms_archive_{}".format(self.id))
            else:  # archive alarm now
                logger.debug("add archive schedule now for alarmid {}".format(self.id))
                scheduler.add_job(self.changeState, args=[self.id, 3], name="alarms_archive_{}".format(self.id))

    def getDepartment(self):
        if self.street.city:
            return Department.getDepartments(id=self.street.city.dept)
        else:
            Department.getDefaultDepartment()

    def getAlarmFields(self):
        if self.street.city:
            fields = AlarmField.getAlarmFields(dept=self.street.city.dept)
        else:
            fields = AlarmField.getAlarmFields(dept=Department.getDefaultDepartment().id)
        return fields

    def getFieldValue(self, field):
        value = field
        if '-' in field:
            value = AlarmField.getAlarmFields(fieldtype=field.split('-')[0]).getFieldValue(field.split('-')[1], self)
        elif field.startswith('basic.'):
            value = AFBasic().getFieldValue(field, self)
        elif field.startswith('alarm.'):
            if field == 'alarm.key':
                if self.key.id:
                    return "{}: {}".format(self.key.category, self.key.key)
                return self.key.key
            elif field == 'alarm.date':
                return self.timestamp.strftime("%d.%m.%Y")
            elif field == 'alarm.time':
                return self.timestamp.strftime("%H:%M")
        else:
            value = field
        return value

    @staticmethod
    def getMap():
        """
        Returns default map defined in eMonitor

        :return: :py:class:`emonitor.modules.maps.map.Map`
        """
        return Map.getDefaultMap()

    @staticmethod
    def getAlarms(id=0, days=0, state=-1):
        """
        Get list of alarm objects filtered by parameters

        :param optional id: id of alarm or 0 for all alarms
        :param optional days: number of days since alarmdate
        :param optional state: -1 for alarms of all states, see :py:attr:`emonitor.modules.alarms.alarm.Alarm.ALARMSTATES` for value definition
        :return: list or single object :py:class:`emonitor.modules.alarms.alarm.Alarm`
        """
        if id != 0:
            return Alarm.query.filter_by(id=id).first()
        elif days != 0:  # filter last days, 0 = all days
            if int(state) == -1:
                return Alarm.query.filter(Alarm.timestamp > (datetime.datetime.now() - datetime.timedelta(days=days))).order_by(Alarm.timestamp.desc()).all()
            else:
                return Alarm.query.filter(Alarm.timestamp > (datetime.datetime.now() - datetime.timedelta(days=days)), Alarm.state == state).order_by(Alarm.timestamp.desc()).all()
        else:
            if int(state) == -1:  # all states
                return Alarm.query.order_by(Alarm.timestamp.desc()).all()
            else:
                return Alarm.query.filter(Alarm.state == state).order_by(Alarm.timestamp.desc()).all()

    @staticmethod
    def getAlarmCount(days=0):
        """
        Get number of alarms, grouped by state

        :param optional days: 0 for all alarms, since days else
        :return: list grouped by state
        """
        if days != 0:
            return db.get(Alarm.state, count(Alarm.id)).filter(Alarm.timestamp > (datetime.datetime.now() - datetime.timedelta(days=days))).order_by(Alarm.timestamp.desc()).group_by(Alarm.state).all()
        else:
            return db.get(Alarm.state, count(Alarm.id)).group_by(Alarm.state).all()

    @staticmethod
    def getActiveAlarms():
        """
        Get list of all active alarms

        :return: list or :py:class:`emonitor.modules.alarms.alarm.Alarm`
        """
        from sqlalchemy.exc import OperationalError
        try:
            return Alarm.query.filter_by(state=1).order_by(Alarm.timestamp.desc()).all()
        except OperationalError:
            return []

    @staticmethod
    def changeStates(state):
        """
        Set states of ALL alarms to given state

        :param state: state as :py:attr:`emonitor.modules.alarms.alarm.Alarm.ALARMSTATES`
        """
        for alarm in Alarm.getAlarms(0):
            Alarm.changeState(alarm.id, state)

    def getRouting(self):
        if self.get('routing', '') == "":  # load from webservice if not stored
            routingdata = alarmutils.getAlarmRoute(self)
            if len(routingdata['coordinates']) > 0:
                self.set('routing', yaml.safe_dump(routingdata, encoding="UTF-8"))
                db.session.commit()
        data = yaml.load(self.get('routing'))
        if 'error' in data:
            data['errormessage'] = babel.gettext(u'alarms.routingerror')
        return data

    @staticmethod
    def changeState(id, state):
        """
        Change state of alarm with given id. Adds entry in alarmhistory and sends signal

        :param id: id of alarm
        :param state: new state as :py:attr:`emonitor.modules.alarms.alarm.Alarm.ALARMSTATES`
        """
        from emonitor.extensions import monitorserver
        global LASTALARM
        alarm = Alarm.getAlarms(id=id)
        if not alarm:
            return []

        if alarm.state != state:  # only change
            _op = 'changestate'
        else:
            _op = 'added'

        if alarm.get('alarmtype', '') != '':
            _type = '.{}'.format(alarm.get('alarmtype'))
        else:
            _type = ''

        alarm.state = state
        try:
            alarm.addHistory('autochangeState', Alarm.ALARMSTATES[str(state)])
        except KeyError:
            alarm.addHistory('autochangeState', 'archived')
        db.session.commit()

        if state == 1:  # activate alarm
            c = []
            for a in Alarm.getActiveAlarms():  # check cars
                if a.id == id:
                    continue
                c.extend(set(a.cars1).intersection(set(alarm.cars1)))
                c.extend(set(a.cars2).intersection(set(alarm.cars2)))
                c.extend(set(a.material).intersection(set(alarm.material)))

            if time.time() - LASTALARM < 60.0:
                try:
                    ids = [a.id for a in Alarm.getActiveAlarms()]
                    for j in [job for job in scheduler.get_jobs() if job.name == 'changeLayout']:
                        for i in ids:
                            if "'alarmid', %s" % i in str(j.args):  # layout changes for given alarm
                                scheduler.unschedule_job(j)
                except:
                    logger.error('%s' % [a.id for a in Alarm.getActiveAlarms()])
            LASTALARM = time.time()
            alarm.updateSchedules(reference=0)  # use current time + delta
            j = scheduler.add_job(events.raiseEvent, next_run_time=datetime.datetime.fromtimestamp(LASTALARM), args=['alarm_{}{}'.format(_op, _type)], kwargs={'alarmid': id}, name="alarms_activate_{}".format(id))
            signal.send('alarm', 'added', alarmid=id)
            try:
                flash(babel.gettext(u'alarms.statechangeactivated'), 'alarms.activate')
            except:
                pass
            finally:
                monitorserver.sendMessage('0', 'reset')  # refresh monitor layout
                #signal.send('alarm', 'changestate', newstate=1)
                return list(set(c))

        elif state == 2:  # close alarm
            LASTALARM = 0.0
            alarm.updateSchedules(reference=1)  # use alarm.timestamp + delta
            monitorserver.sendMessage('0', 'reset')  # refresh monitor layout
            signal.send('alarm', 'changestate', newstate=2)
            return []

        elif state == 3:  # archive alarm
            alarm.updateSchedules()
            signal.send('alarm', 'changestate', newstate=3)
            return []

        signal.send('alarm', 'changestate', newstate=state)

    @staticmethod
    def getExportData(exportformat, **params):
        """
        Export alarm to given format

        :param exportformat: *.html*, *.png*
        :param params:
          - style: exportstyle: *alarmmap*, *routemap*

          - filename: name of exportfile

        :return: alarm in correct format
        """
        if params['id'] and params:
            alarm = Alarm.getAlarms(id=params['id'])
            logger.debug('load export data for alarm {}, style {}, exportformat {}'.format(params['id'], params['style'], exportformat))
            if not alarm:  # create dummy alarm
                alarm = Alarm(datetime.datetime.now(), '', 2, 0)
                alarm.position = dict(lat=Settings.get('defaultLat'), lng=Settings.get('defaultLng'))
                alarm.set('id.key', '1')
                alarm.set('id.address', '1')
                alarm.set('id.city', '1')
                alarm.set('remark', 'TEST TEST TEST')
            if alarm:
                if exportformat == '.html' and 'style' in params:  # build html-template
                    params.update({'alarm': alarm})
                    try:
                        if params['style'].startswith(u'report'):
                            return render_template('{}.html'.format(params['style']), **params)
                        else:
                            return render_template('print.{}.html'.format(params['style']), **params)
                    except TemplateNotFound:
                        logger.error('template {}{} not found'.format(params['style'], exportformat))
                        return abort(404)

                elif exportformat == '.png':  # send image file

                    if params['style'].startswith('alarmmap'):  # deliver map for alarmid
                        from emonitor.modules.maps.map_utils import getAlarmMap
                        args = dict()
                        if params['style'] != 'alarmmap':
                            args = dict(style=params['style'].split('_')[-1])
                        return getAlarmMap(alarm, current_app.config.get('PATH_TILES'), **args)

                    elif params['style'] == 'routemap':  # deliver map with route
                        from emonitor.modules.maps.map_utils import getAlarmRoute
                        return getAlarmRoute(alarm, current_app.config.get('PATH_TILES'))

                    if 'filename' in params and os.path.exists("%s/inc/%s.png" % (os.path.abspath(os.path.dirname(__file__)), params['filename'])):
                        with open("%s/inc/%s.png" % (os.path.abspath(os.path.dirname(__file__)), params['filename']), 'rb') as f:
                            return f.read()
        abort(404)

    @staticmethod
    def handleEvent(eventname, **kwargs):
        """
        Eventhandler for alarm class

        :param eventname: name of event
        :param kwargs: parameter list: error, fields, filename, id, incomepath, mode, time
        :return: all kwargs
        """
        from emonitor import app
        global LASTALARM

        alarm_fields = dict()
        stime = time.time()
        alarmtype = None
        for t in AlarmType.getAlarmTypes():
            #if re.search(t.keywords.replace('\r\n', '|'), unicode(kwargs['text'], errors='ignore')):
            if re.search(t.keywords.replace('\r\n', '|'), kwargs['text']):
                alarm_fields = t.interpreterclass().buildAlarmFromText(t, kwargs['text'])
                if u'error' in alarm_fields.keys():
                    kwargs['error'] = alarm_fields['error']
                    del alarm_fields['error']
                alarmtype = t
                break

        # copy file -> original name
        if 'time' in alarm_fields and alarm_fields['time'][1] == 1:  # found correct time
            t = datetime.datetime.strptime(alarm_fields['time'][0], '%d.%m.%Y - %H:%M:%S')
        else:
            t = datetime.datetime.now()

        if not os.path.exists('{}{}'.format(app.config.get('PATH_DONE'), t.strftime('%Y/%m/'))):
            os.makedirs('{}{}'.format(app.config.get('PATH_DONE'), t.strftime('%Y/%m/')))

        try:
            shutil.copy2('{}{}'.format(kwargs['incomepath'], kwargs['filename']), '{}{}{}'.format(app.config.get('PATH_DONE'), t.strftime('%Y/%m/%Y%m%d-%H%M%S'), os.path.splitext(kwargs['filename'])[1]))
        except:
            pass
        try:  # remove file
            os.remove('{}{}'.format(kwargs['incomepath'], kwargs['filename']))
        except:
            pass
        kwargs['filename'] = '{}{}'.format(t.strftime('%Y/%m/%Y%m%d-%H%M%S'), os.path.splitext(kwargs['filename'])[1])
        logger.debug('alarm_fields: {}'.format(alarm_fields))

        if len(alarm_fields) == 0:  # no alarmfields found
            kwargs['id'] = 0
            logger.error('no alarm fields found.')
            return kwargs

        kwargs['fields'] = ''
        for k in alarm_fields:
            kwargs['fields'] = u'{}\n-{}:\n  {}'.format(kwargs['fields'], k, alarm_fields[k])

        if not alarmtype:  # alarmtype not found
            kwargs['id'] = 0
            kwargs['error'] = 'alarmtype not found'
            logger.error('alarmtype not found.')
            return kwargs

        # position
        _position = dict(lat=u'0.0', lng=u'0.0')
        if USE_NOMINATIM == 1:
            try:
                url = 'http://nominatim.openstreetmap.org/search'
                params = 'format=json&city={}&street={}'.format(alarm_fields['city'][0], alarm_fields['address'][0])
                if 'streetno' in alarm_fields:
                    params += ' {}'.format(alarm_fields['streetno'][0].split()[0])  # only first value
                r = requests.get('{}?{}'.format(url, params))
                _position = dict(lat=r.json()[0]['lat'], lng=r.json()[0]['lon'])
            except:
                pass

        # create alarm object
        if 'key' not in alarm_fields.keys() or alarm_fields['key'][0] == u'':
            if alarmtype.translation(u'_bma_main_') in alarm_fields['remark'][0] or alarmtype.translation(u'_bma_main_') in alarm_fields['person'][0]:
                alarmkey = Alarmkey.query.filter(Alarmkey.key.like(u"%{}%".format(alarmtype.translation(u'_bma_')))).all()
                if len(alarmkey) > 0:
                    alarm_fields['key'] = ('{}: {}'.format(alarmkey[0].category, alarmkey[0].key), str(alarmkey[0].id))
                else:
                    alarm_fields['key'] = (alarmtype.translation(u'_bma_key_'), u'0')

        if 'time' in alarm_fields and alarm_fields['time'][1] == 1:  # found correct time
            t = datetime.datetime.strptime(alarm_fields['time'][0], '%d.%m.%Y - %H:%M:%S')
        else:
            t = datetime.datetime.now()

        alarm = Alarm(t, alarm_fields['key'][0], 1, 0)
        alarm.set('id.key', alarm_fields['key'][1])
        alarm.material = dict(cars1='', cars2='', material='')  # set required attributes
        alarm.set('marker', '0')
        alarm.set('filename', kwargs['filename'])
        alarm.set('priority', '1')  # set normal priority
        alarm.set('alarmtype', alarmtype.name)  # set checker name
        alarm.state = 1

        # city
        if 'city' in alarm_fields and alarm_fields['city'][1] != 0:
            alarm.city = City.getCities(id=alarm_fields['city'][1])
            if alarm_fields['address'][1] != 0:
                alarm.street = Street.getStreets(id=alarm_fields['address'][1])
        else:  # city not found -> build from fax
            url = 'http://nominatim.openstreetmap.org/search'
            params = u'format=json&city={}&street={}'.format(alarm_fields['city'][0].split()[0], alarm_fields['address'][0])
            if 'streetno' in alarm_fields and alarm_fields['streetno'][0]:
                params += u' {}'.format(alarm_fields['streetno'][0].split()[0])  # only first value
                alarm.set('streetno', alarm_fields['streetno'][0])

            r = requests.get(u'{}?{}'.format(url, params))
            logger.debug('load address data from nomination with parameters: city=%s street=%s' % (alarm_fields['city'][0].split()[0], alarm_fields['address'][0]))
            try:
                _position = dict(lat=r.json()[0]['lat'], lng=r.json()[0]['lon'])
                alarm.position = _position
            except:
                pass

            alarm.set('city', alarm_fields['city'][0].split()[0])
            alarm.set('id.city', alarm_fields['city'][1])
            alarm.set('address', alarm_fields['address'][0])
            if alarm_fields['address'][1] != 0:
                alarm.street = Street.getStreets(id=alarm_fields['address'][1])

            if 'cars' in alarm_fields:  # add cars found in material
                for _c in alarm_fields['cars'][1].split(';'):
                    alarm.set('k.cars1', alarm.get('k.cars1') + ';' + _c)

        # street / street2
        if 'address' in alarm_fields and alarm_fields['address'][0] != '':
            # check correct city -> change if street has different city
            if len(str(alarm_fields['address'][1]).split(';')) > 0 and alarm_fields['address'][1] != 0:
                _c = []

                for s in str(alarm_fields['address'][1]).split(';'):
                    _s = Street.getStreets(id=s)
                    if _s.cityid and _s.cityid not in _c and _s.cityid == alarm_fields['city'][1]:
                        _c.append(_s.cityid)
                        alarm.street = _s
                        if 'object' in alarm_fields and str(alarm_fields['object'][1]) == '0':
                            if 'lat' not in alarm_fields and 'lng' not in alarm_fields:
                                alarm.position = dict(lat=_s.lat, lng=_s.lng, zoom=_s.zoom)
                                if _position['lat'] != u'0.0' and _position['lng'] != u'0.0':  # set marker if nominatim delivers result
                                    alarm.position = _position
                                    alarm.set('marker', '1')
            else:  # add unknown street
                alarm.set('id.address', 0)
                alarm.set('address', alarm_fields['address'][0])
        # houseno
        if 'streetno' in alarm_fields.keys():
            alarm.set('streetno', alarm_fields['streetno'][0])
            if 'id.streetno' in alarm_fields and 'lat' in alarm_fields and 'lng' in alarm_fields:
                alarm.position = dict(lat=alarm_fields['lat'][0], lng=alarm_fields['lng'][0])
                alarm.set('id.streetno', alarm_fields['id.streetno'][1])
            else:
                # new
                hn = alarm.street.getHouseNumber(name=alarm_fields['streetno'][0])
                if hn:
                    alarm.position = hn.getPosition(0)
            if 'zoom' in alarm_fields.keys():
                alarm.set('zoom', alarm_fields['zoom'][0])

        # crossing
        if 'crossing' in alarm_fields and alarm_fields['crossing'][0] != '':
            if 'crossing' in alarm_fields and alarm_fields['address'][1] != alarm_fields['crossing'][1]:
                alarm.set('id.address2', alarm_fields['crossing'][1])
                alarm.set('address2', alarm_fields['crossing'][0])
            else:
                alarm.set('id.address2', '0')
                alarm.set('address2', alarm_fields['crossing'][0])

        # addresspart
        if 'addresspart' in alarm_fields and alarm_fields['addresspart'][0] != '' and alarm_fields['addresspart'][0] != alarm_fields['address'][0]:
            if alarm_fields['addresspart'][1] > 0:
                if len(str(alarm_fields['addresspart'][1]).split(';')) > 0:
                    _c = []

                    for s in str(alarm_fields['addresspart'][1]).split(';'):
                        try:
                            _s = Street.getStreets(id=s)
                            if _s.cityid not in _c and _s.cityid == alarm_fields['city'][1]:
                                _c.append(_s.cityid)
                                alarm.set('id.address2', _s.id)
                        except:
                            pass
                else:
                    alarm.set('id.address2', alarm_fields['addresspart'][1])
            else:
                alarm.set('id.address2', '0')
            alarm.set('address2', alarm_fields['addresspart'][0])

        # person
        if 'person' in alarm_fields and alarm_fields['person'][0] != '':
            alarm.set('person', alarm_fields['person'][0])
        # alarmplan
        if 'alarmplan' in alarm_fields and alarm_fields['alarmplan'][0] != '':
            alarm.set('alarmplan', alarm_fields['alarmplan'][0])

        # alarmobject
        _ao = None
        if 'object' in alarm_fields and alarm_fields['object'][0] != '' and 'city' in alarm_fields and alarm_fields['city'][1] > 0:
            alarm.set('object', alarm_fields['object'][0])
            alarm.set('id.object', alarm_fields['object'][1])
            # alarmplan from object
            if alarm_fields['object'][1] != 0:
                _ao = AlarmObject.getAlarmObjects(id=alarm_fields['object'][1])

            if _ao:
                if _ao.alarmplan != 0:
                    alarm.set('alarmplan', _ao.alarmplan)
                if _ao.street.id != alarm_fields['address'][1]:  # street config from alarmobject
                    alarm.street = Street.getStreets(id=_ao.street.id)
                    if _ao.streetno == "":
                        alarm.set('streetno', alarm_fields['streetno'][0])
                    else:
                        alarm.set('streetno', _ao.streetno)
                alarm.position = dict(lat=_ao.lat, lng=_ao.lng, zoom=_ao.zoom)

        # remark
        if 'remark' in alarm_fields and alarm_fields['remark'][0] != '':
            alarm.set('remark', alarm_fields['remark'][0])
            if alarmtype.translation(u'_bma_main_') in alarm_fields['remark'][0] or alarmtype.translation(u'_bma_main_') in alarm_fields['person'][0]:
                alarmkey = Alarmkey.query.filter(Alarmkey.key.like(u"%{}%".format(alarmtype.translation(u'_bma_')))).first()
                if alarmkey:
                    alarm.set('id.key', alarmkey.id)
                    alarm._key = u'{}: {}'.format(alarmkey.category, alarmkey.key)
                else:
                    alarm.set('id.key', '0')
                    alarm._key = alarmtype.translation(u'_bma_key_')
        # additional remarks
        if 'remark2' in alarm_fields and alarm_fields['remark2'][0] != '':
            alarm.set('remark', u'%s\n%s' % (alarm.get('remark'), alarm_fields['remark2'][0]))

        # material
        if alarm.get('id.key') != 0 and 'city' in alarm_fields:  # found key with aao
            if alarm_fields['city'][1] != 0:  # default city
                if Department.getDepartments(id=alarm.city.dept).defaultcity == alarm_fields['city'][1]:  # default city for dep
                    if 'material' in alarm_fields:
                        if str(alarm_fields['material'][1])[0] == '0':  # default cars for aao
                            try:
                                alarm.material = dict(cars1=u','.join([str(c.id) for c in alarm.key.getCars1(alarm.street.city.dept)]), cars2=u','.join([str(c.id) for c in alarm.key.getCars2(alarm.street.city.dept)]), material=u','.join([str(c.id) for c in alarm.key.getMaterial(alarm.street.city.dept)]))
                            except AttributeError:
                                alarm.material = dict(cars1=u','.join([str(c.id) for c in alarm.key.getCars1(alarm.city.dept)]), cars2=u','.join([str(c.id) for c in alarm.key.getCars2(alarm.city.dept)]), material=u','.join([str(c.id) for c in alarm.key.getMaterial(alarm.city.dept)]))

                        for _c in u'{}'.format(alarm_fields['material'][1]).split(','):  # add additional cars
                            if _c != '0' and _c not in alarm.get('k.cars1').split(','):
                                alarm.set('k.cars1', u'{},{}'.format(alarm.get('k.cars1'), _c))

                else:  # only alarmed material
                    alarm.material = dict(cars1=alarm_fields['material'][1])

            else:  # else city
                if alarm_fields['material'][1] == u'0':  # default cars for aao
                    alarm.material = dict(cars1=u','.join([str(c.id) for c in alarm.key.getCars1(alarm.city.dept)]), cars2=u','.join([str(c.id) for c in alarm.key.getCars2(alarm.city.dept)]), material=u','.join([str(c.id) for c in alarm.key.getMaterial(alarm.city.dept)]))
                else:
                    alarm.material = dict(cars1=u','.join(list(OrderedDict.fromkeys(filter(lambda x: x != '0', str(alarm_fields['material'][1]).split(','))))))

        else:  # default aao of current department (without aao)
            if alarm_fields['city'][1] != 0:  # found city -> use default aao
                c = City.getCities(id=alarm_fields['city'][1]).dept
                akc = Alarmkey.getDefault(c)
                alarm.material = dict(cars1=u','.join([str(c.id) for c in akc.cars1]), cars2=u",".join([str(c.id) for c in akc.cars2]), material=u",".join([str(c.id) for c in akc.materials]))

            l = (u'%s,%s,%s' % (alarm.get('k.cars1'), alarm.get('k.cars2'), alarm.get('k.material'))).split(',')
            if len(set(str(alarm_fields['material'][1]).split(',')).intersection(set(l))) == 0:
                _dep = Department.getDefaultDepartment()
                for c in alarm_fields['material'][1].split(','):
                    if c == u'0':  # default of home department needed
                        alarm.material = dict(cars1=u','.join([str(c.id) for c in alarm.key.getCars1(_dep.id)]), cars2=u",".join([str(c.id) for c in alarm.key.getCars2(_dep.id)]), material=u",".join([str(c.id) for c in alarm.key.getMaterial(_dep.id)]))
                        break
                if u'0' not in alarm_fields['material'][1]:  # only single car needed
                    alarm.set('k.cars1', u'{},{}'.format(alarm_fields['material'][1], alarm.get('k.cars1')))

        if _ao and _ao.hasOwnAAO():  # use aao of current object
            alarm.material = dict(cars1=u",".join([str(c.id) for c in _ao.getCars1()]), cars2=u",".join([str(c.id) for c in _ao.getCars2()]), material=u",".join([str(c.id) for c in _ao.getMaterial()]))

        if 'time' not in kwargs.keys():
            kwargs['time'] = []
        etime = time.time()
        kwargs['time'].append('alarm creation done in %s sec.' % (etime - stime))

        if kwargs['mode'] != 'test':
            db.session.add(alarm)
            db.session.commit()
            signal.send('alarm', 'added', alarmid=alarm.id)
            Alarm.changeState(alarm.id, 1)  # activate alarm
            logger.info('alarm created with id %s (%s)' % (alarm.id, (etime - stime)))
        else:
            kwargs['fields'] += '\n\n--------------------------\nALARM-Object\n'
            _cdict = Car.getCarsDict()
            for a in alarm.attributes:
                try:
                    if a in ['k.cars1', 'k.cars2', 'k.material']:
                        kwargs['fields'] += '\n-%s:\n  %s -> %s' % (a, alarm.get(a), ", ".join([_cdict[int(_c)].name for _c in alarm.get(a).split(',') if _c not in ['', '0']]))
                    elif a in 'id.key':
                        _k = Alarmkey.getAlarmkeys(id=alarm.get(a))
                        kwargs['fields'] += '\n-%s:\n  %s -> %s: %s' % (a, alarm.get(a), _k.category, _k.key)
                    elif a == 'id.address':
                        kwargs['fields'] += '\n-%s:\n  %s -> %s' % (a, alarm.get(a), Street.getStreets(id=alarm.get(a)).name)
                    else:
                        kwargs['fields'] += '\n-%s:\n  %s' % (a, alarm.get(a))
                except (AttributeError, KeyError):
                    kwargs['fields'] += '\n-%s:\n  %s (error)' % (a, alarm.get(a))
            kwargs['id'] = '-0'  # add dummy id
            db.session.rollback()
            logger.info('alarm created in TESTMODE (%s)' % (etime - stime))
        return kwargs

        #if alarm:
        #    kwargs[0]['id'] = alarm.id
        #else:
        #    kwargs[0]['id'] = 0
        #return kwargs

    def getReportField(self, fieldname):
        afield = AlarmField.getAlarmFields(name=fieldname)
        print afield

