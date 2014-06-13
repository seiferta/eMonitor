REM pybabel extract -F translations\babel.cfg -o emonitor\frontend\translations\frontend.pot emonitor\frontend\
REM pybabel extract -F translations\babel.cfg -o emonitor\login\translations\login.pot emonitor\login\
REM pybabel extract -F translations\babel.cfg -o emonitor\admin\translations\admin.pot emonitor\admin\

REM pybabel init -i emonitor\frontend\translations\frontend.pot -d emonitor\frontend\translations -l de
REM pybabel init -i emonitor\login\translations\login.pot -d emonitor\login\translations -l de
REM pybabel init -i emonitor\admin\translations\admin.pot -d emonitor\admin\translations -l de

REM pybabel update -i emonitor\frontend\translations\frontend.pot -d emonitor\frontend\translations
REM pybabel update -i emonitor\login\translations\login.pot -d emonitor\admin\translations
REM pybabel update -i emonitor\admin\translations\admin.pot -d emonitor\login\translations

REM pybabel compile -d emonitor\frontend\translations
REM pybabel compile -d emonitor\login\translations
REM pybabel compile -d emonitor\frontend\translations

REM pybabel compile -d emonitor\frontend\translations -o translations\de\LC_MESSAAGES\frontend.mo
REM pybabel compile -d emonitor\login\translations -o translations\de\LC_MESSAAGES\login.mo
REM pybabel compile -d emonitor\admin\translations -o translations\de\LC_MESSAAGES\admin.mo


pybabel extract -F translations\babel.cfg -o emonitor\frontend\translations\frontend.pot emonitor\frontend\
pybabel extract -F translations\babel.cfg -o emonitor\admin\translations\admin.pot emonitor\admin\
pybabel extract -F translations\babel.cfg -o emonitor\login\translations\login.pot emonitor\login\

pybabel init -D frontend -i emonitor\frontend\translations\frontend.pot -d emonitor\frontend\translations -l de
pybabel init -D admin -i emonitor\admin\translations\admin.pot -d emonitor\admin\translations -l de
pybabel init -D login -i emonitor\login\translations\login.pot -d emonitor\login\translations -l de


pybabel compile -f -D frontend -i emonitor\frontend\translations\de\LC_MESSAGES\frontend.po -o emonitor\frontend\translations\de\LC_MESSAGES\frontend.mo
pybabel compile -f -D admin -i emonitor\admin\translations\de\LC_MESSAGES\admin.po -o emonitor\admin\translations\de\LC_MESSAGES\admin.mo
pybabel compile -f -D login -i emonitor\login\translations\de\LC_MESSAGES\login.po -o emonitor\login\translations\de\LC_MESSAGES\login.mo

