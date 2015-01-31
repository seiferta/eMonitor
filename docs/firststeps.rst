Erste Schritte
==============

Nach der Installation und dem ersten Start von eMonitor stehen folgende Funktionen zur Verfügung:

- Webserver mit verschiedenen Oberflächen:

  - Frontend: `http://localhost:[port] </>`_

  - Admin-Bereich: `http://localhost:[port]/admin </admin>`_

  - Monitor-Bereich: `http://localhost:[port]/monitor </monitor>`_ (für Clients)

- Einsatztestverarbeitung

- Scheduler

- Observer

Frontend
--------

Im Frontend erfolgt die eigentliche Steuerung der Software und die Kommunikation mit dem Benutzer. Das Frontend ist
unterteilt in drei Bereiche, die mit unterschiedlichen Inhalten belegt werden können:

    ========= ========= ============
    **Links** **Mitte** **Rechts**
    Einsätze  Karte     Straßenliste
    ========= ========= ============

Die Konfiguration erfolgt unter `Startseite </admin/settings/start>`_. Je nach gewähltem Modul werden unterschiedliche
Funktionen geboten, es können auch mehrere Module für die einzelnen Bereiche gewählt werden, zwischen denen umgeschaltet
werden kann. Die oben dargestellten Module stellen die Basiseinstellungen dar. Die beiden äußeren Bereiche können ein-
und ausgeblendet werden und die Größen konfiguiert und geändert werden.

Admin-Bereich
-------------

Es sind eine Reihe an Grundeinstellungen vorzunehmen, ohne die eMonitor nicht korrekt arbeiten kann. Die
Standardlogin-Daten lauten *Administrator*/*admin*, diese können nach dem Anmelden unter der
`Benutzerverwaltung </admin/users>`_ geändert werden.

Folgende Grundeinstellungen sind unbedingt erforderlich:

#. **Straßenkarte:** Die `Startposition </admin/maps/position>`_ und die `Straßenkarten </admin/maps>`_

#. **Definition einer Einheit:** Mindestens eine `Einheit </admin/settings/department>`_ muss angelegt werden, die als
   Basisfeuerwehr genutzt wird

#. **Definition eines Ortes/Stadt:** Es muss in der `Ortskonfiguration </admin/streets/0>`_ ein Ort als Basis definiert
   werden

#. **Definition von Material/Ausrüstung:** `Fahrzeuge/Material </admin/settings/cars>`_

#. **Definition der Ausrückeordnung:** `Ausrückeordnung </admin/alarmkeys>`_

#. **Einsatz-Typen:** Einsatzarten, die ausgewertet werden können `Einsatz-Typen </admin/alarms/types>`_

Wenn diese Einstellungen vorgenommen worden sind, dann werden noch für folgende Module Warnungen angezeigt:

- **Einsatzobjekte:** An dieser Stelle fehlt noch die Typ-Definition für Einsatzobjekte. So lange keine Einsatzobjekte
  definiert worden sind, bereitet das keine Probleme. Wenn Einsatzobjekte erzeugt werden sollen, muss vorher mindestens
  ein Typ unter `Einsatzobjekt-Typen </admin/alarmobjects/types>`_ angelegt werden.

- **Eventhandling:** Bevor keine Handler an Events gebunden werden, erfolgt keine automatische Verarbeitung der
  eingehenden Faxe, da noch definiert werden muss, welche Schritte für ein korrektes Arbeiten erforderlich ist.
  Details sind in der :doc:`basicconfig` zu finden

- **Monitorkonfiguration:** Es müssen noch die Monitore/Clients definiert werden, auf denen die Daten von eMonitor
  angezeigt werden sollen. Unter `Definition </admin/monitors>`_ müssen zuerst die Monitore definiert werden,
  anschließend kann für jeden Monitor für jeden Trigger ein eigenes Layout definiert werden.

  *Hinweis:* bei einem Monitor mit einer Full-HD-Auflösung (1920x1080 Pixel) ist ein Raster von 9x6 sinnvoll.

Nach der Basiskonfiguration ist eMonitor einsatzbereit und überwacht das Input-Verzeichnis auf den Eingang neuer Dateien

Monitor-Bereich
---------------

Die Daten/Seiten des Monitor-Bereichs werden vom Client geladen und sind für die Darstellung auf den Clients angepasst.
Zur Kontrolle der Anzeige kann allerdings zu jeder Zeit auch über den Browser auf diese Seiten navigiert werden.
Folgende URLs sind möglich:

- `Testbild </monitor>`_

- `Seite für Client 1 </monitor/1>`_

- `Seite für Client 2 </monitor/2>`_

- ...

Falls die angegebene ID nicht bei der `Monitorkonfiguration </admin/monitors>`_ definiert ist, wird ebenfalls das Testbild angezeigt.

Einsatztestverarbeitung
-----------------------

Zum Testen der korrekten Arbeitsweise der Faxauswertung kann ein Testfax unter `Testverarbeitung </admin/alarms/test>`_ hochgeladen
werden, das die selben Schritte durchläuft, die auch der automatische Prozess nutzt. So kann das korrekte Arbeiten
überprüft werden.

Scheduler
---------

In eMonitor arbeitet ein Scheduler im Hintergrund, der das Zeitgesteuerte-Eventhandling übernimmt, so dass zu
bestimmten Zeitpunkten Aktionen ausgeführt werden können. Die Aktionen werden in den verschiedenen Modulen erzeugt und
können zentral unter `Schedules </admin/monitors/actions>`_ abgefragt werden.

Observer
--------

Zur Verzeichnisüberwachung wird ein Observer eingesetzt, der im Intervall von 2 Sekunden das konfigurierte Verzeichnis
überwacht und ggf. Events auslöst.
