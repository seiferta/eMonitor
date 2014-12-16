Basisdaten
==========

In diesem Bereich können sämtliche Grundeinstellungen vorgenommen werden

Verzeichniseinstellungen
------------------------

Bestimmte Pfade sind für eMonitor zwingend erforderlich, dass der Arbeitsablauf funktionieren kann:

- **Erledig:** hier werden alle PDF-Dateien gespeichert, die bereits abgearbeitet wurden
- **Temp:** temporäres Verzeichnis zur Zwischenablage
- **Daten:** Basispfad, unter dem normalerweise auch die Datenbank liegt
- **Eingang:** Verzeichnis, das auf Faxeingang (PDF) überwacht wird.

Verzeichnisüberwachung
^^^^^^^^^^^^^^^^^^^^^^

Wenn die Verzeichnisüberwachung aktiv ist, wird das Verzeichnis, das unter *Eingang* konfiguriert wurde in einem 
Abstand von 2 Sekunden auf neue Dateien überprüft. Falls eMonitor nur zur Anzeige ohne aktiven Alarmeingang genutzt 
werden soll, kann die Überwachung deaktiviert werden.

Datenbankversion
^^^^^^^^^^^^^^^^

Die Datenbank hinter eMonitor ist versioniert, dass Änderungen am System auch passende Tabellen vorfinden. Im Bereich 
Datenbankversion kann die Version der Datenbank angezeigt werden, aber auch auf den aktuellen Stand aktualisert, bzw. 
auf einen älteren zurückgesetzt werden. Das ist immer dann sinnvoll, wenn Probleme beim automatischen Update 
aufgetreten sind. eMonitor aktualisiert automatisch beim Start auf die notwendige Version der Datenbank.

Einsatz automatisch schließen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Dass Einsätze nicht evig offen bleiben und sich sammeln, kann eine Zeit in Sekunden angegeben werden, nach der ein 
Einsatz automatisch geschlossen werden soll. Der Status ändert sich dann von *aktiv* auf *abgearbeitet*

Einsatz automatisch archivieren
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Einsätze können nach einer bestimmten Zeit automatisch archiviert werden, dass sie nicht mehr im Frontend geladen 
werden. In diesem Bereich kann das Intervall in Stunden angegeben werden, nach dem die Einsätze automatisch archiviert 
werden sollen
