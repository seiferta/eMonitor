---
layout: index
permalink: /server/frontend/
breadcrumb: Server-Frontend
---
### Frontend

![eMonitor Frontend]({{ site.url }}/eMonitor/images/frontend.jpg) Die Standardoberfläche ist über einen aktuellen Browser im Netzwerk erreichbar und konfigurierbar: Es wird ein Layout 
verwendet, in dem links und rechts neben einem zentralen Bereich unterschiedliche Module einblendbar sind. Diese sind 
auch per Mausklick ausblendbar, um im zentralen Bereich mehr Platz zur Verfügung zu haben. Man kann vordefinieren, wie 
breit die beiden Seitenmodule sein sollen und auch zwischen allen Modulen wählen, die eine Darstellung im Frondend 
erlauben.

Von der Standardoberfläche können sämtliche angeschlossenen Monitore ferngesteuert werden und auch kontrolliert werden, 
ob die verschiedenen Monitore noch "online" sind.

##### Einsatzmodul:

Hier werden in verschiedenen Kategorien Einsätze in Kurzform angezeigt. Man hat so alle wichtigen Informationen zu 
einem Einsatz auf einen Blick verfügbar. Die Kategorien der Oberfläche sind "Laufende Einsätze", "Offene Einstäze" und 
"Abgeschlossene Einstätze". Im Hintergrund gibt es noch "Archivierte Einsätze".
Für jeden Einsatz werden Datum/Uhrzeit, das Alarmstichwort, die Einsatzadresse, sowie weitere Zusatzinfomrationen über 
Piktogramme angezeigt. Im Kontextmenü kann man verschiedene Operationen auslösen. Von Bearbeiten, über Statusänderungen,
 bis hin zum Ausdruck einer speziellen Einsatzübersicht sind unterschiedliche Funktionen hinterlegt.
Zusätzlich ist es möglich, sich die kürzeste Straßenverbindung zum Einsatzort von einem definierbaren Startpunkt aus 
auf dem Kartenmodul anzeigen zu lassen.
Falls Hausnummern für den Kartenausschnitt der Einsatzadresse in der OpenStreetMap-Karte definiert wurden, wird das 
entsprechende Gebäude mit einer farbigen Kennzeichnung dargestellt. Falls keine Hausnummer existiert, kann auch explizit
 ein farbiger Marker auf der Karte gesetzt werden. Dieser Marker wird entsprechend der Priorität des Einsatzes in 
 unterschiedlicher Farbe gesetzt.

##### Mitteilungsmodul:

Hier kann die Konfiguration von Mitteilungen erfolgen, die in einer Art Slideshow angezeigt werden können, solange kein 
Einsatz aktiv ist. Es stehen unterschiedliche Mitteilungstypen zur Verfügung, die jeweils zu frei definierbaren Zeiten 
eingeblendet werden können. Derzeit sind folgende Arten möglich:

* Textmitteilungen
* Wetterübersicht
* Geburtstagskalender

Geplant:
* Bildergalerie
* Kartendarstellung mit Besonderheiten, Behinderungen

Wenn während der Anzeige einer Mitteilung ein Alarmeingang erfolgt, wird automatisch zur Anzeige der 
Einsatzinformationen umgeschlatet. Sobald der letzte Einsatz abgeschlossen ist, erscheinen wieder die Mitteilungen.

##### Kartenmodul:

Das Kartenmodul dient als zentrale Anzeigeoberfläche mit **Kartendarstellung**. Es können verschiedene Karten eingeblendet 
werden, die über den Adminstrationsbereich konfigurierbar sind. Getestet sind aktuell die Karten von Bing, Google und 
OpenStreetMap. Dabei ist es möglich auch Karten im Offline-Modus anzeigen zu lassen, die auf dem Server gespeichert 
werden.
Zusätzlich kann man weitere Elemente auf der Karte in einer eigenen Ebene darstellen. Aktuell ist hier realisiert, dass 
man **Hydranten** einblenden kann.
Zusätzlich können andere Module die API der Karte nutzen und beispielsweise eine Route oder Markierungen anzeigen. 
Geplant ist hier auch die Erweiterung um **Feuerwehrzufahrten** für die Drehleiter.

##### Straßen-/Objektmodul:

Für das Einsatzgebiet können für konfigurierbare Orte die **Straßen** gespeichert werden, so dass eine schnelle Suche 
möglich wird. Die Daten stammen dabei von OpenStreetMap. Es werden im Hintergrund Straßen und (falls vorhanden) 
Hausnummern gespeichert. Somit funktioniert diese Suche auch Offline ohne Internetvebindung. Es ist geplant, dass man 
eMonitor auch auf deinem abgesetzten Arbeitsplatz nutzen kann, z.B. in einem ELW.
Neben den Straßen kann man auch spezielle **Einsatzobjekte** definieren. In der aktuellen Version ist dabei der 
Funktionsumfang noch sehr beschränkt. Geplant ist aber, dass man beispielsweise Objektpläne und weitere Informationen 
ablegen kann, und z.B. die Fahrzeugaufstellung mit speichern kann, so dass die bei der Auswahl des Objekts dann auf der 
Karte dargestellt werden kann.
