---
layout: index
permalink: /server/index.html
---

### eMonitor-Server


Die eMonitor Software bietet eine Reihe unterschiedlicher Oberflächen:

#### Standardoberfläche

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

Wenn während der Anzeige einer Mitteilung ein Alarmeingang erfolgt, wird automatisch zur Anzeige der 
Einsatzinformationen umgeschlatet. Sobald der letzte Einsatz abgeschlossen ist, erscheinen wieder die Mitteilungen.

##### Kartenmodul:

Das Kartenmodul dient als zentrale Anzeigeoberfläche mit Kartendarstellung. Es können verschiedene Karten eingeblendet 
werden, die über den Adminstrationsbereich konfigurierbar sind. Getestet sind aktuell die Karten von Bing, Google und 
OpenStreetMap. Dabei ist es möglich auch Karten im Offline-Modus anzeigen zu lassen, die auf dem Server gespeichert 
werden.
Zusätzlich kann man weitere Elemente auf der Karte in einer eigenen Ebene darstellen. Aktuell ist hier realisiert, dass 
man Hydranten einblenden kann.
Zusätzlich können andere Module die API der Karte nutzen und beispielsweise eine Route oder Markierungen anzeigen. 
Geplant ist hier auch die Erweiterung um Feuerwehrzufahrten für die Drehleiter.

##### Straßen-/Objektmodul:

Für das Einsatzgebiet können für konfigurierbare Orte die Straßen gespeichert werden, so dass eine schnelle Suche 
möglich wird. Die Daten stammen dabei von OpenStreetMap. Es werden im Hintergrund Straßen und (falls vorhanden) 
Hausnummern gespeichert. Somit funktioniert diese Suche auch Offline ohne Internetvebindung. Es ist geplant, dass man 
eMonitor auch auf deinem abgesetzten Arbeitsplatz nutzen kann, z.B. in einem ELW.
Neben den Straßen kann man auch spezielle Einsatzobjekte definieren. In der aktuellen Version ist dabei der 
Funktionsumfang noch sehr beschränkt. Geplant ist aber, dass man beispielsweise Objektpläne und weitere Informationen 
ablegen kann, und z.B. die Fahrzeugaufstellung mit speichern kann, so dass die bei der Auswahl des Objekts dann auf der 
Karte dargestellt werden kann.

#### Administrationsoberfläche

![eMonitor Admin]({{ site.url }}/eMonitor/images/admin.jpg) Im Administrationsbereich kann man alle Einstellengen vornehmen, 
die für den Betrieb erforderlich sind. Dabei ist dieser Bereich über einen Authentifikationsmechanismus geschützt, dass 
nicht jeder an die Einstellungen heran kommt.

Folgende Module sind hier konfigurierbar (Auszug):

##### Ausrückeordnung

Für jedes verfügbare Alarmstichwort kann eine eigene Ausrückeordnung definiert werden. Zusätzlich ist es möglich eine 
Standardfahrzeugreihenfolge zu definieren, die immer dann zum Einsatz kommt, falls ein Stichwort nicht explizit 
definiert wurde.
Dabei wird für jedes Stichwort unterschieden zwischen Primärfahrzeug, Folgefahrzeug und Sondermittel. 
Es sind beliebig viele Einheiten konfigurierbar, so dass diese getrennt voneinander behandelt werden können. Für jede 
Einheit ist dabei ein Standardort vorgesehen, um eine Trennung von Einsatzgebieten zu ermöglichen. Genau das war auch 
der Grund für die Entwicklung der Software, weil das in den bisher bekannten Lösungen nicht vorgesehen war, dass 
verschiedene Einheiten über das selbe FAX alarmiert werden.
Die Ausrückeordnung kann einfach per Excel verwaltet und geändert werden und dann wieder neu in eMonitor eingespielt 
werden. Der Export aus eMonitor nach Excel ist ebenfalls möglich.

##### Fahrzeug-/Materialverwaltung

Für jede definierte Einheit können beliebig viele Fahrzeuge oder Ausrüstungsgegenstände definiert werden. Diese stehen 
dann für die Ausrückeordnung zur Verfügung. Das Material kann in beliebige Kategorien eingeteilt werden, so dass z.B. 
Farhzeuge, Anhänger und sonstiges Material getrennt voneinander behandelt werden kann. Beim Erstellen eines Einsatzes 
stehen dann alle aktiv-geschalteten Gegenstände zur Auswahl.

##### Monitorkonfiguration

eMonitor kann beliebig viele Monitore ansteuern. Dabei bekommt jeder eine ID zugeordnet und kann fortan auf 
verschiedene Events reagieren und entsprechende Inhalte anzeigen. Dabei können auch mehrere Monitore den selben Inhalt 
anzeigen.
Es werden Layouts definiert, die beliebige Bereiche des Monitors füllen können. Die Bereiche kann man dabei per 
Drag&Drop in einem Raster definieren und zusammenbauen. Dann werden den Layouts Events zugeordnet, zu denen die 
Darstellung auf den Bildschirmen dargestellt werden soll.
Dadurch ist es beispielsweise möglich, dass man in der Fahrzeughalle mehrere Bildschirme mit den Alarmdeteils mit 
Straßenkarte, ausrückenden Fahrzeugen und Alarmdetails darstellen kann. Auf einem anderen Monitor kann auch nur eine 
Gesamtübersichtskarte mit den Markierungen der Einsatzstellen anzgezeit werden, um die Übersicht zu behalten. Das ist 
gerade für Unwettereinsätze sinnvoll, wenn mehrere Einsatzstellen gleichzeitig abgearbeitet werden sollen.
Dabei ist das System so ausgelegt, dass lediglich eine Netzwerkverbindung zwischen Monitor und eMonitor-Server bestehen 
muss. Somit lassen sich die Monitore an nahezu beliebigen Orten installieren.

##### Event-Handling

Im System werden verschiedene Events ausgelöst, auf die Module reagieren können. Wenn beispielsweise ein Alarmeingang 
signalisiert werden soll, kann man auf Monitoren ein spezielles Layout anzeigen lassen, bis die Auswertung 
abgeschlossen ist und dann die Alarmdetails ermittelt wurden. Es können beliebige Module miteinander kombiniert werden, 
so dass auch komplexe Abläufe ermöglicht werden. Dabei kann auch zeitgesteuert der Monitor wieder in den Ruhezustand 
geschickt werden, wenn keine Anzeige vorliegt.

##### Straßenkonfiguration

Es können beliebig viele Orte definiert werden. Zu jedem Ort können beliebig viele Straßen definiert werden. In den 
Straßen dann Hausnummern. Diese Informationen können automatisiert von OpenStreetMap importiert werden. Das hat den 
großen Vorteil, dass die Daten allen zur Verfügung stehen und man selber auch Ergänzungen bei OpenStreetMap machen 
kann, die dann wieder Allen Nutzern zur Verfügung stehen.
Diese Informationen stehen dann auch Offline zur Verfügung, falls mal keine Internetverbindung vorhanden ist. Wenn bei 
der Alarmauswertung eine Straße oder Ort nicht lokal gefunden werden sollte, versucht eMonitor über WebServices eine 
genaue Koordinate zu ermitteln und diese dann auch zu speichern. Gerade bei überörtlichen Einsätzen ist das sehr 
hilfreich.
