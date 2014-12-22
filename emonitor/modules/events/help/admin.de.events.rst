Events Bearbeiten/Definition
============================

Für ein Event kann aus einer Liste der möglichen **Event-Handler** der gewünschte ausgewählt werden. Jeder Handler hat 
dabei eine eigene Liste an Eingabe- und Ausgabe-Parametern, die konfiguriert werden müssen. Dabei kann entweder aus den 
bisher schon vorhandenen Parametern auswählen oder selber einen Wert eingeben.

Ausgabe-Parameter der vorangegangenen Aktionen können als Eingabe-Parameter der Folgeaktion gewähl werden. So können 
Parameter in einer Aktion erzeugt werden und durch weitere Aktionen verändert und weiterverarbeitet werden.

Beispiele
---------

Observer - Datei hinzugefügt
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 
Wenn die Verzeichnisüberwachung eine neue Datei feststellt, wird das Event aufgerufen. Folgende Bearbeitungsschritte 
sollten mindestens angelegt werden:

1. *MonitorServer*  
   keine weiteren Parameter konfiguriert, aktualisiert die Darstellung auf den Monitoren.
   
2. *Text-Erkennung*  
   startet die Texterkennung aus dem Fax
   *Parameter:*
   - path: incomepath (in)
   - filename: filename (in)
   - text: text (out)
 
3. *Textoptimierung*  
   *Parameter:*
   - text: text (in/out)
 
4. *Alarmerstellung*  
   *Parameter:*
   - text: text (in)
   - id: id (out)
   - fields: fields (out)

Einsatz hinzugefügt
^^^^^^^^^^^^^^^^^^^

Wenn der Text eines Fax erkannt wurde, das von bestimmten Alarmtyp ist, wird dieses Event aufgerufen. Damit kann für 
unterschiedliche Alarmtypen jeweils eine eigene Anzeige definiert werden.  
Standardmäßig kann das FEZ oder auch jeder weitere Typ sein. Folgende Bearbeitungsschritte sollten konfiguriert werden:

1. *MonitorServer*  
   Aktualisierung der Darstellung auf dem Monitor mit dem gerade neu erzeugten Alarm  
   *Parameter:*
   - params: alarmid (in)
