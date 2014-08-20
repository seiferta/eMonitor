from emonitor.modules.alarms.alarmutils import AlarmFaxChecker

__all__ = ['DummyAlarmFaxChecker']


class DummyAlarmFaxChecker(AlarmFaxChecker):
    __name__ = "Dummy"
    __version__ = '0.1'

    fields = {}

    def getEvalMethods(self):
        return []
