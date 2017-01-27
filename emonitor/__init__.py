"""
    Core methods for creating eMonitor application
"""

__version__ = "0.5.1"

from run import args
from app import create_app
app = create_app(args.get('configfile'))
