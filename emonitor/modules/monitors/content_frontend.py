from flask import render_template, request
from emonitor.extensions import classes, monitorserver, scheduler


def getFrontendContent(self, **params):
    """
    Deliver frontend content of module monitors

    :return: data of monitors
    """
    pass


def getFrontendData(self):
    """
    Deliver frontend content of module monitors (ajax)

    :return: rendered template as string or json dict
    """
    if request.args.get('action') == 'monitoroverview':
        monitors = []
        return render_template('frontend.monitors.html', monitors=monitors)

    elif request.args.get('action') == 'ping':  # search from monitors
        if request.args.get('refresh') == '1':  # force refresh
            scheduler.add_job(monitorserver.getClients)  # use scheduler for search
        else:
            clients = monitorserver.clients['clients']  # clientids
            layouts = {}
            for c in clients:
                try:
                    layouts[c] = classes.get('monitor').getMonitors(clientid=int(c)).getLayouts()
                except AttributeError:  # no layouts for clientid found
                    pass
            return render_template('frontend.monitors_clients.html', clients=clients, layouts=layouts, t=monitorserver.clients['time'])

    elif request.args.get('action') == 'changelayout':  # load monitorlayout
        monitorserver.changeLayout(request.args.get('id'), request.args.get('layoutid'))
        return ""
    return ""
