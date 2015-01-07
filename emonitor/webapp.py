import os
from alembic import util as alembicutil
from sqlalchemy.exc import OperationalError
from flask import Flask, request, render_template, current_app
from .extensions import alembic, db, login_manager, babel, classes, cache, events, scheduler, monitorserver, signal, printers
from .user import User

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
    APP_VERSION = '0.3.2'                                  # current version
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    LANGUAGE_DIR = 'emonitor/web/translations'            # relative path of default templates
    DEFAULTZOOM = 12                                      # used for map-data
    LANGUAGES = {'de': 'Deutsch'}
    ALEMBIC = {'script_location': 'alembic'}             # alembic base path
    DB_VERSION = 'a35c7dbf502'                           # version of database

    # monitorserver
    MONITORSERVER_ANY = "0.0.0.0"
    MONITORSERVER_MCAST_ADDR = "224.168.2.9"
    MONITORSERVER_MCAST_PORT = 1600


def create_app(config=None, app_name=None, blueprints=None):
    """
    Create app with given configuration and add blueprints

    :param config: configuration from :py:class:`emonitor.webapp.DEFAULT_CONFIG` and config file
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
    app.config.from_pyfile('emonitor.cfg', silent=True)

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

    with app.app_context():
        try:
            db.reflect()  # check init
            db.create_all()
            alembic.stamp()  # set stamp to latest version
        except:
            if alembic.context.get_current_revision() != current_app.config.get('DB_VERSION'):  # update version
                try:
                    alembic.upgrade(current_app.config.get('DB_VERSION'))
                except (alembicutil.CommandError, OperationalError):
                    pass
                finally:
                    alembic.stamp()

    # babel
    babel.init_app(app)

    # add default classes
    from emonitor.monitorserver import MonitorLog
    #from modules.settings.department import Department
    classes.add('monitorlog', MonitorLog)
    #classes.add('department', Department)

    # flask-cache
    cache.init_app(app)

    # signals
    signal.init_app(app)

    #events
    events.init_app(app)
    events.addEvent('default', handlers=[], parameters=[])

    # scheduler
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
    if User.count() == 0:
        User.getUsers(1)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)


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

    #if app.debug or app.testing:
    #    # Skip debug and test mode. Just check standard output.
    #    return
    
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler('%swebapp.log' % app.config.get('PATH_DATA'), maxBytes=1024 * 1024 * 100, backupCount=20)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(app.config.get('LOGLEVEL', logging.ERROR))
   

def configure_hook(app):
    #@app.before_request
    #def before_request():
    #    pass
        
    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(app.config.get('LANGUAGES').keys())


def configure_handlers(app):

    #@app.before_request
    #def before_request():
    #    print "before_request"

    #@app.after_request
    #def after_request(response):
    #    print "after_request", response
    #    return response

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("errors403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors404.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors500.html"), 500
