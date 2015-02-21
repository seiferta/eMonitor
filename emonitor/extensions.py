
# flask extensions
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# flask alembic
from flask_alembic import Alembic
alembic = Alembic()

# flask babel translator
from .mybabel import MyBabel
babel = MyBabel()

# signals
from .signals import MySignal
signal = MySignal()

from flask.ext.login import LoginManager
login_manager = LoginManager()

from flask.ext.cache import Cache
cache = Cache()

# classes
from .utils import Classes
classes = Classes()

# events
from .events import Event
events = Event

# monitorserver
from .monitorserver import MonitorServer
monitorserver = MonitorServer()

# scheduler
from .scheduler import MyScheduler
scheduler = MyScheduler()

# printer
from .printertype import ePrinters
printers = ePrinters()
