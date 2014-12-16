import os
import sys


def translateHelpStrings(language_code):
    """
    Translate all strings used in help templates and code

    :param language_code: de|en
    """
    if sys.platform == 'win32':
        pybabel = 'pybabel'
    else:
        pybabel = 'flask/bin/pybabel'

    os.system(pybabel + ' extract -F bin/babel.cfg -k gettext -o emonitor\\onlinehelp\\translations\\onlinehelp.pot emonitor\\onlinehelp')
    os.system(pybabel + ' update -D onlinehelp -i emonitor\\onlinehelp\\translations\\onlinehelp.pot -d emonitor\\onlinehelp\\translations -l ' + language_code)

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print "usage: tr_init <language-code>"
        sys.exit(1)
    else:
        translateHelpStrings(sys.argv[1])
