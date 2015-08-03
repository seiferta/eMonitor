import datetime
import os
import shutil
import StringIO
from collections import Counter
from operator import attrgetter
from flask import current_app, render_template, request, flash, session, render_template_string, jsonify, redirect, make_response
from emonitor.extensions import scheduler, db, signal
from emonitor.modules.alarms.alarm import Alarm
from emonitor.modules.alarms.alarmhistory import AlarmHistory
from emonitor.modules.alarms.alarmfield import AlarmField
from emonitor.modules.alarmobjects.alarmobject import AlarmObject
from emonitor.modules.alarms.alarmreport import AlarmReport
from emonitor.modules.streets.city import City
from emonitor.modules.streets.street import Street
from emonitor.modules.cars.car import Car
from emonitor.modules.settings.settings import Settings
from emonitor.modules.settings.department import Department
from emonitor.modules.printers.printers import Printers
from emonitor.modules.monitors.monitor import Monitor
from emonitor.modules.monitors.monitorlayout import MonitorLayout
from emonitor.frontend.frontend import frontend


def getFrontendContent(**params):
    """
    Deliver frontend content of module alarms

    :return: data of alarms
    """
    from emonitor.extensions import monitorserver

    if 'alarmfilter' not in session:
        session['alarmfilter'] = '7'
    if request.args.get('alarmfilter'):  # filter for alarms last x days, -1 no filter set
        session['alarmfilter'] = request.args.get('alarmfilter', '7')

    if 'area' in request.args:
        params['area'] = request.args.get('area')
    if 'state' in request.args:
        params['activeacc'] = request.args.get('state')

    if request.form.get('action') == 'updatealarm':
        if request.form.get('alarm_id') != 'None':  # update alarm
            alarm = Alarm.getAlarms(request.form.get('alarm_id'))
        else:  # create new alarm
            d = datetime.datetime.strptime('%s %s' % (request.form.get('edit_timestamp_date'), request.form.get('edit_timestamp_time')), "%d.%m.%Y %H:%M:%S")
            alarm = Alarm(d, request.form.get('edit_keyid'), 2, 0)
            db.session.add(alarm)
            params['activeacc'] = 1
        try:
            alarm.timestamp = datetime.datetime.strptime('%s %s' % (request.form.get('edit_timestamp_date'), request.form.get('edit_timestamp_time')), "%d.%m.%Y %H:%M:%S")
        except ValueError:
            alarm.timestamp = datetime.datetime.now()
        alarm._key = request.form.get('edit_key')

        alarm.set(u'id.key', request.form.get('edit_keyid'))
        alarm.set(u'k.cars1', request.form.get('val_cars1'))
        alarm.set(u'k.cars2', request.form.get('val_cars2'))
        alarm.set(u'k.material', request.form.get('val_material'))

        alarm.set(u'marker', request.form.get('marker'))
        alarm.set(u'id.city', request.form.get('edit_city'))
        _city = City.getCities(id=request.form.get('edit_cityname'))
        if _city:
            alarm.set(u'city', _city.name)
        else:
            alarm.set(u'city', request.form.get('edit_cityname'))

        alarm.set(u'streetno', request.form.get('edit_streetno'))
        street = Street.getStreets(id=request.form.get('edit_addressid'))
        hnumber = None
        if street:
            alarm.set(u'id.address', street.id)
            try:
                hnumber = [h for h in street.housenumbers if h.number == request.form.get('edit_streetno').split()[0]]
                if len(hnumber) > 0:
                    alarm.set(u'lat', hnumber[0].points[0][0])
                    alarm.set(u'lng', hnumber[0].points[0][1])
            except IndexError:
                pass
        elif request.form.get('edit_addressid') == 'None':
            alarm.set(u'id.address', '')
        else:
            alarm.set(u'id.address', request.form.get('edit_addressid'))
        alarm.set(u'address', request.form.get('edit_address'))
        alarm.set(u'id.object', request.form.get('edit_object'))
        alarm.set(u'priority', request.form.get('edit_priority'))
        alarm.set(u'remark', request.form.get('edit_remark'))
        alarm.set(u'person', request.form.get('edit_person'))

        if request.form.get(u'edit_address2').strip() != '':
            alarm.set(u'address2', request.form.get('edit_address2'))

        if (request.form.get(u'marker') == '1' and not hnumber) or request.form.get('update_position') == '1':
            alarm.set(u'routing', '')
            alarm.set(u'lat', request.form.get('lat'))
            alarm.set(u'lng', request.form.get('lng'))
            alarm.set(u'zoom', request.form.get('zoom'))
        try:
            d = datetime.datetime.strptime('%s %s' % (request.form.get('edit_endtimestamp_date'), request.form.get('edit_endtimestamp_time')), "%d.%m.%Y %H:%M:%S")
        except ValueError:
            d = datetime.datetime.now()
        alarm.set(u'endtimestamp', d)
        db.session.commit()
        signal.send('alarm', 'updated', alarmid=alarm.id)
        if request.form.get('alarm_id') == u'None':  # create new
            Alarm.changeState(alarm.id, 0)  # prepare alarm
            return redirect('/alarms?area=%s&state=1' % params['area'])
        elif alarm.state == 1:  # active alarm update
            monitorserver.sendMessage('0', 'reset')  # refresh monitor layout
        return redirect('/alarms?area=%s&state=0' % params['area'])

    elif request.args.get('action') == 'editalarm':
        if request.args.get('alarmid', '0') == '0':  # add new alarm
            alarm = Alarm(datetime.datetime.now(), '', 2, 0)
            #flash(babel.gettext(u'alarms.alarmadded'), 'alarms.add')
        else:  # edit alarm
            alarm = Alarm.getAlarms(id=request.args.get('alarmid'))
        return render_template('frontend.alarms_edit.html', alarm=alarm, cities=City.getCities(), objects=AlarmObject.getAlarmObjects(), cars=Car.getCars(), departments=Department.getDepartments(), frontendarea=params['area'], frontendmodules=frontend.modules, frontendmoduledef=Settings.get('frontend.default'))

    elif request.args.get('action') == 'refresh':  # refresh alarm section
        params['area'] = request.args.get('area')
        params['activeacc'] = int(request.args.get('activeacc'))

    elif request.args.get('action') == 'finishalarm':  # finish selected alarm
        Alarm.changeState(int(request.args.get('alarmid')), 2)
        params['area'] = request.args.get('area')

    elif request.args.get('action') == 'activatealarm':  # activate selected alarm
        ret = Alarm.changeState(int(request.args.get('alarmid')), 1)
        if len(ret) > 0:
            flash(render_template_string("{{ _('alarms.carsinuse') }}</br><b>" + ", ".join([r.name for r in sorted(ret, key=attrgetter('name'))]) + "</b>"), 'alarms')
        params['area'] = request.args.get('area')
        params['activeacc'] = 0

    elif request.args.get('action') == 'deletealarm':  # delete selected alarm
        alarm = Alarm.getAlarms(id=request.args.get('alarmid'))
        refresh = 1 or alarm.state == 1  # check if alarm is active
        try:
            if os.path.exists("{}{}".format(current_app.config.get('PATH_DONE'), alarm.get('filename'))):
                os.remove("{}{}".format(current_app.config.get('PATH_DONE'), alarm.get('filename')))
        except:
            pass
        alarm.state = -1
        alarm.updateSchedules()
        db.session.delete(alarm)
        db.session.commit()
        if refresh:
            monitorserver.sendMessage('0', 'reset')  # refresh monitor layout
        signal.send('alarm', 'deleted', alarmid=request.args.get('alarmid'))

    elif request.args.get('action') == 'archivealarm':  # archive selected alarms, id=0 == all
        if ";" in request.args.get('alarmid'):  # archive selected alarms
            for alarmid in request.args.get('alarmid').split(';'):
                Alarm.changeState(int(alarmid), 3)
        elif int(request.args.get('alarmid')) == 0:  # archive all alarms
            Alarm.changeStates(3)
        else:  # archive single selected alarm
            Alarm.changeState(int(request.args.get('alarmid')), 3)
        params['area'] = request.args.get('area')

    stats = dict.fromkeys(Alarm.ALARMSTATES.keys() + ['3'], 0)
    for s, c in Alarm.getAlarmCount(days=int(session['alarmfilter'])):  # s=state, c=count(ids of state)
        if str(s) in stats.keys():
            stats[str(s)] = c

    if 'area' not in params:
        params['area'] = 'center'
    if 'activeacc' not in params:
        params['activeacc'] = 0
    return render_template('frontend.alarms_smallarea.html', alarmstates=Alarm.ALARMSTATES, stats=stats, frontendarea=params['area'], activeacc=str(params['activeacc']), printdefs=Printers.getActivePrintersOfModule('alarms'), frontendmodules=frontend.modules, frontendmoduledef=Settings.get('frontend.default'), alarmfilter=session['alarmfilter'])


def getFrontendData(self):
    """
    Deliver frontend content of module alarms (ajax)

    :return: rendered template as string or json dict
    """
    from emonitor.extensions import monitorserver

    if "download" in request.path:  # deliver file
        with open('{}{}'.format(current_app.config.get('PATH_TMP'), request.path.split('download/')[-1]), 'rb') as data:
            si = StringIO.StringIO(data.read()).getvalue()
            output = make_response(si)
        if request.path.split('/')[-1].startswith('temp'):  # remove if filename starts with temp == temporary file
            os.remove('{}{}'.format(current_app.config.get('PATH_TMP'), request.path.split('download/')[-1]))
        output.headers["Content-Disposition"] = "attachment; filename=report.{}".format(request.path.split('.')[-1])
        output.headers["Content-type"] = "application/x.download"
        return output

    if request.args.get('action') == 'editalarm':
        
        if request.args.get('alarmid', '0') == '0':  # add new alarm
            alarm = Alarm(datetime.datetime.now(), '', 2, 0)

        else:  # edit alarm
            alarm = Alarm.getAlarms(id=request.args.get('alarmid'))
        return render_template('frontend.alarms_edit.html', alarm=alarm, cities=City.getCities(), objects=AlarmObject.getAlarmObjects(), cars=Car.getCars(), frontendarea=request.args.get('frontendarea'))

    elif request.args.get('action') == 'alarmmonitor':  # send alarm to monitor
        for monitor in Monitor.getMonitors():
            scheduler.deleteJobForEvent('changeLayout')  # send update to monitors
            for l in MonitorLayout.getLayouts(mid=int(monitor.id)):
                if l.trigger == 'alarm_added':
                    #monitorserver.sendMessage(str(monitor.id), 'load', ['layoutid=%s' % l.id, 'alarmid=%s' % request.args.get('alarmid')])  TODO changed from list
                    monitorserver.sendMessage(str(monitor.id), 'load', layoutid=l.id, alarmid=request.args.get('alarmid'))

    elif request.args.get('action') == 'printalarm':
        Printers.getPrinters(pid=int(request.args.get('printerdef'))).doPrint(object=Alarm.getAlarms(id=int(request.args.get('alarmid'))), id=request.args.get('alarmid'), copies=1)
        return ""

    elif request.args.get('action') == 'routeinfo':
        return render_template('frontend.alarms_routing.html', routing=Alarm.getAlarms(id=request.args.get('alarmid')).getRouting())

    elif request.args.get('action') == 'routecoords':
        return jsonify(Alarm.getAlarms(id=request.args.get('alarmid')).getRouting())

    elif request.args.get('action') == 'message':
        return render_template('frontend.alarms_message.html', alarm=Alarm.getAlarms(id=request.args.get('alarmid')), messagestates=AlarmHistory.historytypes, area=request.args.get('area'), reload=request.args.get('reload', 'true'))

    elif request.args.get('action') == 'addmessage':  # add message
        if request.form.get('messagetext') != "":
            alarm = Alarm.getAlarms(request.form.get('alarmid'))
            alarm.addHistory(request.form.get('messagestate'), request.form.get('messagetext'))
            db.session.commit()
        return render_template('frontend.alarms_message.html', alarm=Alarm.getAlarms(request.form.get('alarmid')), messagestates=AlarmHistory.historytypes, area=request.args.get('area'))

    elif request.args.get('action') == 'deletemessage':  # delete selected message
        alarm = Alarm.getAlarms(request.args.get('alarmid'))
        for msg in alarm.history:
            if str(msg.timestamp) == request.args.get('datetime'):
                db.session.delete(msg)
        db.session.commit()
        return render_template('frontend.alarms_message.html', alarm=Alarm.getAlarms(request.args.get('alarmid')), messagestates=AlarmHistory.historytypes, area=request.args.get('area'))

    elif request.args.get('action') == 'housecoordinates':  # return a dict with coordinats of housenumber
        if request.args.get('alarmid') != "None":
            alarm = Alarm.getAlarms(id=int(request.args.get('alarmid')))
            if alarm and alarm.housenumber:
                return {'lat': map(lambda x: x[0], alarm.housenumber.points), 'lng': map(lambda x: x[1], alarm.housenumber.points)}
        return []

    elif request.args.get('action') == 'evalhouse':  # try to eval housenumer
        street = Street.getStreets(id=request.args.get('streetid'))
        if street:
            points = dict(lat=[], lng=[])
            for hn in street.housenumbers:
                if str(hn.number) == request.args.get('housenumber').strip():
                    points['lat'].extend(map(lambda x: x[0], hn.points))
                    points['lng'].extend(map(lambda x: x[1], hn.points))
            return points
        return {}

    elif request.args.get('action') == 'alarmsforstate':  # render alarms for given state
        if 'alarmfilter' not in session:
            session['alarmfilter'] = 7
        return render_template('frontend.alarms_alarm.html', alarms=Alarm.getAlarms(days=int(session['alarmfilter']), state=int(request.args.get('state', '-1'))), printdefs=Printers.getActivePrintersOfModule('alarms'))

    elif request.args.get('action') == 'collective':  # render collective form
        reports = [r for r in AlarmReport.getReports() if r.reporttype.multi]
        if len(reports) == 0:
            return ""
        return render_template('frontend.alarms_collective.html', alarms=Alarm.getAlarms(state=2), reports=reports)

    elif request.args.get('action') == 'docollective':  # build collective form
        if request.args.get('ids') == "":
            ids = []
        else:
            ids = request.args.get('ids').split(',')
        f = AlarmReport.getReports(request.args.get('form')).createReport(ids=ids)
        _path, _filename = os.path.split(f)
        shutil.move(f, "{}{}".format(current_app.config.get('PATH_TMP'), _filename))
        return _filename

    elif request.args.get('action') == 'alarmpriocars':  # show prio cars
        cars = []
        c = Settings.getIntList('alarms.spc_cars.{}'.format(request.args.get('state')))
        if len(c) == 0:
            return ""
        for alarm in Alarm.getAlarms(state=request.args.get('state')):
            cars.extend([car for car in alarm.cars1 if car.id in c])
        cars = Counter(cars)
        return render_template('frontend.alarms_cars.html', cars=cars)

    elif request.args.get('action') == 'showdetailsform':  # build alarmdetails edtit form
        alarm = Alarm.getAlarms(id=request.args.get('alarmid'))
        if alarm.street.city:
            fields = AlarmField.getAlarmFields(dept=alarm.street.city.dept)
        else:
            fields = AlarmField.getAlarmFields(dept=Department.getDefaultDepartment().id)
        return render_template('frontend.alarms_fields.html', alarm=alarm, fields=fields, reports=AlarmReport.getReports())

    elif request.args.get('action') == 'saveextform':  # store ext-form values
        alarm = Alarm.getAlarms(id=request.form.get('alarmid'))
        for field in AlarmField.getAlarmFields(dept=alarm.street.city.dept):
            field.saveForm(request, alarm)
        db.session.commit()

    return ""
