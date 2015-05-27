import os
import sys
import logging
from alembic import util as alembicutil
from sqlalchemy.exc import OperationalError
from flask import Flask, request, render_template, current_app
from .extensions import alembic, db, login_manager, babel, cache, events, scheduler, monitorserver, signal, printers
from .user import User

from emonitor import __version__
from emonitor.widget.widget import widget
from emonitor.frontend.frontend import frontend
from emonitor.modules import modules
from emonitor.admin.admin import admin
from emonitor.onlinehelp.onlinehelp import onlinehelp
from emonitor.login.login import login
from emonitor.tileserver.tileserver import tileserver
from emonitor.monitor.monitor import monitor

# For import *
__all__ = ['create_app']
DEFAULT_BLUEPRINTS = (
    widget,
    admin,
    monitor,
    frontend,
    onlinehelp,
    login,
    modules,
    tileserver,
)


class DEFAULT_CONFIG(object):
    """ default configuration if no .cfg file found """
    
    PROJECT = "eMonitor"
    DEBUG = False
    TESTING = False
    
    #PORT = 8080                                          # default webserver port
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 60
    SECRET_KEY = 'secret key'                             # default key, overwrite in cfg
    APP_VERSION = __version__                             # current version
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    LANGUAGE_DIR = 'emonitor/web/translations'            # relative path of default templates
    DEFAULTZOOM = 12                                      # used for map-data
    LANGUAGES = {'de': 'Deutsch'}
    ALEMBIC = {'script_location': 'alembic'}              # alembic base path
    DB_VERSION = '2b56ad35fcd7'                           # version of database

    # monitorserver
    MONITORSERVER_ANY = "0.0.0.0"
    MONITORSERVER_MCAST_ADDR = "224.168.2.9"
    MONITORSERVER_MCAST_PORT = 1600

    OBSERVERINTERVAL = 2                                # interval for folderobserver
    MONITORPING = 2                                     # monitor ping in minutes


def create_app(config=None, app_name=None, blueprints=None):
    """
    Create app with given configuration and add blueprints

    :param config: configuration from :py:class:`emonitor.app.DEFAULT_CONFIG` and config file
    :param app_name: name of app as string
    :param blueprints: list of blueprints to init
    :return: app object :py:class:`Flask`
    """
    if not app_name:
        app_name = DEFAULT_CONFIG.PROJECT

    app = Flask(app_name, template_folder='emonitor/web/templates')
    app.flashtypes = []
    configure_app(app, config)
    configure_logging(app)
    configure_extensions(app)
    if not blueprints:
        configure_blueprints(app, DEFAULT_BLUEPRINTS)
    else:
        configure_blueprints(app, blueprints)
    configure_hook(app)
    configure_handlers(app)
    return app

    
def configure_app(app, config=None):
    """Different ways of configurations."""

    if not config:
        app.config.from_object(DEFAULT_CONFIG)
    else:
        app.config.from_object(config)
    try:
        app.config.from_pyfile('emonitor.cfg', silent=False)
    except IOError:
        print "config file 'emonitor.cfg' not found"
        sys.exit()

    # create missing directories of config
    for p in [path for path in app.config.keys() if path.startswith('PATH')]:
        if not os.path.exists(app.config[p]):
            os.makedirs(app.config[p])

recorded = []


def configure_extensions(app):
    """
    Confgure all extensions with current app object

    :param app: :py:class:`Flask`
    """
    # alembic
    alembic.init_app(app)

    # flask-sqlalchemy
    db.init_app(app)
    db.app = app
    db.create_all()

    with app.app_context():
        if alembic.context.get_current_revision() != current_app.config.get('DB_VERSION'):  # update version
            try:
                alembic.upgrade(current_app.config.get('DB_VERSION'))
            except (alembicutil.CommandError, OperationalError):
                pass
        db.reflect()  # check init
        db.create_all()
        alembic.stamp()  # set stamp to latest version

    # babel
    babel.init_app(app)

    # flask-cache
    cache.init_app(app)

    # signals
    signal.init_app(app)

    #events
    events.init_app(app)
    events.addEvent('default', handlers=[], parameters=[])

    # scheduler
    if scheduler._stopped:
        scheduler.start()
    scheduler.initJobs(app)

    # monitorserver
    monitorserver.init_app(app)
    monitorserver.sendMessage('0', 'reset')

    # printers
    printers.init_app(app)
    
    # flask-login
    login_manager.login_view = 'login.loginform'
    login_manager.login_message = "admin.login.needed"
    login_manager.unauthorized_handler = "frontend.login_page"
    login_manager.init_app(app)

    # jinja2 filters
    from utils import getmarkdown, getreStructuredText
    app.jinja_env.filters['markdown'] = getmarkdown
    app.jinja_env.filters['rst'] = getreStructuredText

    # user
    if User.query.count() == 0:
        User.getUsers(1)
    
    @login_manager.user_loader
    def load_user(id):
        return User.getUsers(userid=id)

    # add global elements
    from emonitor.scheduler import eMonitorIntervalTrigger
    from emonitor.modules.settings.settings import Settings
    try:
        _jping = scheduler.add_job(monitorserver.getClients, trigger=eMonitorIntervalTrigger(minutes=int(Settings.get('monitorping', app.config.get('MONITORPING', 2)))), name='monitorping')
    except:
        _jping = scheduler.add_job(monitorserver.getClients, trigger=eMonitorIntervalTrigger(minutes=int(app.config.get('MONITORPING', 2))), name='monitorping')

    if str(Settings.get('monitorping', app.config.get('MONITORPING'))) == '0':
        _jping.pause()
    from emonitor.observer import observeFolder
    try:
        _jobserver = scheduler.add_job(observeFolder, trigger=eMonitorIntervalTrigger(seconds=int(Settings.get('observer.interval', app.config.get('OBSERVERINTERVAL', 2)))), kwargs={'path': app.config.get('PATH_INCOME', app.config.get('PATH_DATA'))}, name='observerinterval')
    except ValueError:
        _jobserver = scheduler.add_job(observeFolder, trigger=eMonitorIntervalTrigger(seconds=int(app.config.get('OBSERVERINTERVAL', 2))), kwargs={'path': app.config.get('PATH_INCOME', app.config.get('PATH_DATA'))}, name='observerinterval')
    if str(Settings.get('observer.interval', app.config.get('OBSERVERINTERVAL'))) == '0':
        _jobserver.pause()


def configure_blueprints(app, blueprints):
    """
    Configure blueprints with app configuration

    :param app: :py:class:`Flask`
    :param blueprints: list of blueprints
    """
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
        if hasattr(blueprint, 'init_app'):
            blueprint.init_app(app)


def configure_logging(app):
    """
    Configure logging

    :param app: :py:class:`Flask`
    """
    from logging.handlers import RotatingFileHandler

    class MyFilter(object):
        def __init__(self, level):
            self.__level = level

        def filter(self, logRecord):
            return logRecord.levelno == self.__level

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    accesslogger = logging.getLogger('werkzeug')

    if app.debug:
        accesslogger.propagate = False
        file_handler = RotatingFileHandler('{}{}-access.log'.format(app.config.get('PATH_DATA'), app.name), maxBytes=1024 * 1024 * 100, backupCount=20)
        file_handler.setFormatter(formatter)
        accesslogger.addHandler(file_handler)
        app.logger.addHandler(accesslogger)

        # set debug mode to all other loggers of emonitor, use loglevel definition of emonitor.cfg
        for l in [l for l in logging.Logger.manager.loggerDict if l.startswith(app.name.lower())]:
            lo = logging.getLogger(l)
            if lo.level > logging.DEBUG:
                lo.setLevel(app.config.get('LOGLEVEL', logging.DEBUG))
    else:
        accesslogger.setLevel(logging.ERROR)

    logger = logging.getLogger('alembic.migration')
    logger.setLevel(logging.ERROR)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler('%s%s.log' % (app.config.get('PATH_DATA'), app.name), maxBytes=1024 * 1024 * 100, backupCount=20)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    file_handler = RotatingFileHandler('%s%s-error.log' % (app.config.get('PATH_DATA'), app.name), maxBytes=1024 * 1024 * 100, backupCount=20)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(MyFilter(logging.ERROR))
    file_handler.setLevel(logging.ERROR)
    logger.addHandler(file_handler)


def configure_hook(app):
    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(app.config.get('LANGUAGES').keys())


def configure_handlers(app):
    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("errors403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors404.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        try:
            from emonitor.extensions import db
            db.rollback()
        except:
            pass
        return render_template("errors500.html"), 500
