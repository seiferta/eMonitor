import types

# flask extensions
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
DeclarativeBase = declarative_base()


def get_query(self, *entities, **kwargs):
    return self.session.query(*entities, **kwargs)

db = SQLAlchemy()
db.get = types.MethodType(get_query, db)  # add method get
db.DeclarativeBase = DeclarativeBase

# flask alembic
from flask_alembic import Alembic
alembic = Alembic()

# flask babel translator
from emonitor.mybabel import MyBabel
babel = MyBabel()

# signals
from emonitor.signals import MySignal
signal = MySignal()

from flask.ext.login import LoginManager
login_manager = LoginManager()

from flask.ext.cache import Cache
cache = Cache()

# scheduler
from emonitor.scheduler import MyScheduler
scheduler = MyScheduler()

# events
from emonitor.events import Event
events = Event

# monitorserver
from emonitor.monitorserver import MonitorServer
monitorserver = MonitorServer()

# printer
from emonitor.printertype import ePrinters
printers = ePrinters()
