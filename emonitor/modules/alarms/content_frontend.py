import datetime
from operator import attrgetter
from flask import render_template, request, flash, session, render_template_string, jsonify
from emonitor.extensions import classes, monitorserver, scheduler, db, signal
from emonitor.frontend import frontend


def getFrontendContent(**params):
    alarmstates = classes.get('alarm').ALARMSTATES

    if request.args.get('alarmfilter', '-1') != '-1':  # filter for alarms last x days, -1 no filter set
        session['alarmfilter'] = request.args.get('alarmfilter', '-1')
    elif 'alarmfilter' not in session:
        session['alarmfilter'] = '0'

    if 'area' in request.args:
        params['area'] = request.args.get('area')
    if 'state' in request.args:
        params['activeacc'] = request.args.get('state')

    if request.form.get('action') == 'updatealarm':
        if request.form.get('alarm_id') != 'None':  # update alarm
            alarm = classes.get('alarm').getAlarms(request.form.get('alarm_id'))
        else:  # create new alarm
            d = datetime.datetime.strptime('%s %s' % (request.form.get('edit_timestamp_date'), request.form.get('edit_timestamp_time')), "%d.%m.%Y %H:%M:%S")
            alarm = classes.get('alarm')(d, request.form.get('edit_keyid'), 2, 0)
            db.session.add(alarm)

        alarm.timestamp = datetime.datetime.strptime('%s %s' % (request.form.get('edit_timestamp_date'), request.form.get('edit_timestamp_time')), "%d.%m.%Y %H:%M:%S")
        alarm._key = request.form.get('edit_key')

        alarm.set(u'id.key', request.form.get('edit_keyid'))
        alarm.set(u'k.cars1', request.form.get('val_cars1'))
        alarm.set(u'k.cars2', request.form.get('val_cars2'))
        alarm.set(u'k.material', request.form.get('val_material'))

        alarm.set(u'marker', request.form.get('marker'))
        alarm.set(u'id.city', request.form.get('edit_city'))
        _city = classes.get('city').get_byid(request.form.get('edit_cityname'))
        if _city:
            alarm.set(u'city', _city.name)
        else:
            alarm.set(u'city', request.form.get('edit_cityname'))

        alarm.set(u'streetno', request.form.get('edit_streetno'))
        street = classes.get('street').getStreet(request.form.get('edit_addressid'))
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

        d = datetime.datetime.strptime('%s %s' % (request.form.get('edit_endtimestamp_date'), request.form.get('edit_endtimestamp_time')), "%d.%m.%Y %H:%M:%S")
        alarm.set(u'endtimestamp', d)
        db.session.commit()
        signal.send('alarm', 'updated', alarmid=alarm.id)
        if request.form.get('alarm_id') == u'None':  # create new
            classes.get('alarm').changeState(alarm.id, 0)  # prepare alarm
        #else:
        #    classes.get('alarm').changeState(alarm.id, 1)  # activate alarm

    elif request.args.get('action') == 'editalarm':
        if request.args.get('alarmid', '0') == '0':  # add new alarm
            alarm = classes.get('alarm')(datetime.datetime.now(), '', 2, 0)
            #flash(babel.gettext(u'alarms.alarmadded'), 'alarms.add')
        else:  # edit alarm
            alarm = classes.get('alarm').getAlarms(id=int(request.args.get('alarmid')))
        return render_template('frontend.alarms_edit.html', alarm=alarm, cities=classes.get('city').getCities(), objects=classes.get('alarmobject').getAlarmObjects(), cars=classes.get('car').getCars(), frontendarea=params['area'], frontendmodules=frontend.frontend.modules, frontendmoduledef=classes.get('settings').get('frontend.default'))

    elif request.args.get('action') == 'refresh':  # refresh alarm section
        params['area'] = request.args.get('area')
        params['activeacc'] = int(request.args.get('activeacc'))

    elif request.args.get('action') == 'finishalarm':  # finish selected alarm
        classes.get('alarm').changeState(int(request.args.get('alarmid')), 2)
        params['area'] = request.args.get('area')

    elif request.args.get('action') == 'activatealarm':  # activate selected alarm
        ret = classes.get('alarm').changeState(int(request.args.get('alarmid')), 1)
        if len(ret) > 0:
            flash(render_template_string("{{ _('alarms.carsinuse') }}</br><b>" + ", ".join([r.name for r in sorted(ret, key=attrgetter('name'))]) + "</b>"), 'alarms')
        params['area'] = request.args.get('area')

    elif request.args.get('action') == 'deletealarm':  # delete selected alarm
        alarm = classes.get('alarm').getAlarms(id=int(request.args.get('alarmid')))
        refresh = 1 or alarm.state == 1  # check if alarm is active
        db.session.delete(alarm)
        db.session.commit()
        if refresh:
            monitorserver.sendMessage('0', 'reset')  # refresh monitor layout
        signal.send('alarm', 'deleted', alarmid=request.args.get('alarmid'))

    elif request.args.get('action') == 'archivealarm':  # archive selected alarms, id=0 == all
        if ";" in request.args.get('alarmid'):  # archive selected alarms
            for alarmid in request.args.get('alarmid')[:-1].split(';'):
                classes.get('alarm').changeState(int(alarmid), 3)
        elif int(request.args.get('alarmid')) == 0:  # archive all alarms
            classes.get('alarm').changeStates(3)
        else:  # archive single selected alarm
            classes.get('alarm').changeState(int(request.args.get('alarmid')), 3)
        params['area'] = request.args.get('area')

    alarms = classes.get('alarm').getAlarms(days=int(session['alarmfilter']))
    stats = dict.fromkeys(classes.get('alarm').ALARMSTATES.keys() + ['3'], 0)
    for alarm in alarms:
        stats[str(alarm.state)] += 1

    if 'area' not in params:
        params['area'] = 'center'
    if 'activeacc' not in params:
        params['activeacc'] = 0
    return render_template('frontend.alarms_smallarea.html', alarmstates=alarmstates, alarms=alarms, stats=stats, frontendarea=params['area'], activeacc=params['activeacc'], printdefs=classes.get('printer').getActivePrintersOfModule('alarms'), frontendmodules=frontend.frontend.modules, frontendmoduledef=classes.get('settings').get('frontend.default'), alarmfilter=session['alarmfilter'])

    
def getFrontendData(self):
    if request.args.get('action') == 'editalarm':
        
        if request.args.get('alarmid', '0') == '0':  # add new alarm
            alarm = classes.get('alarm')(datetime.datetime.now(), '', 2, 0)
            #flash(babel.gettext(u'alarms.alarmadded'), 'alarms.add')
            
        else:  # edit alarm
            alarm = classes.get('alarm').getAlarms(id=int(request.args.get('alarmid')))
        return render_template('frontend.alarms_edit.html', alarm=alarm, cities=classes.get('city').getCities(), objects=classes.get('alarmobject').getAlarmObjects(), cars=classes.get('car').getCars(), frontendarea=request.args.get('frontendarea'))

    elif request.args.get('action') == 'alarmmonitor':  # send alarm to monitor
        for monitor in classes.get('monitor').getMonitors():
            scheduler.deleteJobForEvent('changeLayout')  # send update to monitors
            for l in classes.get('monitorlayout').getLayouts(mid=int(monitor.id)):
                if l.trigger == 'alarm_added':
                    #monitorserver.sendMessage(str(monitor.id), 'load', ['layoutid=%s' % l.id, 'alarmid=%s' % request.args.get('alarmid')])
                    monitorserver.sendMessage(str(monitor.id), 'load', layoutid='%s' % l.id, alarmid='%s' % request.args.get('alarmid'))  # TODO check

    elif request.args.get('action') == 'printalarm':
        classes.get('printer').getPrinters(pid=int(request.args.get('printerdef'))).doPrint(alarmid=request.args.get('alarmid'))
        return ""

    elif request.args.get('action') == 'routeinfo':
        alarm = classes.get('alarm').getAlarms(request.args.get('alarmid'))
        data = alarm.getRouting()
        return render_template('frontend.alarms_routing.html', routing=data)

    elif request.args.get('action') == 'routecoords':
        alarm = classes.get('alarm').getAlarms(request.args.get('alarmid'))
        data = alarm.getRouting()
        return jsonify(data)

    elif request.args.get('action') == 'message':
        return render_template('frontend.alarms_message.html', alarm=classes.get('alarm').getAlarms(request.args.get('alarmid')), messagestates=classes.get('alarmhistory').historytypes, area=request.args.get('area'), reload=request.args.get('reload', 'true'))

    elif request.args.get('action') == 'addmessage':  # add message
        if request.form.get('messagetext') != "":
            alarm = classes.get('alarm').getAlarms(request.form.get('alarmid'))
            alarm.addHistory(request.form.get('messagestate'), request.form.get('messagetext'))
            db.session.commit()
        return render_template('frontend.alarms_message.html', alarm=classes.get('alarm').getAlarms(request.form.get('alarmid')), messagestates=classes.get('alarmhistory').historytypes, area=request.args.get('area'))

    elif request.args.get('action') == 'deletemessage':  # delete selected message
        #print "delete message with timestamp", request.args.get('datetime'), request.args.get('alarmid')
        alarm = classes.get('alarm').getAlarms(request.args.get('alarmid'))
        for msg in alarm.history:
            if str(msg.timestamp) == request.args.get('datetime'):
                db.session.delete(msg)
        db.session.commit()
        return render_template('frontend.alarms_message.html', alarm=classes.get('alarm').getAlarms(request.args.get('alarmid')), messagestates=classes.get('alarmhistory').historytypes, area=request.args.get('area'))

    elif request.args.get('action') == 'housecoordinates':  # return a dict with coordinats of housenumber
        if request.args.get('alarmid') != "None":
            alarm = classes.get('alarm').getAlarms(id=int(request.args.get('alarmid')))
            if alarm and alarm.housenumber:
                return {'lat': map(lambda x: x[0], alarm.housenumber.points), 'lng': map(lambda x: x[1], alarm.housenumber.points)}
        return []

    elif request.args.get('action') == 'evalhouse':  # try to eval housenumer
        street = classes.get('street').getStreet(request.args.get('streetid'))
        if street:
            for hn in street.housenumbers:
                if str(hn.number) == request.args.get('housenumber').strip():
                    return {'lat': map(lambda x: x[0], hn.points), 'lng': map(lambda x: x[1], hn.points)}
        return {}

    return ""
