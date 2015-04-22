import yaml
import datetime
import pytz
import logging
from emonitor.extensions import db, scheduler, classes, monitorserver
from messageutils import calcNextStateChange, MessageTrigger
from emonitor.modules.messages.message_text import TextWidget  # MessageText
from emonitor.modules.messages.messagetype import MessageType

logger = logging.getLogger(__name__)


class Messages(db.Model):
    """Messages class"""
    __tablename__ = 'messages'
    __table_args__ = {'extend_existing': True}

    ACTIVE_MESSAGES = []

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    remark = db.Column(db.TEXT)
    startdate = db.Column(db.DATETIME)
    enddate = db.Column(db.DATETIME)
    state = db.Column(db.Integer)
    _monitors = db.Column('monitors', db.String(32))
    _type = db.Column('type', db.String(32))
    _attributes = db.Column('attributes', db.TEXT)

    def __init__(self, name, remark, startdate, enddate, state, mtype=TextWidget('dd')):
        self.name = name
        self.remark = remark
        self.startdate = startdate
        self.enddate = enddate
        self.state = state
        self.type = mtype

    def __str__(self):
        return "<Message %s> %s: %s-%s, visible: %s, on monitor: %s" % (self.id, self.name, self.startdate, self.enddate, self.currentState, self.monitors)

    @property
    def attributes(self):
        """
        Load attributes from database in yaml format

        :return: attributes as dict
        """
        try:
            return yaml.load(self._attributes)
        except AttributeError:
            return ""

    @attributes.setter
    def attributes(self, val):
        """
        Store given attributes in yaml format in database

        :param val: value for attribute
        """
        self._attributes = yaml.safe_dump(val, encoding='utf-8')

    def get(self, attribute, default=""):
        """
        Get attribute value if found in definition of object, default else

        :param attribute: name of attribute as string
        :param optional default: use default value if attribute not found
        :return: value of attribute or default
        """
        if attribute in self.attributes:
            return self.attributes[attribute]
        attr = attribute.split('.')
        if attr[0] in self.attributes:
            if len(attr) == 2:
                if attr[1] in self.attributes[attr[0]]:
                    return self.attributes[attr[0]][attr[1]]
            else:
                return self.attributes[attr[0]]
        return default

    def set(self, attribute, value):
        """
        Set attribute with given value

        :param attribute: name of attribute
        :param value: value for attribute
        """
        self.attributes[attribute] = value

    @property
    def type(self):
        """
        Get message type as MessageType class object

        :return: :py:class:`emonitor.modules.messages.messagetype.MessageType`
        """
        if self._type == '':
            self._type = classes.get('settings').get('messages.base.type')
        impl = filter(lambda x: x[0].split('.')[0] == self._type, MessageType.getMessageTypes())
        if len(impl) == 1:
            return impl[0][1]
        return None

    @type.setter
    def type(self, messageType):
        """
        Set typename for message and store value in type column of database table

        :param messageType: use messagetype object or objectname
        """
        self._type = str(messageType).split('.')[0]

    @property
    def monitors(self):
        """
        Getter for monitors property

        :return: list of monitor ids
        """
        try:
            return [int(m) for m in self._monitors.split(',')]
        except ValueError:
            return []

    @monitors.setter
    def monitors(self, monitors):
        """
        Setter for monitors property

        :param monitors: list of monitor ids
        """
        self._monitors = ','.join(monitors)

    @property
    def currentState(self, timestamp=None):
        """
        Return current state of message, use calculated value for next state change if defined

        :param optional timestamp: use given timestamp or now as reference
        :return: boolean
        """
        if self.attributes['cron']:
            if not timestamp:
                timestamp = datetime.datetime.now(tz=pytz.timezone('CET'))
            return not calcNextStateChange(timestamp, self.attributes['cron'])[1]
        return True

    @staticmethod
    def getMessages(id=0, state=-1):
        """
        Get messages filtered by criteria

        :param optional id: id of message
        :param optional state: -1: all messages, else only messages with given state
        :return: :py:class:`emonitor.modules.messages.messages.Messages` list
        """
        if id == 0:
            if state == -1:
                return db.session.query(Messages).order_by('messages.startdate').all()
            else:
                return db.session.query(Messages).filter(Messages.state == state).order_by('messages.startdate').all()
        else:
            return db.session.query(Messages).filter(Messages.id == int(id)).first()

    @staticmethod
    def getActiveMessages():
        """
        Filters only startdate, enddate and state > 0

        :return: :py:class:`emonitor.modules.messages.messages.Messages` list
        """
        return db.session.query(Messages).filter(Messages.state > 0).filter(Messages.startdate <= datetime.datetime.now()).filter(Messages.enddate >= datetime.datetime.now()).order_by(Messages.startdate.asc()).all()

    @staticmethod
    def initMessageTrigger():
        """Init scheduler tasks for messages"""
        job = scheduler.add_job(Messages.doMessageTrigger, name="messages", id="messages", trigger=MessageTrigger(Messages.getActiveMessages(), minutes=60))
        if len(job.trigger.messagelist) == 0:  # pause job if no active messages
            job.pause()
        logger.info('scheduler job init done, next run at %s' % job.next_run_time)

    @staticmethod
    def updateMessageTrigger():
        """Update message trigger after changes in message objects and update next fire time"""
        job = scheduler.get_job(job_id="messages")
        job.trigger.messagelist = Messages.getActiveMessages()  # update message list for new firetime
        if len(job.trigger.messagelist) == 0:
            job.pause()  # pause job if no active messages
        else:
            job.resume()  # reactivate if active messages
        scheduler.modify_job(job_id="messages", next_run_time=job.trigger.get_next_fire_time('', ''))
        scheduler.app.logger.info('message trigger: update message trigger, next run %s' % job.next_run_time)
        monitorserver.sendMessage('0', 'reset')  # refresh monitor layout

    @staticmethod
    def doMessageTrigger():
        """Run every state-change of a message and update messagelist for displays and call monitors"""
        scheduler.app.logger.info('message trigger: run state changes at %s' % datetime.datetime.now())
        Messages.updateMessageTrigger()  # update trigger and calculate next run
