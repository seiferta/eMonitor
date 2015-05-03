import os
from flask import request, render_template, current_app
from emonitor.extensions import db, events, scheduler#, monitorserver
from emonitor.modules.monitors.monitor import Monitor
from emonitor.modules.monitors.monitorlayout import MonitorLayout


def getAdminContent(self, **params):
    """
    Deliver admin content of module monitors

    :param params: use given parameters of request
    :return: rendered template as string
    """
    module = request.view_args['module'].split('/')
    
    if len(module) == 1:  # monitor definition
        if request.method == 'POST':
            if request.form.get('action') == 'createmonitor':  # add monitor
                params.update({'monitor': Monitor('', '', '', '', '', '', ''), 'orientations': ['monitors.landscape', 'monitors.portrait']})
                return render_template('admin.monitors_actions.html', **params)

            elif request.form.get('action') == 'updatemonitors':  # save monitor
                if request.form.get('edit_id') != 'None':  # update
                    monitor = Monitor.getMonitors(id=request.form.get('edit_id'))
                else:  # add monitor
                    monitor = Monitor('', '', '', '', '', '', '')
                    db.session.add(monitor)
                    
                monitor.clientid = request.form.get('edit_clientid')
                monitor.name = request.form.get('edit_name')
                monitor.orientation = request.form.get('edit_orientation')
                monitor.resolutionx = request.form.get('edit_resolutionx')
                monitor.resolutiony = request.form.get('edit_resolutiony')
                monitor.formatx = request.form.get('edit_formatx')
                monitor.formaty = request.form.get('edit_formaty')
                db.session.commit()
                
            elif request.form.get('action').startswith('editmonitor_'):  # edit monitor
                params.update({'monitor': Monitor.getMonitors(id=int(request.form.get('action').split('_')[-1])), 'orientations': ['monitors.landscape', 'monitors.portrait']})
                return render_template('admin.monitors_actions.html', **params)

            elif request.form.get('action').startswith('deletemonitor_'):  # delete monitor
                db.session.delete(Monitor.getMonitors(id=int(request.form.get('action').split('_')[-1])))
                db.session.commit()
                
            elif request.form.get('action').startswith('createlayout_'):  # layout edit
                mid = int(request.form.get('action').split('_')[-1])
                monitor = Monitor.getMonitors(id=int(request.form.get('action').split('_')[-1]))
                
                layouts = []
                usedtriggers = []
                for l in monitor.getLayouts():
                    if l.mid == monitor.id:
                        layouts.append(l)
                        usedtriggers.append(l.trigger)

                params.update({'monitors': Monitor.getMonitors(), 'layout': MonitorLayout(mid, '', '', '', 0, 0, ''), 'layouts': layouts, 'triggers': events.getEvents(), 'usedtriggers': usedtriggers, 'monitor': Monitor.getMonitors(id=mid), 'widgets': current_app.blueprints['widget'].modules})
                return render_template('admin.monitors.layout_actions.html', **params)

            elif request.form.get('action') == 'updatelayout':  # update layout
                    if request.form.get('edit_id') != 'None':  # update
                        layout = MonitorLayout.getLayouts(id=request.form.get('edit_id'))
                    
                    else:  # add layout
                        layout = MonitorLayout('', '', '', '', '', '', '')
                        db.session.add(layout)
                        
                    layout.mid = request.form.get('edit_mid')
                    layout.trigger = ";".join(sorted(request.form.getlist('edit_trigger')))
                    layout.layout = request.form.get('edit_layout').split('\r\n')
                    layout.theme = request.form.get('edit_theme')
                    layout.mintime = request.form.get('edit_mintime')
                    layout.maxtime = request.form.get('edit_maxtime')
                    layout.nextid = request.form.get('edit_nextid')
                    db.session.commit()
                    
            elif request.form.get('action').startswith('editmonitorlayout_'):  # edit layout
                layout = MonitorLayout.getLayouts(id=int(request.form.get('action').split('_')[-1]))
                layouts = []
                usedtriggers = []
                for l in MonitorLayout.getLayouts(mid=layout.mid):
                    if l.id != layout.id:
                        layouts.append(l)
                        usedtriggers.extend(l.trigger.split(';'))
                params.update({'monitors': Monitor.getMonitors(), 'layout': layout, 'layouts': layouts, 'triggers': events.getEvents(), 'usedtriggers': usedtriggers, 'monitor': Monitor.getMonitors(id=layout.mid), 'widgets': current_app.blueprints['widget'].modules})
                return render_template('admin.monitors.layout_actions.html', **params)

            elif request.form.get('action').startswith('deletemonitorlayout_'):  # delete layout
                db.session.delete(MonitorLayout.getLayouts(id=int(request.form.get('action').split('_')[-1])))
                db.session.commit()

        params.update({'monitors': Monitor.getMonitors()})
        return render_template('admin.monitors.html', **params)

    else:
        if module[1] == 'style':  # monitor styles
        
            themecss = {}
            for root, dirs, files in os.walk("%s/emonitor/frontend/web/css" % current_app.config.get('PROJECT_ROOT')):
                for name in [f for f in files if f.startswith('monitor_')]:
                    with open("%s/emonitor/frontend/web/css/%s" % (current_app.config.get('PROJECT_ROOT'), name), 'r') as c:
                        themecss[name.split("_")[-1][:-4]] = c.read()
                    
            if request.method == 'POST':
                if request.form.get('action') == 'savecss':
                    for k in themecss:
                        if themecss[k] != request.form.get(k):
                            with open("%s/emonitor/frontend/web/css/monitor_%s.css" % (current_app.config.get('PROJECT_ROOT'), k), 'w') as c:
                                c.write(request.form.get(k))
                            themecss[k] = request.form.get(k)
                            
                # check new theme data
                if request.form.get('newname') != '' and request.form.get('newcss') != '':
                    with open("%s/emonitor/frontend/web/css/monitor_%s.css" % (current_app.config.get('PROJECT_ROOT'), request.form.get('newname')), 'w') as c:
                        c.write(request.form.get('newcss'))
                    themecss[request.form.get('newname')] = request.form.get('newcss')
                    
            params.update({'themes': themecss})
            return render_template('admin.monitors.style.html', **params)

        elif module[1] == 'current':  # monitors current
            if request.method == 'POST':
                pass
            params.update({'monitors': Monitor.getMonitors()})
            return render_template('admin.monitors.current.html', **params)

        elif module[1] == 'actions':  # monitors actions
            return render_template('admin.monitors.actions.html', **params)

    return "else"

    
def getAdminData(self):
    """
    Deliver admin content of module monitors (ajax)

    :return: rendered template as string or json dict
    """
    if request.args.get('action') == 'thumb':  # create dynamic thumbnail of layout
        layout = MonitorLayout.getLayouts(id=request.args.get('id'))
        return layout.getLayoutThumb()
    
    if request.args.get('action') == 'widgetparams':  # params: width, height, w_id,
        return render_template('admin.monitors.actions.html', width=request.args.get('width'), height=request.args.get('height'), widget=request.args.get('w_id'))  # macro='widgetparams'
        
    if request.args.get('action') == 'ping':  # ping clients
        from emonitor.extensions import monitorserver
        clients = monitorserver.getClients()  # start discovery
        return dict(clients=[k for k in clients.keys() if clients[k][0]])

    if request.args.get('action') == 'schedules':  # get active schedules
        return render_template('admin.monitors.actions_actions.html', schedjobs=scheduler.get_jobs())  # macro='schedjobs'
        
    return ""
