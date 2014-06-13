import os
from flask import Flask, request, render_template, message_flashed
from .extensions import db, login_manager, babel, classes, cache, events, scheduler, monitorserver, signal, printers
from .user import User

from emonitor.widget.widget import widget
from emonitor.frontend.frontend import frontend
from emonitor.modules import modules
from emonitor.admin.admin import admin
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
    APP_VERSION = '0.3a'                                  # current version
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    LANGUAGE_DIR = 'emonitor/web/translations'            # relative path of default templates
    DEFAULTZOOM = 12                                      # used for map-data
    LANGUAGES = {'de': 'Deutsch'}

    # monitorserver
    MONITORSERVER_ANY = "0.0.0.0"
    MONITORSERVER_MCAST_ADDR = "224.168.2.9"
    MONITORSERVER_MCAST_PORT = 1600


def create_app(config=None, app_name=None, blueprints=None):

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
    app.config.from_pyfile('emonitor.cfg', silent=False)


recorded = []


def configure_extensions(app):
    # flask-sqlalchemy
    db.init_app(app)
    db.app = app
    db.create_all()
    
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
    babel.gettext(u'trigger.default')
    
    # scheduler
    scheduler.start()
    scheduler.initJobs(app)
    
    # modules
    #modules.init_app(app)
    
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
    
    # user
    if User.count() == 0:
        User.get(1)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)

    #message_flashed.connect(record, app)
    #message_flashed.connect(ApiHandler.send_message, app)

    
def configure_blueprints(app, blueprints):
    """Configure blueprints in views."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)
        if hasattr(blueprint, 'init_app'):
            blueprint.init_app(app)

   
def configure_logging(app):
    """Configure file(info)"""

    #if app.debug or app.testing:
    #    # Skip debug and test mode. Just check standard output.
    #    return
    
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler('%swebapp.log' % app.config.get('PATH_DATA'), maxBytes=1024 * 1024 * 100, backupCount=20)
        #file_handler.setLevel(app.config.get('LOGLEVEL', 40)) # 40 = error as default
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(app.config.get('LOGLEVEL', 40))  # 40 = error as default
   

def configure_hook(app):
    #@app.before_request
    #def before_request():
    #    pass
        
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
        return render_template("errors500.html"), 500
