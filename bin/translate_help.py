import os
import sys
if sys.platform == 'win32':
    pybabel = 'pybabel'
else:
    pybabel = 'flask/bin/pybabel'
if len(sys.argv) != 2:
    print "usage: tr_init <language-code>"
    sys.exit(1)
os.system(pybabel + ' extract -F bin/babel.cfg -k gettext -o emonitor\\onlinehelp\\translations\\onlinehelp.pot emonitor\\onlinehelp')
os.system(pybabel + ' update -D onlinehelp -i emonitor\\onlinehelp\\translations\\onlinehelp.pot -d emonitor\\onlinehelp\\translations -l ' + sys.argv[1])
