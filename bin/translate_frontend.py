import os
import sys
if sys.platform == 'win32':
    pybabel = 'pybabel'
else:
    pybabel = 'flask/bin/pybabel'
if len(sys.argv) != 2:
    print "usage: tr_init <language-code>"
    sys.exit(1)
os.system(pybabel + ' extract -F bin/babel.cfg -k gettext -o emonitor\\frontend\\translations\\frontend.pot emonitor\\frontend')
os.system(pybabel + ' update -D frontend -i emonitor\\frontend\\translations\\frontend.pot -d emonitor\\frontend\\translations -l ' + sys.argv[1])
