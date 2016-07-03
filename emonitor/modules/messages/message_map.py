import json
from flask import render_template
from emonitor.extensions import babel
from emonitor.widget.monitorwidget import MonitorWidget
from emonitor.modules.settings.settings import Settings
from emonitor.modules.maps.map import Map
from emonitor.utils import getreStructuredText

__all__ = ['MapWidget']

babel.gettext(u'map')
babel.gettext(u'message.map')


class MapWidget(MonitorWidget):
    """Widget for map messages"""
    __info__ = {'icon': 'fa-map-signs'}
    __fields__ = ['text', 'mapconfig', 'textposition']
    template = 'widget.message.map.html'
    size = (5, 4)

    def __repr__(self):
        return "map"

    def getAdminContent(self, **params):
        """
        Get content for admin area to config all parameters of message type object

        :param params: list of all currently used parameters
        :return: rendered template of text message type
        """
        params.update({'settings': Settings})
        return render_template('admin.message.map.html', **params)

    def getMonitorContent(self, **params):
        """
        Get Content for monitor of map type message

        :param params: list of all currently used parameters
        :return: html content for monitor
        """
        self.addParameters(**params)
        return self.getHTML('', **params)

    def getEditorContent(self, **params):
        """
        Get content for frontend configuration of map type message

        :param params: list of all currently used parameters
        :return: renderd template of text message type
        """
        return render_template('frontend.messages_edit_map.html', **params)

    def addParameters(self, **kwargs):
        """
        Add special parameters for map widget *messages.map.\**
        :param kwargs: list of parameters for update
        """
        if 'message' in kwargs:
            text = kwargs['message'].get('text')
            template = kwargs['message'].get('template')  # todo: define templates
            mapconfig = kwargs['message'].get('mapconfig')
            map = Map.getDefaultMap()
        else:
            text = ""
            template = ""  # todo define templates
            mapconfig = ""
            map = None

        kwargs.update({'map': map, 'text': text, 'mapconfig': mapconfig, 'template': template})
        self.params = kwargs

    @staticmethod
    def action(**kwargs):
        """
        implementation of map-message specific actions
        :param kwargs: list of parameters: action, mid and all arguments of ajax requests
        :return: results of action
        """
        if kwargs.get('action') == 'render':
            """
            render string with restructured text engine
            """
            return getreStructuredText(kwargs.get('text'))

        elif kwargs.get('action') == 'mapconfig':
            """
            open overlay map with config values
            """
            try:
                config = json.loads(kwargs.get('config', ''))
            except ValueError:
                config = {}
            if not config.get('lat'):
                config['lat'] = Settings.get('defaultLat')
            if not config.get('lng'):
                config['lng'] = Settings.get('defaultLng')
            config['map'] = Map.getDefaultMap()
            kwargs.update(**config)
            #print ">>>>>", kwargs
            return render_template("frontend.messages_map.html", **kwargs)
        return ""
