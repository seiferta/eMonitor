

BABEL:

1)
pybabel extract -F babel/babel.cfg -o babel/messages.pot .

2)
pybabel init -i babel/messages.pot -d web/i18n -l de

3)
pybabel update -i babel/messages.pot -d web/i18n

4)
pybabel compile -d web/i18n