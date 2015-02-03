Straßenkarte
============

In diesem Bereich können die verschiedenen Kartentypen definiert werden, die in der Asicht im Frontend zur Verfügung 
stehen sollen. Dabei sind sowohl Online- als auch Offline-Karten möglich.

Zusätzlich wird noch der Startpunkt auf der Karte definiert, zusammen mit der Position des Feuerwehrhauses. Das bildet 
den Startpunkt der Berechnung der Route zum Einsatzort.

Karte Bearbeiten
----------------

Im Bearbeitungsmodus der Karten-Definition stehen folgende Parameter zur Verfügung:

- **Kartenname:** Name der Karte, wie er im Frontend zur Auswahl angezeigt wird

- **Datenpfad:** Wenn es sich um eine Offline-Karte handelt, muss der Datenpfad für die einzelnen Tiles angegeben werden

- **Kartentyp:** Es stehen unterschiedliche Kartentypen zur Auswahl

  - **Offline-Tileserver:** Alle Karteninformationen werden lokal auf dem Server gespeichert

  - **Online-Tileserver:** Die Kartendaten werden über eine Internetverbindung abgerufen und jedes Mal neu geladen
    (Internetverbindung erforderlich)

  - **Online-Tileserver (Quad):** Spezielle Form eines Online-Tileservers, der die Karten-Tiles in einer besonderen Form
    speichert. (z.B. Bing)
  
- **Kartenverwendung:** Eine Karte sollte als Standardkarte definiert werden, weitere können als Erweiterungskarte
  genutzt werden

Zusätzlich können für die Offline-Verwendung der Karte die Tiles direkt herunter geladen werden. Dazu muss ein Bereiche
angeklickt werden, anschließend wird in einem Popup gefragt, ob der Download gestartet werden soll. Bereiche, die
aktuell aktualisiert werden, sind mit einer Sanduhr markiert. Der Download läuft im Hintergrund, so dass die Seite
nicht offen gehalten werden muss. Nach Abschluss des Downloads wird wieder der Kartenausschnitt dargestellt.
