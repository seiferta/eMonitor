import datetime
from flask import render_template, request
from emonitor.extensions import db
from emonitor.utils import getreStructuredText
from emonitor.frontend import frontend
from emonitor.modules.messages.messages import Messages
from emonitor.modules.monitors.monitor import Monitor
from emonitor.modules.messages.messagetype import MessageType
from emonitor.modules.settings.settings import Settings


def getFrontendContent(**params):
    """
    Deliver frontend content of module messages

    :return: data of messages
    """
    if 'area' in request.args:
        params['area'] = request.args.get('area')

    if 'area' not in params:
        params['area'] = 'center'
    if 'activeacc' not in params:
        params['activeacc'] = 0

    if request.form.get('action') == 'updatemessage':
        sd = datetime.datetime.strptime('%s %s' % (request.form.get('messages.startdate'), '00:00:00'), "%d.%m.%Y %H:%M:%S")
        ed = datetime.datetime.strptime('%s %s' % (request.form.get('messages.enddate'), '23:59:59'), "%d.%m.%Y %H:%M:%S")
        if request.form.get('messages.id') != 'None':  # update message
            msg = Messages.getMessages(id=request.form.get('messages.id'))
            msg.startdate = sd
            msg.enddate = ed
        else:  # create new message
            msg = Messages('', '', sd, ed, 0, request.form.get('messages.type'))
            db.session.add(msg)
        msg.name = request.form.get('messages.name')
        msg.remark = request.form.get('messages.remark')
        msg.state = int(request.form.get('messages.state'))
        msg.monitors = request.form.getlist('messages.monitors')
        cron = dict(day_of_week='*', hour='*')
        if len(request.form.getlist('messages.cron.day_of_week')) > 0:
            cron['day_of_week'] = ",".join(request.form.getlist('messages.cron.day_of_week'))
        if len(request.form.getlist('messages.cron.hour')) > 0:
            cron['hour'] = ",".join(request.form.getlist('messages.cron.hour'))
        attributes = dict(cron=cron)

        # add type specific fields
        for fn in msg.type.getFieldNames():
            attributes[fn] = request.form.get('messages.' + fn)

        msg.attributes = attributes
        db.session.commit()
        Messages.updateMessageTrigger()

    elif request.args.get('action') == 'deletemessage':
        db.session.delete(Messages.getMessages(id=int(request.args.get('messageid'))))
        db.session.commit()

    elif request.args.get('action') == 'editmessage':
        monitors = Monitor.getMonitors()
        if request.args.get('messageid', '0') == '0':  # add new message
            message = Messages('', '', datetime.datetime.now(), datetime.datetime.now(), 0, '')
            message.monitors = [str(m.id) for m in monitors]
        else:  # edit message
            message = Messages.getMessages(id=int(request.args.get('messageid')))
        return render_template('frontend.messages_edit.html', message=message, implementations=filter(lambda x: str(x[1]) != 'base', MessageType.getMessageTypes()), frontendarea=params['area'], frontendmodules=frontend.frontend.modules, frontendmoduledef=Settings.get('frontend.default'), monitors=monitors)

    messages = {'1': Messages.getMessages(state=1), '0': Messages.getMessages(state=0)}
    return render_template('frontend.messages_smallarea.html', messages=messages, frontendarea=params['area'], frontendmodules=frontend.frontend.modules, frontendmoduledef=Settings.get('frontend.default'), monitors=Monitor.getMonitors())


def getFrontendData(self):
    """
    Deliver frontend content of module messages (ajax)

    :return: rendered template as string or json dict
    """
    if request.args.get('action') == 'messagetypefields':
        impl = filter(lambda x: x[0] == request.args.get('messagetypename'), MessageType.getMessageTypes())
        if len(impl) > 0:
            return impl[0][1].getEditorContent(**dict(message=Messages('', '', '', '', 0, impl[0][0])))

    elif request.args.get('action') == 'render':
        return {'text': getreStructuredText(request.form.get('template'))}
    return ""
