---
layout: index
permalink: /install/database/
breadcrumb: Datenbank
---

### Datenbank-Konfiguration

Für den Einsatz von eMonitor in Live-Betrieb sollte MySQL als Datenbank verwendet werden, da SQLite für diesen Zweck 
nicht geeignet ist. Dafür muss auf dem Server ein MySQL-Server installiert sein und eine passende Datenbank erzeugt 
worden sein. Anschließend muss noch die Variable ** entsprechend angepasst werden

 > SQLALCHEMY_DATABASE_URI = 'sqlite:///emonitor.db'
 
 erzeugt eine SQLite Datenbank im Basisverzeichnis der eMonitor-Server Installation
 
 > SQLALCHEMY_DATABASE_URI = 'mysql://emonitoruser:emonitorpwd@127.0.0.1/emonitor'
 
 nutzt die MySQL-Datenbank *emonitor* mit dem Benutzer *emonitoruser* und Passwort *emonitorpwd*


### Datenbank-Konvertierung

eMonitor bringt ein Script mit, das eine nachträgliche Konvertierung einer SQLite-Datenbank zu einer MySQL-Datenbank 
ermöglicht.

 > python bin/dataconvert.py -f XXX -t YYY
  
  -f sqlite:///emonitor.db
  
  -t mysql://emonitoruser:emonitorpwd@127.0.0.1/emonitor
 
Dabei müssen die Parameter *-f* = *from* und *-t* = *to* an die jeweiligen Gegebenheiten angepasst werden. Nach dem 
Ausführen des Scriptes muss die Konfigurationsdatei *emonitor.cfg* natürlich auf die gewünschte Datenbankverbindung hin 
angepasst werden.
Nach einem Neustart der Software nutzt eMonitor ab sofort die neue Datenbankverbindung.
