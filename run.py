import sys
sys.path.append('emonitor')  # do not remove to find wsgiserver2
import os, argparse
import logging
from emonitor import app

__all__ = ['main', 'builtin']

logger = logging.getLogger()

f = __file__
_PATH = os.path.realpath(__file__)[:os.path.realpath(__file__).rfind(os.sep)]
os.environ['TESSDATA_PREFIX'] = '{}/bin/tesseract'.format(_PATH)


def builtin(args):
    """
    Start application with flask webserver

    :param args: start parameters from command line
    """
    app.logger.info('emonitor started with builtin server on port {}'.format(app.config.get('PORT')))
    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'), debug=app.config.get('DEBUG'), threaded=True)
    logger.info('emonitor stopped')


def main():
    """
    Start eMonitor application

    :argument:
        -   -t --tornado: use tornado webserver
        -   -b --builtin: use flask webserver (only for test)
        -   -p --port: define port for webserver
        -   -d: start in debug mode
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--builtin', help='use builtin flask webserver', default=None, action='store_true')
    parser.add_argument('-c', '--cherrypy', help='use cherrypy webserver', default=None, action='store_true')
    port = app.config.get('PORT')
    parser.add_argument('-p', '--port', help='run webserver on port (default: 8080)', type=int, default=port)
    parser.add_argument('-d', help='debug mode without restart', default=None)

    args = vars(parser.parse_args())

    if 'port' in args:  # use port from command line
        app.config['PORT'] = args['port']
    if not args['builtin'] and not args['cherrypy']:
        from emonitor.webserver import webserver
        webserver(app)
    elif args['builtin']:
        builtin(args)

if __name__ == "__main__":
    main()
