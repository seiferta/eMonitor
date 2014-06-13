from flask import render_template, request
from emonitor.extensions import classes, monitorserver


def getFrontendContent(self, params={}):
    pass


def getFrontendData(self):

    if request.args.get('action') == 'monitoroverview':
        monitors = []
        return render_template('frontend.monitors.html', monitors=monitors)

    elif request.args.get('action') == 'ping':  # search fro monitors
        clients = monitorserver.getClients()
        layouts = {}
        for c in clients:
            layouts[c] = classes.get('monitorlayout').getLayouts(mid=c)
        return render_template('frontend.monitors_clients.html', clients=clients, layouts=layouts)

    elif request.args.get('action') == 'changelayout':  # load monitorlayout
        monitorserver.changeLayout(request.args.get('id'), request.args.get('layoutid'))
        return ""
    return ""
