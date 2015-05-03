from flask import render_template, request
from emonitor.modules.monitors.monitor import Monitor


def getFrontendData(self):
    """
    Deliver frontend content of module monitors (ajax)

    :return: rendered template as string or json dict
    """
    from emonitor.extensions import monitorserver
    if request.args.get('action') == 'monitoroverview':
        return render_template('frontend.monitors.html', monitors=Monitor.getMonitors())

    elif request.args.get('action') == 'ping':  # search from monitors
        clients = monitorserver.getClients()  # start discovery
        return dict(clients=[k for k in clients.keys() if clients[k][0]])

    elif request.args.get('action') == 'changelayout':  # load monitorlayout
        #monitorserver.changeLayout(request.args.get('id'), request.args.get('layoutid'))
        monitorserver.changeLayout(request.args.get('id'), layoutid=request.args.get('layoutid'))  # TODO
        return ""
    return ""
