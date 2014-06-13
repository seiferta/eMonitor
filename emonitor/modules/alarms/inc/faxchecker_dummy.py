import re
import difflib
from emonitor.modules.alarms.alarmutils import AlarmFaxChecker
from emonitor.extensions import classes

__all__ = ['DummyAlarmFaxChecker']


class DummyAlarmFaxChecker(AlarmFaxChecker):
    __name__ = "Dummy"
    __version__ = '0.1'

    fields = {}

    def getEvalMethods(self):
        return []

