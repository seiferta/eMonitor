from datetime import datetime, timedelta
import pytz
from tzlocal import get_localzone
from apscheduler.triggers.base import BaseTrigger
from apscheduler.util import timedelta_seconds, astimezone


def calcNextStateChange(timestamp, params):
    """
    Calculate next state change for given parameters

    :param timestamp: timestamp for calculation
    :param params: dict with string values, keys: *day_of_week*, *hour*
    :return: :py:class:`datetime.datetime`, state (*True* = activate, *False* = deactivate)
    """
    next_state = False
    next_change = None

    if 'day_of_week' in params and params['day_of_week'] != '*':  # weekday
        l = [x in map(int, params['day_of_week'].strip().split(',')) for x in range(0, 7)]
        x = timestamp.weekday()

        if l[timestamp.weekday()]:  # actual day status ON
            next_change = pytz.timezone('CET').localize(datetime(year=timestamp.year, month=timestamp.month, day=timestamp.day))
        else:
            while True and x < 14:
                if (not l[timestamp.weekday()] and l[x % 7]) != (l[timestamp.weekday()] and not l[x % 7]):
                    break
                x += 1
            next_change = pytz.timezone('CET').localize(datetime(year=timestamp.year, month=timestamp.month, day=(timestamp.day + (x - timestamp.weekday()) % 7)))
            next_state = l[x % 7]  # True = activate, False = deacivate

    if 'hour' in params and params['hour'] != '*':  # calculate next switch hour
        l = [x in map(int, params['hour'].strip().split(',')) for x in range(0, 24)]
        x = timestamp.hour

        while True and x < 48:
            if (not l[timestamp.hour] and l[x % 24]) != (l[timestamp.hour] and not l[x % 24]):
                break
            x += 1
        if next_state:  # if current state = deactivated, deliver first active hour
            x = map(int, params['hour'].strip().split(','))[0]

        if not next_change:
            next_change = pytz.timezone('CET').localize(datetime(year=timestamp.year, month=timestamp.month, day=timestamp.day))
        next_change += timedelta(hours=x)
        next_state = l[x % 24]

    if not next_change:
        next_change = pytz.timezone('CET').localize(datetime(year=timestamp.year, month=timestamp.month, day=timestamp.day) + timedelta(days=1))

    return next_change, next_state


class MessageTrigger(BaseTrigger):
    """
    Use own trigger class for messages.
    This trigger fires only at changes of messages states
    """
    __slots__ = 'timezone', 'interval', 'messagelist'

    def __init__(self, messagelist, hours=0, minutes=0, timezone=None):
        self.messagelist = messagelist
        self.interval = timedelta(hours=hours, minutes=minutes)
        self.interval_length = timedelta_seconds(self.interval)
        if self.interval_length == 0:
            self.interval = timedelta(minutes=60)
            self.interval_length = 1

        if timezone:
            self.timezone = astimezone(timezone)
        else:
            self.timezone = get_localzone()

    def get_next_fire_time(self, previous_fire_time, now):
        """Get next event datetime for changes"""
        times = [(datetime.now(tz=pytz.timezone('CET')) + (self.interval * 12), True)]
        for msg in self.messagelist:
            times.append(calcNextStateChange(datetime.now(tz=pytz.timezone('CET')), msg.attributes['cron']))  # (next_change_time, status)
        return self.timezone.normalize(min([t[0] for t in times]))

    def __str__(self):
        ret = '*message trigger* with %s active messages:\n\n' % len(self.messagelist)
        for m in self.messagelist:
            ret += "- %s\n" % m
        return ret

    def __repr__(self):
        return "<%s (number of messages=%r, interval=%r)>" % (self.__class__.__name__, len(self.messagelist), self.interval)
