import os
import sys
if sys.platform == 'win32':
    pybabel = 'pybabel'
else:
    pybabel = 'flask/bin/pybabel'
if len(sys.argv) != 2:
    print "usage: tr_init <language-code>"
    sys.exit(1)
    
# admin pages
os.system(pybabel + ' extract -F bin/babel.cfg -k gettext -o emonitor\\admin\\translations\\admin.pot emonitor\\admin')
os.system(pybabel + ' update -D admin -i emonitor\\admin\\translations\\admin.pot -d emonitor\\admin\\translations -l ' + sys.argv[1])

# frontend pages
os.system(pybabel + ' extract -F bin/babel.cfg -k gettext -o emonitor\\frontend\\translations\\frontend.pot emonitor\\frontend')
os.system(pybabel + ' update -D frontend -i emonitor\\frontend\\translations\\frontend.pot -d emonitor\\frontend\\translations -l ' + sys.argv[1])

# login pages
os.system(pybabel + ' extract -F bin/babel.cfg -k gettext -o emonitor\\login\\translations\\login.pot emonitor\\login')
os.system(pybabel + ' update -D login -i emonitor\\login\\translations\\login.pot -d emonitor\\login\\translations -l ' + sys.argv[1])