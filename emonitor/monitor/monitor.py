"""
Basic framework for monitor area (blueprint).
This area will be used by the client part of eMonitor

Use the info parameter of the module implementation:
::

    info = dict(area=['widget'], name='modulename', path='modulepath', ...)

Widgets are parts of the monitor area to display information about the module
"""
import re
import datetime, time
from flask import Blueprint, current_app, render_template, request, send_from_directory
from emonitor.extensions import classes, monitorserver, scheduler


monitor = Blueprint('monitor', __name__, template_folder="templates")


@monitor.route('/monitor')
@monitor.route('/monitor/')
@monitor.route('/monitor/<int:clientid>')
def monitorContent(clientid=0):
    """
    Create monitor area under url */monitor*

    :return: rendered template */emonitor/monitor/templates/monitor.html*
    """
    alarmid = None
    count = []
    pos = 0

    if 'alarmid' in request.args:  # eval active alarms or defined id
        alarmid = int(request.args.get('alarmid'))
        if len(classes.get('alarm').getActiveAlarms()) > 0:
            count = classes.get('alarm').getActiveAlarms()
    elif len(classes.get('alarm').getActiveAlarms()) > 0:
        alarmid = classes.get('alarm').getActiveAlarms()[0].id
        count = classes.get('alarm').getActiveAlarms()
    alarm = classes.get('alarm').getAlarms(id=alarmid)

    defmonitor = classes.get('monitor').getMonitors(clientid)
    try:
        layout = defmonitor.currentlayout
    except AttributeError:
        return render_template('monitor-test.html')

    if 'layoutid' in request.args:  # eval current layout
        layout = defmonitor.layout(int(request.args.get('layoutid')))
    else:
        try: layout = defmonitor.getLayouts(triggername='default')[0]
        except: pass

    if len(count) > 0:  # eval layout for current and next alarm
        nextalarm = currentalarm = count[0]
        for c in count:
            if c.id == alarmid:
                pos = count.index(c) + 1
                currentalarm = count[(pos - 1) % len(count)]
                nextalarm = count[pos % len(count)]

            for j in [job for job in scheduler.get_jobs(name='changeLayout') if "'alarmid', %s" % c.id in str(job.args)]:
                scheduler.unschedule_job(j)  # layout changes for given alarm

        for l in defmonitor.getLayouts(triggername='alarm_added'):
            for tr in l.trigger.split(';'):  # support more than one trigger for layout
                if ('.' in tr and len(count) >= 1 and tr.split('.')[-1] == currentalarm.get('alarmtype')) or ('.' not in tr and currentalarm.get('alarmtype', '') == ""):
                    layout = l
                    break

        if len(count) > 1:
            for l in defmonitor.getLayouts(triggername='alarm_added'):
                for tr in l.trigger.split(';'):  # support more than one trigger for layout
                    if ('.' in tr and tr.split('.')[-1] == nextalarm.get('alarmtype')) or ('.' not in tr and nextalarm.get('alarmtype', '') == ""):
                        if int(l.mintime) != 0:
                            scheduler.add_date_job(monitorserver.changeLayout, datetime.datetime.fromtimestamp(time.time() + float(l.mintime)), [defmonitor.id, l.id, [('alarmid', nextalarm.id), ('monitorid', defmonitor.id)]])

    # render content for monitor
    content = '<div id="content">%s</div>' % layout.htmllayout
    for w in re.findall('\[\[\s?(.+?)\s?\]\]', content):
        for widgets in current_app.blueprints['widget'].modules:
            for widget in widgets.getMonitorWidgets():
                if widget.getName() == w:
                    content = content.replace(u'[[%s]]' % w, widget.getHTML(request, alarmid=alarmid, alarm=alarm))

    return render_template('monitor.html', content=content, theme=layout.theme, activecount=len(count), position=pos, app_name=current_app.config.get('PROJECT'), app_version=current_app.config.get('APP_VERSION'))


# static folders
@monitor.route('/monitor/inc/<path:filename>')
def streets_static(filename):
    return send_from_directory("%s/emonitor/monitor/inc/" % current_app.config.get('PROJECT_ROOT'), filename)
