Basiskonfiguration (DE)
=======================

1. Konfigurations-Datei
-----------------------

Im Basisverzeichnis von eMonitor wird eine Beispielkonfiguration mitgeliefert: emonitor.cfg.template
In dieser Datei sind sämtliche möglichen Parameter angegeben, die angepasst werden können. Wichtig sind dabei die
Parameter:

* SQLALCHEMY_DATABASE_URI
* PATH_DATA
* PATH_INCOME
* PATH_DONE
* PATH_TMP
* PATH_TILES

Datenbank-Verbindung
````````````````````

eMonitor unterstützt eine Reihe unterschiedlicher Datenbanken, die je nach Einsatzzweck genutzt werden können.

* MySQL: Im Live-Betrieb sollte auf diese Datenbank zugegriffen werden, da gerade bei der Nutzung mehrerer Monitore und
  der Druckfunktion sehr viele gleichzeitige Zugriffe erfolgen, die andere Datenbanken verhindern.

::

 > SQLALCHEMY_DATABASE_URI = 'mysql://<benutzer>:<passwort>@<host>/<datenbankname>
                                                        ?charset=utf8&use_unicode=0'

z.B.
::

 > SQLALCHEMY_DATABASE_URI = 'mysql://emonitor:geheim@127.0.0.1/emonitor
                                                        ?charset=utf8&use_unicode=0'

Benutzer: emonitor
Passwort: geheim
Host: 127.0.0.1
Datenbankname: emonitor

* Sqlite: Einfache Datenbank, die ohne Installation eine Datei nutzt. Kann aber zu Problemen führen, wenn viele
  Verbindungen bzw. Anfragen auf die Datenbank gestartet werden.

::

 > SQLALCHEMY_DATABASE_URI = 'sqlite:///<pfad>/<dateiname>'

z.B.
::

 > SQLALCHEMY_DATABASE_URI = 'sqlite:///D:/data/emonitor/emonitor.db'


Pfade
`````

eMonitor speichert Daten in verschiedenen Verzeichnissen

* PATH_DATA: Basisverzeichnis der Daten
* PATH_INCOME: Verzeichnis, das überwacht wird (für Fax-Empfang)
* PATH_DONE: Faxablage nach der Bearbeitung - Darunter wird eine Struktur aufgebaut Jahr/Monat z.B. 2015/04
* PATH_TMP: Verzeichnis für temporäre Dateien
* PATH_Tiles: Pfad für den Kartenserver, unter dem die Tiles für die Offline-Kartendarstellung abgelegt werden.

Die Pfade können jeweils absolut sein oder im UNC-Format angegeben werden, sollten aber immer mit */* enden. Unter
Windows ist es ratsam, dass */* als Verzeichnistrenner verwendet wird.
