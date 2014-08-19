import re
import datetime, time
from flask import Blueprint, current_app, render_template, request, send_from_directory
from emonitor.extensions import classes, monitorserver, scheduler


monitor = Blueprint('monitor', __name__, template_folder="templates")


@monitor.route('/monitor')
@monitor.route('/monitor/')
@monitor.route('/monitor/<int:clientid>')
@monitor.route('/monitor/<int:clientid>')
def monitorContent(clientid=0):
    #print "clientid", clientid, request.args
    alarmid = None
    count = []
    pos = 0

    if 'alarmid' in request.args:
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

    if 'layoutid' in request.args:
        layout = defmonitor.layout(int(request.args.get('layoutid')))

    if len(count) > 1:  # autochange layout after min-time of current layout
        # load last active alarm - slider if more active alarms
        for layout in [la for la in defmonitor.getLayouts() if la.trigger == 'alarm_added']:
            nextalarm = count[0].id  # first alarmid

            for c in count:
                if c.id == alarmid:
                    try:
                        pos = count.index(c) + 1
                        nextalarm = count[pos].id
                        break
                    except: pass

                for j in [job for job in scheduler.get_jobs() if job.name == 'changeLayout']:
                    if "'alarmid', %s" % c.id in str(j.args):  # layout changes for given alarm
                        scheduler.unschedule_job(j)

            scheduler.add_date_job(monitorserver.changeLayout, datetime.datetime.fromtimestamp(time.time() + float(layout.mintime)), [defmonitor.id, layout.id, [('alarmid', nextalarm), ('monitorid', defmonitor.id)]])

    elif len(count) == 1:
        try: layout = [la for la in defmonitor.getLayouts() if la.trigger == 'alarm_added'][0]
        except: pass

    elif len(count) == 0:
        # load default layout
        if 'layoutid' not in request.args:
            try: layout = [la for la in defmonitor.getLayouts() if la.trigger == 'default'][0]
            except: pass

    # render content for monitor
    content = '<div id="content">' + layout.htmllayout + '</div>'
    for w in re.findall('\[\[\s?(.+?)\s?\]\]', content):
        for widgets in current_app.blueprints['widget'].modules:
            for widget in widgets.getMonitorWidgets():
                if widget.getName == w:
                    content = content.replace(u'[[%s]]' % w, widget.getHTML(request, alarmid=alarmid, alarm=alarm))

    return render_template('monitor.html', content=content, theme=layout.theme, activecount=len(count), position=pos, app_name=current_app.config.get('PROJECT'), app_version=current_app.config.get('APP_VERSION'))


# static folders
@monitor.route('/monitor/inc/<path:filename>')
def streets_static(filename):
    return send_from_directory("%s/emonitor/monitor/inc/" % current_app.config.get('PROJECT_ROOT'), filename)
