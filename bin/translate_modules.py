import os
import sys
if sys.platform == 'win32':
    pybabel = 'pybabel'
else:
    pybabel = 'flask/bin/pybabel'
if len(sys.argv) != 2:
    print "usage: tr_init <language-code>"
    sys.exit(1)
os.system(pybabel + ' extract -F bin/babel.cfg -k gettext -o emonitor\\modules\\translations\\modules.pot emonitor\\modules')
os.system(pybabel + ' update -D modules -i emonitor\\modules\\translations\\modules.pot -d emonitor\\modules\\translations -l ' + sys.argv[1])
