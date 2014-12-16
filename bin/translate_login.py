import os
import sys


def translateLoginStrings(language_code):
    """
    Translate all strings used in login templates and code

    :param language_code: de|en
    """
    if sys.platform == 'win32':
        pybabel = 'pybabel'
    else:
        pybabel = 'flask/bin/pybabel'

    os.system(pybabel + ' extract -F bin/babel.cfg -k gettext -o emonitor\\login\\translations\\login.pot emonitor\\login')
    os.system(pybabel + ' update -D login -i emonitor\\login\\translations\\login.pot -d emonitor\\login\\translations -l ' + language_code)


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print "usage: tr_init <language-code>"
        sys.exit(1)
    else:
        translateLoginStrings(sys.argv[1])
