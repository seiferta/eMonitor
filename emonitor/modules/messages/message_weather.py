import datetime
import time
import urllib2, urllib, json
import codecs
from itertools import ifilter
from flask import render_template, current_app
from emonitor.widget.monitorwidget import MonitorWidget
from emonitor.extensions import babel
from emonitor.modules.settings.settings import Settings

__all__ = ['WeatherWidget']

babel.gettext('Mon')
babel.gettext('Tue')
babel.gettext('Wed')
babel.gettext('Thu')
babel.gettext('Fri')
babel.gettext('Sat')
babel.gettext('Sun')
babel.gettext('message.weather')

wIcons = ['{}.png'.format(i) for i in range(0, 19)]


def getIcon4Code(code, iconlist):
    try:
        return wIcons[[_i for _i, x in enumerate(iconlist) if code in x][0]]
    except IndexError:
        return wIcons[0]


def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        try:
            items.extend(flatten(v, new_key, sep=sep).items())
        except:
            items.append((new_key, v))
    return dict(items)


class WeatherData:
    def __init__(self):
        self.weather = {'condition': "", 'conditioncode': '', 'conditionicon': '', 'conditioncss': '', 'temperature': '', 'temperatureunit': '', 'humidity': '', 'pressure': '',
                        'forecast': [], 'sunrise': '', 'sunset': '', 'location': '', 'builddate': '', 'rain': 0, 'clouds': 0,
                        'windspeed': '', 'winddirection': '', 'windunit': ''}

    def set(self, name, value):
        if name in self.weather:
            self.weather[name] = value

    def get(self, name, default=""):
        return self.weather.get(name, default)


class WeatherWidget(MonitorWidget):
    """Weather widget for monitors"""
    __info__ = {'icon': 'fa-cloud'}
    __fields__ = ['weather.type', 'weather.location', 'weather.locationid', 'weather.icons', 'weather.forecast']
    template = 'widget.message.weather.html'
    size = (5, 4)
    lastcall = None
    data = WeatherData()

    def __repr__(self):
        return "weather"

    def getAdminContent(self, **params):
        """Deliver admin content for current message module"""
        params.update({'settings': Settings})
        return render_template('admin.message.weather.html', **params)

    def getMonitorContent(self, **params):
        """Deliver monitor content for current message module"""
        self.addParameters(**params)
        return self.getHTML('', **params)

    def getEditorContent(self, **params):
        """Deliver editor content for current message module"""
        params.update({'settings': Settings})
        return render_template('frontend.messages_edit_weather.html', **params)

    def _addParametersYahoo(self, **kwargs):
        """
        Add special parameters for yahoo weather widget *messages.weather.\**
        check https://developer.yahoo.com/yql/console/ for online editor

        :param kwargs: list of parameters for update
        """
        if 'message' in kwargs:
            location = kwargs['message'].attributes['weather.locationid']
            icons = kwargs['message'].attributes['weather.icons']
            forecast = kwargs['message'].attributes['weather.forecast']
        else:
            location = Settings.get('messages.weather.locationid')
            icons = Settings.get('messages.weather.icons')
            forecast = Settings.get('messages.weather.forecast')

        _yahooIcons = [[], ['31', '32', '33', '34', '44'], ['36'], ['21'], ['22'], ['26', '27', '28', '29', '30'],
                       ['9', '11', '12', '37', '38', '40', '45', '47'], [], ['3', '4'], [], [], [],
                       ['13', '14', '15', '16', '41', '42', '43', '46'], ['5', '6', '7', '18', '35'],
                       ['8', '10', '15', '17'], [], ['25'], ['19', '20'], ['0', '1', '2', '23', '24']]

        if not self.lastcall or datetime.datetime.now() > self.lastcall + datetime.timedelta(hours=1):
            # reload data from web
            yql_url = "https://query.yahooapis.com/v1/public/yql?{}&format=json".format(urllib.urlencode({'q': u'select * from weather.forecast where woeid = {} and u="c"'.format(location).encode('utf-8')}))

            try:
                result = urllib2.urlopen(yql_url).read()
                d = json.loads(result)
                d = flatten(d.get('query', {'results': {}}).get('results', {'channel': {}}).get('channel'))
            except urllib2.URLError:
                d = {}

            self.data.set('conditioncode', d.get('item_condition_code', ''))
            self.data.set('conditionicon', getIcon4Code(d.get('item_condition_code', 0), _yahooIcons))
            self.data.set('conditioncss', "wi wi-yahoo-{}".format(d.get('item_condition_code', '0')))

            self.data.set('condition', d.get('item_condition_text', ''))
            self.data.set('temperature', d.get('item_condition_temp', ''))

            for fcast in d.get('item_forecast', []):
                fcast['date'] = datetime.datetime.strptime(fcast.get('date'), "%d %b %Y")
                fcast['iconclass'] = "wi-yahoo-{}".format(fcast.get('code', 0))
                self.data.weather['forecast'].append(fcast)

            self.data.set('temperatureunit', d.get('units_temperature', ''))

            self.data.set('winddirection', int(d.get('wind_direction', '0')))
            self.data.set('windspeed', d.get('wind_speed', 0))
            self.data.set('windunit', d.get('units_speed', 'km/h'))
            self.data.set('humidity', d.get('atmosphere_humidity', ''))
            if d.get('atmosphere_pressure', 0) < 2000:  # fix error in pressure of webservice
                self.data.set('pressure', d.get('atmosphere_pressure', ''))
            self.data.set('sunrise', datetime.datetime(*time.strptime(d.get('astronomy_sunrise', time.time()).upper(), "%I:%M %p")[:6]))
            self.data.set('sunset', datetime.datetime(*time.strptime(d.get('astronomy_sunset', time.time()).upper(), "%I:%M %p")[:6]))
            self.data.set('location', d.get('location_city', ''))
            self.data.set('builddate', datetime.datetime.now())

        kwargs.update({'location': location, 'icons': icons, 'forecast': forecast, 'data': self.data})
        self.params = kwargs
        return kwargs

    def _addParametersOWM(self, **kwargs):
        """
        Add special parameters for open-weather-map weather widget *messages.weather.\**
        check https://www.openweathermap.org/ for online help

        weather conditions: https://www.openweathermap.org/weather-conditions

        :param kwargs: list of parameters for update
        """
        if 'message' in kwargs:
            location = kwargs['message'].attributes['weather.locationid']
            icons = kwargs['message'].attributes['weather.icons']
            forecast = kwargs['message'].attributes['weather.forecast']
        else:
            location = Settings.get('messages.weather.locationid')
            icons = Settings.get('messages.weather.icons')
            forecast = Settings.get('messages.weather.forecast')
        _owmIcons = [[], [800, ], [904, ], [905, ], [711, 801], [804, 771, 802, 803],
                     [313, 520, 521, 522, 701, 602, 300, 301, 321, 500, 531, 901, 210, 211, 212, 221], 
                     [302, 311, 312, 314, 501, 502, 503, 504], [200, 201, 202, 230, 231, 232],
                     [], [], [], [600, 601, 621, 622], [310, 511, 611, 612, 615, 616, 620], [906, ], [],
                     [903, ], [731, 761, 762, 721, 741], [900, 781, 901, 902, 957]]  # weather code mapping for png icons

        url_weather = "http://api.openweathermap.org/data/2.5/weather?id={}&units=metric&lang={}&APPID={}".format(location, current_app.config.get('LANGUAGES').keys()[0], Settings.get('messages.weather.owmkey', ''))
        url_forecast = "http://api.openweathermap.org/data/2.5/forecast?id={}&units=metric&lang={}&APPID={}".format(location, current_app.config.get('LANGUAGES').keys()[0], Settings.get('messages.weather.owmkey', ''))

        try:
            d = flatten(json.loads(urllib2.urlopen(url_weather).read()))
            f = flatten(json.loads(urllib2.urlopen(url_forecast).read()))
        except:
            d = {}
            f = {}

        self.data.set('condition', d.get('weather', [{'description': ''}])[0]['description'])
        self.data.set('conditionicon', getIcon4Code(d.get('weather', [{'id': '01'}])[0].get('id'), _owmIcons))
        self.data.set('conditioncss', "wi wi-owm-{}".format(d.get('weather', [{'id': '01'}])[0].get('id')))
        self.data.set('temperature', d.get('main_temp', 0))

        self.data.set('forecast', [])

        _ld = ""
        for fcast in f.get('list'):
            _day = datetime.datetime(*time.gmtime(fcast.get('dt', 0))[:6])
            if datetime.date.today() == _day.date():
                continue

            if _ld != _day.strftime('%Y%m%d'):
                self.data.weather['forecast'].append({'date': _day, 'low': fcast.get('main', {'temp_min': 0})['temp_min'], 'high': fcast.get('main', {'temp_max': 0})['temp_max'], 'pressure': fcast.get('main', {'pressure': 0})['pressure'], 'description': '', 'code': '', 'windspeed': 0, 'winddegree': 0})
                _ld = _day.strftime('%Y%m%d')

            if self.data.weather.get('forecast')[-1].get('low') > fcast.get('main', {'temp_min': 0})['temp_min']:
                self.data.weather.get('forecast')[-1].update({'low': fcast.get('main', {'temp_min': 0})['temp_min']})

            if self.data.weather.get('forecast')[-1].get('high') < fcast.get('main', {'temp_max': 0})['temp_max']:
                self.data.weather.get('forecast')[-1].update({'high': fcast.get('main', {'temp_max': 0})['temp_max']})

            if self.data.weather.get('forecast')[-1].get('windspeed') < fcast.get('wind', {'speed': 0}).get('speed'):
                self.data.weather.get('forecast')[-1].update({'windspeed': fcast.get('wind', {'speed': 0})['speed']})
                self.data.weather.get('forecast')[-1].update({'winddegree': fcast.get('wind', {'deg': 0})['deg']})

            self.data.weather.get('forecast')[-1].update({'pressure': (self.data.weather.get('forecast')[-1].get('pressure') + fcast.get('main', {'pressure': 0})['pressure'])/2.0})

            if _day.strftime('%H') == "12":
                self.data.weather.get('forecast')[-1].update({'description': fcast.get('weather', {'description': ''})[0]['description']})
                self.data.weather.get('forecast')[-1].update({'code': fcast.get('weather', {'id': ''})[0]['id']})
                self.data.weather.get('forecast')[-1].update({'iconclass': "wi-owm-{}".format(fcast.get('weather', {'id': ''})[0]['id'])})

        self.data.set('temperatureunit', 'C')
        self.data.set('winddirection', int(d.get('wind_deg', '0')))
        self.data.set('windspeed', d.get('wind_speed', 0))
        self.data.set('windunit', 'm/s')
        self.data.set('humidity', d.get('main_humidity', ''))
        self.data.set('pressure', d.get('main_pressure', ''))
        self.data.set('clouds', d.get('clouds_all', 0))
        self.data.set('sunrise', datetime.datetime(*time.gmtime(d.get('sys_sunrise', 0))[:6]))
        self.data.set('sunset', datetime.datetime(*time.gmtime(d.get('sys_sunset', 0))[:6]))
        self.data.set('location', d.get('name', ''))
        self.data.set('builddate', datetime.datetime.now())
        kwargs.update({'location': location, 'icons': icons, 'forecast': forecast, 'data': self.data})
        self.params = kwargs
        return kwargs

    def addParameters(self, **kwargs):
        """
        choose implementation of weather channel

        :param kwargs:
        :return: list of parameters, weather dict added
        """
        if kwargs.get('message', {'weather.type': Settings.get('messages.weather.type', '')}).get('weather.type') in ['', 'yahoo']:
            return self._addParametersYahoo(**kwargs)
        else:
            return self._addParametersOWM(**kwargs)

    @staticmethod
    def action(**kwargs):
        if kwargs.get('action') == 'findcity':
            """
            get list of weather stations for given weather channel
            """
            config = {'settings': Settings, 'data': []}
            cityname = kwargs.get('cityname')

            if kwargs.get('weathertype', '') == 'owm':
                if cityname.isnumeric():  # zip code given -> start request
                    url_zip = "http://api.zippopotam.us/{}/{}".format(current_app.config.get('LANGUAGES').keys()[0], cityname)
                    try:
                        d = json.loads(urllib2.urlopen(url_zip).read())
                        cityname = d.get('places', [])[0]['place name']
                    except:
                        config['data'] = []
                try:
                    with codecs.open('emonitor/modules/messages/inc/weather/city.list.de.json', 'r', encoding="utf-8") as f:
                        for l in (ifilter(lambda line: cityname.lower() in line.lower(), f)):
                            d = eval(l.replace('\r\n', ''))
                            config['data'].append({'name': u"{}".format(d.get('name').decode('utf-8')), 'lat': d.get('coord', {'lat': ''}).get('lat'), 'lon': d.get('coord', {'lon': ''}).get('lon'), 'id': d.get('_id'), 'country': d.get('country')})
                except:
                    config['data'] = []

            elif kwargs.get('weathertype', '') == 'yahoo':
                baseurl = "https://query.yahooapis.com/v1/public/yql?"
                if cityname.isnumeric():  # zip code given -> start request
                    yql_query = u'select name, locality1.woeid, locality1.content, centroid from geo.places where text="{}" and locality1.type="Town" and country.code="{}"'.format(cityname, current_app.config.get('LANGUAGES').keys()[0].upper())
                    yql_url = baseurl + urllib.urlencode({'q': yql_query}) + "&format=json"
                    try:
                        d = json.loads(urllib2.urlopen(yql_url).read())
                        d = flatten(d.get('query', {'results': {}}).get('results', {}))
                    except:
                        d = {}
                    config['data'].append({'name': d.get('place_locality1_content', ''), 'lat': d.get('place_centroid_latitude', ''), 'lon': d.get('place_centroid_longitude', ''), 'id': d.get('place_locality1_woeid', ''), 'country': current_app.config.get('LANGUAGES').keys()[0].upper()})
                else:
                    yql_query = 'select name, woeid, centroid from geo.places where text="*%s*, %s"' % (cityname.encode('utf8'), current_app.config.get('LANGUAGES').keys()[0].upper())
                    yql_url = baseurl + urllib.urlencode({'q': yql_query}) + "&format=json"
                    try:
                        d = json.loads(urllib2.urlopen(yql_url).read())
                        d = d.get('query', {'results': {}})
                    except:
                        d = {}

                    if d.get('count', 0) == 1:
                        d = d.get('results').get('place')
                        config['data'].append(
                            {'name': d.get('name', ''), 'lat': d.get('centroid', {'latitude': ''}).get('latitude'), 'lon': d.get('centroid', {'longitude': ''}).get('longitude'), 'id': d.get('woeid', ''), 'country': current_app.config.get('LANGUAGES').keys()[0]})
                    else:
                        for p in d.get('results').get('place'):
                            config['data'].append({'name': p.get('name', ''), 'lat': p.get('centroid', {'latitude': ''}).get('latitude'), 'lon': p.get('centroid', {'longitude': ''}).get('longitude'), 'id': p.get('woeid', ''), 'country': current_app.config.get('LANGUAGES').keys()[0]})
            kwargs.update(config)
            return render_template('frontend.messages_weather_map.html', **kwargs)
        return ""
