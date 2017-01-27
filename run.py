import sys
sys.path.append('emonitor')  # do not remove to find wsgiserver2
import os, argparse
import logging

__all__ = ['main', 'args']

logger = logging.getLogger()
f = __file__
_PATH = os.path.realpath(__file__)[:os.path.realpath(__file__).rfind(os.sep)]
os.environ['TESSDATA_PREFIX'] = '{}/bin/tesseract'.format(_PATH)

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--configfile', help='use given config file', default='emonitor.cfg')
parser.add_argument('-p', '--port', help='run webserver on port (default: 5000)', type=int)
parser.add_argument('--debug', help='debug mode without restart', default=False, action="store_true")

args = vars(parser.parse_args())


def main():
    """
    Start eMonitor application

    :argument:
        -p --port: define port for webserver
        -f --configfile: use given config file, default: emonitor.cfg
        --debug  : start in debug mode
    """
    global args
    from emonitor import app
    from emonitor.webserver import webserver
    if args.get('port'):
        app.config.update({'PORT': args.get('port')})
    if args.get('debug'):
        app.config.update({'DEBUG': True})
    webserver(app)


if __name__ == "__main__":
    main()
