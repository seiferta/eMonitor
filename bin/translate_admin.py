import os
import sys


def translateAdminStrings(language_code):
    """
    Translate all strings used in admin templates and code

    :param language_code: de|en
    """

    if sys.platform == 'win32':
        pybabel = 'pybabel'
    else:
        pybabel = 'flask/bin/pybabel'

    os.system(pybabel + ' extract -F bin/babel.cfg -k gettext -o emonitor\\admin\\translations\\admin.pot emonitor\\admin')
    os.system(pybabel + ' update -D admin -i emonitor\\admin\\translations\\admin.pot -d emonitor\\admin\\translations -l ' + language_code)


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print "usage: tr_init <language-code>"
        sys.exit(1)
    else:
        translateAdminStrings(sys.argv[1])
