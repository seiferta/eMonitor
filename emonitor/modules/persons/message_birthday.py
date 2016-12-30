import datetime
import math
from collections import OrderedDict
from flask import render_template
from emonitor.extensions import babel
from emonitor.modules.persons.persons import Person
from emonitor.widget.monitorwidget import MonitorWidget
from emonitor.modules.settings.settings import Settings

__all__ = ['BirthdayWidget']

babel.gettext(u'message.birthday')


class BirthdayWidget(MonitorWidget):
    """Widget for text messages"""
    __info__ = {'icon': 'fa-birthday-cake'}
    __fields__ = ['orientation', 'number']
    template = 'widget.message.birthday.html'
    size = (5, 4)

    def __repr__(self):
        return "birthday"

    def getAdminContent(self, **params):
        """
        Get content for admin area to config all parameters of message type object

        :param params: list of all currently used parameters
        :return: rendered template of text message type
        """
        params.update({'settings': Settings})
        return render_template('admin.message.birthday.html', **params)

    def getMonitorContent(self, **params):
        """
        Get Content for monitor of birthday type message

        :param params: list of all currently used parameters
        :return: html content for monitor
        """
        self.addParameters(**params)
        return self.getHTML('', **params)

    def getEditorContent(self, **params):
        """
        Get content for frontend configuration of birthday type message

        :param params: list of all currently used parameters
        :return: renderd template of birthday message type
        """
        params.update({'settings': Settings})
        return render_template('frontend.messages_edit_birthday.html', **params)

    def addParameters(self, **kwargs):
        """
        Add special parameters for birthday widget *messages.birthday.\**
        :param kwargs: list of parameters for update
        """
        if 'message' in kwargs:
            content = kwargs['message'].get('content')
            template = kwargs['message'].get('template')
            n = int(kwargs['message'].get('number'))
            orientation = kwargs['message'].get('orientation')
        else:
            content = Settings.get('messages.birthday.content')
            template = ""  # todo define templates
            n = int(Settings.get('messages.birthday.number', 20))
            orientation = Settings.get('messages.birthday.orientation', 20)

        persons = sorted(Person.getPersons(onlyactive=True), key=lambda p: p.birthday)
        p = [(val.birthday - int(datetime.datetime.now().strftime('%j')), idx, persons[idx].lastname, persons[idx].birthdate) for (idx, val) in enumerate(persons)]
        idx = min(filter(lambda x: x[0] % 365 >= 0, p))

        person = OrderedDict()
        try:
            for i in range(idx[1] - (n / 2) + 1, idx[1] + (n / 2) + 2):
                _p = persons[i % (len(p))]
                if _p.birthdate.strftime('%d.%m.') not in person.keys():
                    person[_p.birthdate.strftime('%d.%m.')] = []
                person[_p.birthdate.strftime('%d.%m.')].append(_p)
            for _p in persons:
                if _p.birthdate.strftime('%d.%m.') in person.keys() and _p not in person[_p.birthdate.strftime('%d.%m.')]:
                    person[_p.birthdate.strftime('%d.%m.')].append(_p)
        except:
            pass

        kwargs.update({'content': content, 'template': template, 'persons': person, 'daynum': int((datetime.datetime.now()).strftime('%j')), 'orientation': orientation})
        self.params = kwargs
