import sys
import os, argparse
from emonitor import webapp
from emonitor.sockethandler import SocketHandler

__all__ = ['main', 'tornado', 'builtin']

f = __file__
_PATH = os.path.realpath(__file__)[:os.path.realpath(__file__).rfind(os.sep)]
os.environ['TESSDATA_PREFIX'] = _PATH + '/bin/tesseract'


def tornado(args):
    """
    Start application with tornado webserver

    :param args: start parameters from command line
    """
    from tornado import ioloop, wsgi, autoreload, web

    def t_reload():
        sys.exit(0)  # exit app

    webapp.logger.info('emonitor started with tornado server on port %s' % webapp.config.get('PORT'))
    _server = web.Application([(r'/ws', SocketHandler), (r'.*', web.FallbackHandler, {'fallback': wsgi.WSGIContainer(webapp)})])
    _server.listen(int(webapp.config.get('PORT')))

    tornadoloop = ioloop.IOLoop.instance()
    autoreload.watch('emonitor.cfg')
    autoreload.add_reload_hook(t_reload)
    if not args['d']:
        autoreload.start(tornadoloop)
    try:
        tornadoloop.start()
    except KeyboardInterrupt:
        webapp.logger.info('emonitor stopped')
        tornadoloop.stop()
        try:
            sys.exit(0)
        except:
            pass
    finally:
        tornadoloop.stop()


def builtin(args):
    """
    Start application with flask webserver

    :param args: start parameters from command line
    """
    webapp.logger.info('emonitor started with builtin server on port %s' % webapp.config.get('PORT'))
    webapp.run(host=webapp.config.get('HOST'), port=webapp.config.get('PORT'), debug=webapp.config.get('DEBUG'), threaded=True)
    webapp.logger.info('emonitor stopped')


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
    parser.add_argument('-t', '--tornado', help='use tornado webserver (default)', default=None, action='store_true')
    parser.add_argument('-b', '--builtin', help='use builtin flask webserver', default=None, action='store_true')
    port = webapp.config.get('PORT')
    parser.add_argument('-p', '--port', help='run webserver on port (default: 8080)', type=int, default=port)
    parser.add_argument('-d', help='debug mode without restart', default=None)

    args = vars(parser.parse_args())

    if not args['tornado'] and not args['builtin']:
        tornado(args)
    elif args['builtin']:
        builtin(args)

if __name__ == "__main__":
    main()
