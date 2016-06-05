import yaml
import logging
from emonitor.extensions import events, babel, db
from emonitor.modules.events.eventhandler import Eventhandler
from emonitor.modules.alarms.alarm import Alarm
from emonitor.modules.settings.settings import Settings
from emonitor.modules.persons.persons import Person

logger = logging.getLogger(__name__)


class Communicator:
    def sendMessage(self, addressee, message):
        pass

    def getUsers(self):
        return []


class TelegramBot(Communicator):
    """
    telegram connector class
    """
    __personidentifier__ = 'telegramid'
    app = None
    logger = logging.getLogger('telegram.ext')
    logger.setLevel(logging.CRITICAL)
    logger = logging.getLogger('telegram.bot')
    logger.setLevel(logging.ERROR)
    users = Person

    def __init__(self, **kwargs):
            # Create the EventHandler and pass it your bot's token.
            from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
            from telegram.error import InvalidToken, Unauthorized, NetworkError

            self.updater = Updater(kwargs.get('token', ''))
            self.active = False
            self.botname = None

            TelegramBot.app = kwargs.get('app', None)

            try:
                if self.updater.bot.getMe():
                    self.botname = self.updater.bot.getMe().name
                # on different commands - answer in Telegram
                self.updater.dispatcher.addHandler(CommandHandler("start", TelegramBot.msg_start, pass_args=True))
                self.updater.dispatcher.addHandler(CommandHandler("Start", TelegramBot.msg_start, pass_args=True))
                self.updater.dispatcher.addHandler(CommandHandler("hilfe", TelegramBot.msg_help, pass_args=True))
                self.updater.dispatcher.addHandler(CommandHandler("Hilfe", TelegramBot.msg_help, pass_args=True))
                self.updater.dispatcher.addHandler(CallbackQueryHandler(TelegramBot.msg_responder))
                self.updater.start_polling()
            except InvalidToken:
                self.logger.error('invalid telegram token {}'.format(kwargs.get('token', '')))
                self.updater = Updater(kwargs.get('token', ''))
            except Unauthorized:
                self.logger.error('unauthorized telegram token {}'.format(kwargs.get('token', '')))
            except NetworkError:
                self.logger.error('network error with telegram token {}'.format(kwargs.get('token', '')))

    def updateToken(self, token=None):
        """
        update token after changes
        :return: botname
        """
        from telegram.ext import Updater
        from telegram.error import Unauthorized, NetworkError
        updater = Updater(token or Settings.get('telegramkey'))
        self.updater = updater
        self.botname = None
        try:
            if updater.bot.getMe():
                self.botname = updater.bot.getMe().name

        except Unauthorized:
            self.botname = None
        except NetworkError:
            self.logger.error("network error")

        return self.botname

    def start(self):
        """
        start update handler for telegram messages
        """
        self.logger.debug('telegram bot updater started')
        self.active = True
        try:
            self.updater.idle()
        except:
            self.active = True

    def stop(self):
        """
        stop update handler for telegram messages
        """
        self.active = False
        self.updater.stop()

    def state(self):
        return self.active

    def getUsers(self):
        """
        get list of users for telegram messenger
        :return: list of persons
        """
        return Person.query.filter(self.users._options.like('%{}%'.format(self.__personidentifier__))).all()

    def sendMessage(self, addressee, message, **kwargs):
        """
        send message via telegram messenger
        :param addressee: id of user or group
        :param message: text message
        :param kwargs: additional attributes, 'reply_markup' defined
        """
        self.updater.bot.sendMessage(addressee, message, parse_mode='Markdown', reply_markup=kwargs.get('reply_markup', None))

    def sendVenue(self, addressee, message, **kwargs):
        """
        send venue of current item
        :param addressee: id of user or group
        :param message: text message for header
        :param kwargs: deliver 'lat', 'lng', 'address', 'reply_markup'
        """
        self.updater.bot.sendVenue(addressee, kwargs.get('lat'), kwargs.get('lng'), message, kwargs.get('address'), reply_markup=kwargs.get('reply_markup', None))

    def sendFile(self, addressee, document, **kwargs):
        """
        send file for given parameters
        :param addressee: id of user or group
        :param document: document pointer to document to send
        :param kwargs: additional attributes, 'filename', 'caption'
        """
        self.updater.bot.sendDocument(addressee, document, filename=kwargs.get('filename', None), caption=kwargs.get('caption', None))

    @staticmethod
    def msg_start(bot, update, **kwargs):
        """
        send start message and add user id to emonitor user if found
        :param bot:
        :param update:
        :param kwargs:
        """
        for person in TelegramBot.users.getPersons():
            if person.firstname == update.message.from_user['first_name'] and person.lastname == update.message.from_user['last_name']:
                TelegramBot.logger.info('add telegramid {} to user {} {}'.format(update.message.from_user['id'], person.firstname, person.lastname))
                _additional = person.options
                _additional['telegramid'] = update.message.from_user['id']
                person._options = yaml.safe_dump(_additional, encoding='utf-8')
                db.session.commit()

        msgtext = Settings.get('telegramsettings')['welcomemsg'] or babel.gettext('telegram.default.welcomemsg')
        bot.sendMessage(update.message.chat_id, text=msgtext.format(vorname=update.message.from_user.first_name, nachname=update.message.from_user.last_name))
        TelegramBot.logger.info('send message from "msg_start" to {} {}'.format(update.message.from_user.first_name, update.message.from_user.last_name))

    @staticmethod
    def msg_responder(bot, update, **kwargs):
        """
        Responder for incoming messages
        :param bot:
        :param update:
        :param kwargs:
        """
        if update.callback_query.data.startswith('file_'):  # send file
            bot.sendDocument(update.callback_query.message.chat_id, open(TelegramBot.app.config.get('PATH_DONE') + update.callback_query.data.split('_')[-1], 'rb'), 'details.pdf', 'details')

        elif update.callback_query.data.startswith('details_'):  # details_[type]_[id]
            if update.callback_query.data.split('_')[1] == 'alarm':
                from telegram import InlineKeyboardMarkup, InlineKeyboardButton
                args = {'id': int(update.callback_query.data.split('_')[-1]), 'style': 'details', 'addressees': [update.callback_query.message.chat_id], 'keyboard': InlineKeyboardMarkup, 'button': InlineKeyboardButton}
                attrs = Alarm.getExportData('telegram', **args)
                for addressee in [update.callback_query.message.chat_id]:
                    bot.sendMessage(addressee, attrs['details'], reply_markup=attrs['reply'], parse_mode='Markdown')
                return

        elif update.callback_query.data.startswith('location_'):
            bot.sendLocation(update.callback_query.message.chat_id, update.callback_query.data.split('_')[1], update.callback_query.data.split('_')[2])

    @staticmethod
    def msg_help(bot, update, **kwargs):
        """
        send information about the bot
        :param bot:
        :param update:
        :param kwargs:
        """
        msgtext = Settings.get('telegramsettings')['helpmsg'] or babel.gettext('telegram.default.helpmsg')
        bot.sendMessage(update.message.chat_id, msgtext, parse_mode='Markdown')
        TelegramBot.logger.debug("help_msg sent.")


class Mailer(Communicator):

    def __init__(self, **kwargs):
        pass


class Communication(object):
    """
    collector class for all communication interfaces
    """
    app = None

    def __init__(self, app=None):
        self.__dict__ = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        Communication.app = app

        try:  # try telegram
            import telegram
            self.__dict__['telegram'] = TelegramBot(app=app, token=Settings.get('telegramsettings')['telegramkey'] or app.config.get('TELEGRAMKEY'))
        except TypeError:
            Settings.set('telegramsettings', {'telegramkey': ''})
            self.__dict__['telegram'] = None
        except ImportError:
            logger.error("error telegram")
            self.__dict__['telegram'] = None

        try:  # try mail
            # TODO: add Mail communicator
            pass
            self.__dict__['mail'] = Mailer
        except ImportError:
            self.__dict__['mail'] = None
            logger.error("error Mail")
            # Mail = None

        app.extensions['communication'] = self

        logger.info("{} Communicator(s) loaded: {}".format(len(self.__dict__.keys()), ", ".join(self.__dict__.keys())))
        events.addHandlerClass('*', 'emonitor.communication.Communication', Communication.handleEvent, ['in.sendertype', 'in.group', 'in.id', 'in.style'])

    def updateCommunicator(self, commtype):
        for key, communicator in self.__dict__.items():
            if key == commtype:
                self.__dict__[key] = TelegramBot(app=Communication.app, token=Settings.get('telegramsettings')['telegramkey'] or Communication.app.config.get('TELEGRAMKEY'))
                return self.__dict__[key]

    def _teardown(self, **kwargs):
        pass

    @staticmethod
    def handleEvent(eventname, **kwargs):
        hdl = [hdl for hdl in Eventhandler.getEventhandlers(event=eventname) if hdl.handler == 'emonitor.communication.Communication'][0]
        if hdl:
            from emonitor.extensions import communication
            params = {}
            for p in hdl.getParameterValues('in'):
                params[p[0].split('.')[-1]] = p[1]
            if params["sendertype"] == 'telegram':
                for group, members in Settings.getYaml('telegramsettings').__dict__['groups'].items():
                    if group == params['group']:
                        from telegram import InlineKeyboardMarkup, InlineKeyboardButton
                        args = {'id': int(kwargs.get('alarmid')), 'style': params['style'], 'addressees': members[:-1], 'keyboard': InlineKeyboardMarkup, 'button': InlineKeyboardButton}
                        attrs = Alarm.getExportData('telegram', **args)
                        for member in members[:-1]:
                            if params['id'] == 'alarmid':  # send alarm details with location
                                try:
                                    if params.get('style') in ['text', 'details']:
                                        communication.telegram.sendMessage(member, attrs['details'], reply_markup=attrs['reply'])
                                    elif params.get('style') == 'venue':
                                        communication.telegram.sendVenue(member, attrs['text'], lat=attrs['lat'], lng=attrs['lng'], address=attrs['address'], reply_markup=attrs['reply'])
                                except:
                                    print "error handleEvent"
                                return kwargs

            elif params["sendertype"] == 'mailer':
                # TODO: implement mail notification
                pass

        return kwargs
