import datetime
from flask import render_template, request
from emonitor.extensions import classes, db
from emonitor.frontend import frontend
from emonitor.modules.messages.messagetype import MessageType


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
            msg = classes.get('message').getMessages(id=request.form.get('messages.id'))
            msg.startdate = sd
            msg.enddate = ed
        else:  # create new message
            msg = classes.get('message')('', '', sd, ed, 0, request.form.get('messages.type'))
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
        classes.get('message').updateMessageTrigger()

    elif request.args.get('action') == 'deletemessage':
        db.session.delete(classes.get('message').getMessages(id=int(request.args.get('messageid'))))
        db.session.commit()

    elif request.args.get('action') == 'editmessage':
        monitors = classes.get('monitor').getMonitors()
        if request.args.get('messageid', '0') == '0':  # add new message
            message = classes.get('message')('', '', datetime.datetime.now(), datetime.datetime.now(), 0, '')
            message.monitors = [str(m.id) for m in monitors]
        else:  # edit message
            message = classes.get('message').getMessages(id=int(request.args.get('messageid')))
        return render_template('frontend.messages_edit.html', message=message, implementations=filter(lambda x: str(x[1]) != 'base', MessageType.getMessageTypes()), frontendarea=params['area'], frontendmodules=frontend.frontend.modules, frontendmoduledef=classes.get('settings').get('frontend.default'), monitors=monitors)

    messages = {'1': classes.get('message').getMessages(state=1), '0': classes.get('message').getMessages(state=0)}
    return render_template('frontend.messages_smallarea.html', messages=messages, frontendarea=params['area'], frontendmodules=frontend.frontend.modules, frontendmoduledef=classes.get('settings').get('frontend.default'), monitors=classes.get('monitor').getMonitors())


def getFrontendData(self):
    """
    Deliver frontend content of module messages (ajax)

    :return: rendered template as string or json dict
    """
    if request.args.get('action') == 'messagetypefields':
        impl = filter(lambda x: x[0] == request.args.get('messagetypename'), MessageType.getMessageTypes())
        if len(impl) > 0:
            return impl[0][1].getEditorContent(**dict(message=classes.get('message')('', '', '', '', 0, impl[0][0])))
    return ""
