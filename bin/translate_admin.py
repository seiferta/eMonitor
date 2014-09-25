import os
import sys
if sys.platform == 'win32':
    pybabel = 'pybabel'
else:
    pybabel = 'flask/bin/pybabel'
if len(sys.argv) != 2:
    print "usage: tr_init <language-code>"
    sys.exit(1)
os.system(pybabel + ' extract -F bin/babel.cfg -k gettext -o emonitor\\admin\\translations\\admin.pot emonitor\\admin')
os.system(pybabel + ' update -D admin -i emonitor\\admin\\translations\\admin.pot -d emonitor\\admin\\translations -l ' + sys.argv[1])
