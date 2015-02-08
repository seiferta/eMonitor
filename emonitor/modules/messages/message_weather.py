import datetime
import urllib2, urllib, json
from flask import render_template
from emonitor.widget.monitorwidget import MonitorWidget
from emonitor.extensions import babel, classes

__all__ = ['WeatherWidget']

babel.gettext('Mon')
babel.gettext('Tue')
babel.gettext('Wed')
babel.gettext('Thu')
babel.gettext('Fri')
babel.gettext('Sat')
babel.gettext('Sun')
babel.gettext('message.weather')


class WeatherWidget(MonitorWidget):
    """Weather widget for monitors"""
    __info__ = {'icon': 'fa-cloud'}
    __fields__ = ['weather.location', 'weather.icons', 'weather.forecast']
    template = 'widget.message.weather.html'
    size = (5, 4)
    lastcall = None
    data = None

    def __repr__(self):
        return "weather"

    def getAdminContent(self, **params):
        """Deliver admin content for current message module"""
        params.update({'settings': classes.get('settings')})
        return render_template('admin.message.weather.html', **params)

    def getMonitorContent(self, **params):
        """Deliver monitor content for current message module"""
        self.addParameters(**params)
        return self.getHTML('', **params)

    def getEditorContent(self, **params):
        """Deliver editor content for current message module"""
        params.update({'settings': classes.get('settings')})
        return render_template('frontend.messages_edit_weather.html', **params)

    def addParameters(self, **kwargs):
        """
        Add special parameters for weather widget *messages.weather.\**
        check https://developer.yahoo.com/yql/console/ for online editor

        :param kwargs: list of parameters for update
        """
        if 'message' in kwargs:
            location = kwargs['message'].attributes['weather.location']
            icons = kwargs['message'].attributes['weather.icons']
            forecast = kwargs['message'].attributes['weather.forecast']
        else:
            location = classes.get('settings').get('messages.weather.location')
            icons = classes.get('settings').get('messages.weather.icons')
            forecast = classes.get('settings').get('messages.weather.forecast')

        if not self.lastcall or datetime.datetime.now() > self.lastcall + datetime.timedelta(hours=1):
            # reload data from web
            compass = ['N', 'NNO', 'NO', 'ONO', 'O', 'OSO', 'SO', 'SSO', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N']
            baseurl = "https://query.yahooapis.com/v1/public/yql?"
            yql_query = 'select * from weather.forecast where woeid in (select woeid from geo.placefinder where text="%s" and gflags="R" limit 1) and u="c"' % location
            yql_url = baseurl + urllib.urlencode({'q': yql_query}) + "&format=json"
            result = urllib2.urlopen(yql_url).read()
            self.data = json.loads(result)
            self.data = self.data['query']['results']['channel']
            try:
                self.data['wind']['directionstring'] = compass[int(int(self.data['wind']['direction']) / 22.5)]
            except ValueError:
                self.data['wind']['directionstring'] = ""
            if 'am' in self.data['astronomy']['sunrise']:
                self.data['astronomy']['sunrise'] = self.data['astronomy']['sunrise'][:-3]
            if 'pm' in self.data['astronomy']['sunset']:
                self.data['astronomy']['sunset'] = self.data['astronomy']['sunset'][:-3].split(':')
                self.data['astronomy']['sunset'][0] = "%s" % (12 + int(self.data['astronomy']['sunset'][0]))
                self.data['astronomy']['sunset'] = ':'.join(self.data['astronomy']['sunset'])
            self.lastcall = datetime.datetime.now()

        kwargs.update({'location': location, 'icons': icons, 'forecast': forecast, 'data': self.data})
        self.params = kwargs
