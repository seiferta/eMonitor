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
        return render_template('frontend.monitors.html', monitors=classes.get('monitor').getMonitors())

    elif request.args.get('action') == 'ping':  # search from monitors
        clients = monitorserver.getClients()  # start discovery
        return dict(clients=[k for k in clients.keys() if clients[k][0]])

    elif request.args.get('action') == 'changelayout':  # load monitorlayout
        monitorserver.changeLayout(request.args.get('id'), request.args.get('layoutid'))
        return ""
    return ""
