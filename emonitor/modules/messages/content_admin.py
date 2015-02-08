from flask import render_template, request
from emonitor.extensions import classes, monitorserver
from emonitor.modules.messages.messagetype import MessageType


def getAdminContent(self, **params):
    """
    Deliver admin content of module messages

    :param params: use given parameters of request
    :return: rendered template as string
    """
    module = request.view_args['module'].split('/')

    if 'saveparameters' in request.form.keys():  # save parameters for modules
        for k in [k for k in request.form if k != 'saveparameters']:
            classes.get('settings').set("messages.%s" % k, request.form.get(k))
        monitorserver.sendMessage('0', 'reset')  # refresh monitor layout

    if len(module) == 2:
        if module[1] == 'types':  # type submodule
            params.update({'implementations': MessageType.getMessageTypes()})
            return render_template('admin.messages.types.html', **params)
    else:
        messages = {'1': classes.get('message').getMessages(state=1), '0': classes.get('message').getMessages(state=0)}
        params.update({'messages': messages})
        return render_template('admin.messages.html', **params)


def getAdminData(self, **params):
    """
    Deliver admin content of module messages (ajax)

    :return: rendered template as string or json dict
    """
    if request.args.get('action') == 'messagesforstate':
        messages = classes.get('message').getMessages(state=int(request.args.get('state')))
        return render_template('admin.messages_message.html', messages=messages)
    return ""
