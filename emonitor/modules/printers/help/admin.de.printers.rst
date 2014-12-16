Druckansichten
==============

In der Definition der Druckansichten können beliebig viele Druckformate definiert werden, die an unterschiedlichen 
Druckern auch automatisch ausgedruckt werden können. Die aktiven Konfigurationen stehen dabei im Frontend bei der 
Einsatzverwaltung zur Verfügung und können zusätzlich im [Eventhandling](/admin/events) ausgewählt werden.

Definition bearbeiten
---------------------

Für jede Druckansicht können folgende Parameter definiert werden:

- **Name:** sprechender Name für die Konfiguration. Dieser Name wird auch im Kontextmenü im Frontend bei der
  Einsatzübersicht verwendet.

- **Modul:** Layout, das gedruckt werden soll. Über Templates kann das vorhandene Layout auch erweitert werden

- **Drucker:** Auswahl des Druckers, auf dem das Ergebnis erstellt werden soll.
  ACHTUNG: Aufgund eines Bugs in *gsprint* kann unter Windows nur der *<default>*-Drucker verwendet werden.

- **Anzahl Seiten:** Anzahl der Seiten/Exemplare, die für das Layout gedruckt werden sollen.

- **Einstellungen:** weitere Einstellungen für den Druck (aktuell nicht genutzt)

- **aktiv:** nur aktivierte Konfigurationen stehen im Frontend zur Auswahl

Module
------

Folgende Module stehen aktuell zur Verfügung:

- Einsätze

  - Originalfax: Kopie des Alarmfaxes

  - Einsatzzusammenfassung: Zusammenfassung mit Kartendarstellung, Fahrzeugauswahl, Basisinformationen und Anfahrt,
    falls es sich nicht um den Default-Ort handelt
