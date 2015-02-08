"""
Standard message widget to display different message_* entries
"""
from flask import render_template
from emonitor.extensions import babel, classes
from emonitor.modules.messages.messagetype import MessageType
from emonitor.widget.monitorwidget import MonitorWidget


__all__ = ['MessageWidget']

babel.gettext(u'message.base')


class MessageWidget(MonitorWidget):
    """Widget for messages"""
    template = "widget.message.messages.html"
    size = (2, 2)

    def __repr__(self):
        return "base"

    def getAdminContent(self, **params):
        params.update({'implementations': MessageType.getMessageTypes(), 'settings': classes.get('settings')})
        return render_template('admin.message.base.html', **params)

    def addParameters(self, **kwargs):
        """
        Add special parameters for widget and create content of widget from MessageType
        :param kwargs: list of parameters for update
        """
        content = ""
        if 'clientid' in kwargs:
            messages = filter(lambda x: x.currentState and kwargs['clientid'] in x.monitors, classes.get('message').getActiveMessages())
        else:
            messages = filter(lambda x: x.currentState, classes.get('message').getActiveMessages())

        settings = classes.get('settings')
        kwargs.update({'settings': settings})
        if len(messages) > 0:
            for message in messages:
                kwargs.update({'message': message})
                #content += '<div>' + message.type.getMonitorContent(**kwargs) + '</div>\n'
                pos = render_template('monitor.messages.position.html', number=len(messages), position=messages.index(message))
                content += '<div class="slide">%s%s</div>\n' % (message.type.getMonitorContent(**kwargs), pos)

        else:  # load default message widget
            for mt in MessageType.getMessageTypes():
                if mt[0] == settings.get('messages.base.default'):
                    kwargs.update({'footer': 1})  # set footer
                    content = mt[1].getMonitorContent(**kwargs)

        kwargs.update({'content': content})
        if len(messages) > 0:
            kwargs.update({'footer': 1})
        self.params = kwargs
        return kwargs
