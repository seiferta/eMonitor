---
layout: index
permalink: /details/index.html
---

### Funktionen

#### Folgende Funktionen sind in Planung/Entwicklung:

* Alarmeingang über E-Mail
* Personenverwaltung
* Erweiterungen im Mitteilungsmodul (z.B. Kartendarstellung mit Symbolen für Straßensperren)

#### Folgende Funktionen sind bereits integriert:

##### Adressvalidierung über OpenStreetMap

Die Alarmadresse wird über OpenStreetMap validiert. Falls die Hausnummern der Straßen gepflegt wurden, kann die genaue 
Alarmadresse angezeigt werden. Dabei wird das Haus fablich hervorgehoben und zentriert dargestellt. Sonst wird ein 
Punkt in der Mitte der Straße als Einsatzadresse angezeigt.

Die Daten von OpenStreetMap können jederzeit nachgepflegt werden und anschließend automatisch in eMonitor importiert 
werden. Folgende Informationen werden dabei berücksichtigt:

* Straßen: Sämtliche Straßen eines Ortes/einer Stadt können in eMonitor geladen werden. Diese stehen dann sowohl in der 
Oberfläche, als auch für die Alarmauswertung offline zur Verfügung
* Hausnummern: Die Koordinaten der Hausnummern können in eMonitor geladen werden, so dass dann die Umrisse einer 
Adresse angezeigt werden können.
* Hydranten können als Kartenobjekte geladen werden und als eigener Layer über die Karte gelegt werden. Zusäzlich kann 
als Kriterium definiert werden, dass bei bestimmten Alarmstichworten die Hydranten auf der Karte mit 
angezeigt/ausgedruckt werden.
* Feuerwehrzufahren für die Drehleiter können bei korrekter Definition auf der Karte dargestellt werden. Ebenfalls als 
eigener Layer auf der Karte.

##### Kartendarstellung auf dem Monitor

Auf dem Monitor kann für einen Alarm der passende Kartenausschnitt der Alarmadresse angezeigt werden. Falls konfiguriert
mit zusätzlichen Informationen. Es können verschiedene Karten eingebunden werden, so dass die Obberfläche von eMonitor 
eine Umschaltung zwischen verschiedenen Ansichten ermöglicht, z.B. Satelliten-Ansicht, OpenStreetMap-Karte, etc.

##### Individuelle Ausrückeordnungen je Alarmstichwort

Für jede Feuerwehreinheit kann eine eigene Ausrückeordnung mit der Definition der Primären-, Sekundären- und 
zusätzlichen Einsatzmitteln erstellt werden. Diese Konfiguration kann über Import/Export im Excel-Format erfolgen und 
somit auch extern geflegt werden.

##### Drucken einer Alarmübersicht mit Kartendarstellung

Bei Alarmeingang kann eine spezielle Ansicht mit Zusatzinformationen zum Einsatz auf einem Alarmdrucker ausgedruckt 
werden. Aktuell stehen dabei die Originalansicht der eingehenden Informatinen (Fax) und eine detaillierte Ansicht zur 
Verfügung.
