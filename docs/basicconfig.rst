Basiskonfiguration
==================

Für verschiedene Module ist folgende Basiskonfiguration sinnvoll

Eventhandling
-------------

Als Standard kann folgende Reihenfolge erzeugt werden:

- **Observer - Datei hinzugefügt**

  #. *MonitorServer* (ohne weitere Parameter)

     Fordert die clients zum Update des angezeigten Inhalts auf

  #. *Text-Erkennung* (mit Parametern)

     ===================== =============
     **Eingabe**           **Ausgabe**

     *path* = incomepath   *text* = text
     *filename* = filename
     ===================== =============

     Der erkannte Text aus *incomepath*/*filename* wird in der Variablen *text* ausgeliefert

  #. *Textoptimierung* (mit Parametern)

     ============= =============
     **Eingabe**   **Ausgabe**
     *text* = text *text* = text
     ============= =============

     Damit werden die Änderungen in der Variablen *text* entgegen genommen und nach der Bearbeitung wieder in *text*
     ausgeliefert

  #. *Alarmerstellung* (mit Parametern)

     ============= =================
     **Eingabe**   **Ausgabe**
     *text* = text *id* = alarmid
                   *fields* = fields
     ============= =================

     Aus den Daten der Variable *text* wird ein Einsatz erzeugt und die ID in der Variablen *alarmid* ausgeliefert,
     die Werte werden zusäzlich in *fields* weitergegeben.

- **Einsatz hinzugefügt**

  Für jeden neu erzeugten Einsatztyp muss nun noch definiert werden, ob weitere Aktionen erforderlich sind. Dabei wird
  beim manuellen Anlegen eines Einsatzes *Einsatz hinzugefügt* ausgeführt, bei den restlichen Typen ist es abhängig
  davon, welcher Einsatztyp vorliegt.

  Normalerweise sollte an der Stelle immer der MonitorServer ausgeführt werden, um den neu erzeugten Einsatz an die
  Clients auszuliefern.

Text-Bearbeitung
----------------

Bildoptimierung
~~~~~~~~~~~~~~~

Je nach Art des Betriebssystems sind unterschiedliche Parameter notwendig:

- **32-Bit-Betriebssysteme**

  > [basepath]/bin/convert/convert32.exe -depth 32 -density 250 [incomepath][filename] -quality 100 [tmppath]

- **64-Bit-Betriebssysteme**

  > [basepath]/bin/convert/convert64.exe -resize 200% -depth 32 -density 200 [incomepath][filename] -quality 100 [tmppath]

Werte in Klammern werden dabei automatisch beim Aufruf ersetzt. Details sind in der Modul-Hilfe zu finden.

Text-Bearbeitung
~~~~~~~~~~~~~~~~

> [basepath]/bin/tesseract/tesseract.exe [incomepath][filename] [tmppath] -l deu -psm  6 quiet custom

Werte in Klammern werden dabei automatisch beim Aufruf ersetzt. Details sind in der Modul-Hilfe zu finden.