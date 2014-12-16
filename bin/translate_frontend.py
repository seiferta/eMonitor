import os
import sys


def translateFrontendStrings(language_code):
    """
    Translate all strings used in frontend templates and code

    :param language_code: de|en
    """
    if sys.platform == 'win32':
        pybabel = 'pybabel'
    else:
        pybabel = 'flask/bin/pybabel'

    # frontend pages
    os.system(pybabel + ' extract -F bin/babel.cfg -k gettext -o emonitor\\frontend\\translations\\frontend.pot emonitor\\frontend')
    os.system(pybabel + ' update -D frontend -i emonitor\\frontend\\translations\\frontend.pot -d emonitor\\frontend\\translations -l ' + language_code)


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print "usage: tr_init <language-code>"
        sys.exit(1)
    else:
        translateFrontendStrings(sys.argv[1])
