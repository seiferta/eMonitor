from flask import render_template
from emonitor.extensions import babel
from emonitor.widget.monitorwidget import MonitorWidget
from emonitor.modules.settings.settings import Settings

__all__ = ['TextWidget']

babel.gettext(u'message.text')


class TextWidget(MonitorWidget):
    """Widget for text messages"""
    __info__ = {'icon': 'fa-file-text-o'}
    __fields__ = ['layout', 'content']
    template = 'widget.message.text.html'
    size = (5, 4)

    def __repr__(self):
        return "text"

    def getAdminContent(self, **params):
        """
        Get content for admin area to config all parameters of message type object

        :param params: list of all currently used parameters
        :return: rendered template of text message type
        """
        params.update({'settings': Settings})
        return render_template('admin.message.text.html', **params)

    def getMonitorContent(self, **params):
        """
        Get Content for monitor of text type message

        :param params: list of all currently used parameters
        :return: html content for monitor
        """
        self.addParameters(**params)
        return self.getHTML('', **params)

    def getEditorContent(self, **params):
        """
        Get content for frontend configuration of text type message

        :param params: list of all currently used parameters
        :return: renderd template of text message type
        """
        return render_template('frontend.messages_edit_text.html', **params)

    def addParameters(self, **kwargs):
        """
        Add special parameters for text widget *messages.text.\**
        :param kwargs: list of parameters for update
        """
        if 'message' in kwargs:
            content = kwargs['message'].get('content')
            template = kwargs['message'].get('template')  # todo: define templates
        else:
            content = Settings.get('messages.text.content')
            template = ""  # todo define templates

        kwargs.update({'content': content, 'template': template})
        self.params = kwargs
