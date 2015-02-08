from flask import send_from_directory
from emonitor.utils import Module
from emonitor.extensions import classes, db, babel
from .message_weather import WeatherWidget
from .message_base import MessageWidget
from .content_admin import getAdminContent, getAdminData
from .content_frontend import getFrontendContent, getFrontendData


class MessagesModule(Module):
    info = dict(area=['admin', 'frontend', 'widget'], name='messages', path='messages', icon='fa-newspaper-o', version='0.1')

    def __repr__(self):
        return "messages"

    def __init__(self, app):
        Module.__init__(self, app)
        # add template path
        app.jinja_loader.searchpath.append("%s/emonitor/modules/messages/templates" % app.config.get('PROJECT_ROOT'))

        # subnavigation
        self.adminsubnavigation = [('/admin/messages', 'messages.main'), ('/admin/messages/types', 'messages.types')]
        self.widgets = [MessageWidget('messages', size=(4, 2), template='widget.message.messages.html'), WeatherWidget('weather', size=(5, 4), template='widget.message.weather.html')]

        # create database tables
        from .messages import Messages
        classes.add('message', Messages)
        db.create_all()

        # static folders
        @app.route('/messages/inc/<path:filename>')
        def messages_static(filename):
            return send_from_directory("%s/emonitor/modules/messages/inc/" % app.config.get('PROJECT_ROOT'), filename)

        # translations
        babel.gettext(u'module.messages')
        babel.gettext(u'messages.main')
        babel.gettext(u'messages.types')
        babel.gettext(u'weather')
        babel.gettext(u'messages')
        babel.gettext(u'messagestate.1')  # activated
        babel.gettext(u'messagestate.0')  # deactivated
        babel.gettext(u'message.state.1')  # active
        babel.gettext(u'message.state.0')  # in-active

        # init
        # Do init script for messages at start and add active messages
        classes.get('message').initMessageTrigger()

    def frontendContent(self):
        return 1

    def getFrontendContent(self, **params):
        return getFrontendContent(**params)

    def getFrontendData(self):
        return getFrontendData(self)

    def getAdminContent(self, **params):
        return getAdminContent(self, **params)

    def getAdminData(self, **params):
        return getAdminData(self, **params)
