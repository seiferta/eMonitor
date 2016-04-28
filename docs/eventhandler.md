---
layout: index
permalink: /eventhandler/
breadcrumb: Eventhandler
---

# Event und Eventhandler

eMonitor bietet unterschiedliche Events, die über Eventhandler verarbeitet werden können. Eventhandler können miteinaner verschaltet werden, somit lassen sich variable Abläufe definieren.

**Aktuell sind folgende Events vorhanden:**

* [Standardansicht](#standardansicht)
* [Observer Datei hinzugefügt](#observer-datei-hinzugefügt)
* [Observer Datei gelöscht](#observer-datei-gelöscht)
* [Einsatz hinzugefügt](#einsatz-hinzugefügt)
* [Einsatz Status geändert](#einsatz-status-geändert)

**Aktuell sind folgende Eventhandler vorhanden:**

* [MonitorServer](#monitorserver)
* [Text Erkennung](#text-erkennung)
* [Textoptimierung](#textoptimierung)
* [Alarmerstellung](#alarmerstellung)
* [Drucken](#drucken)
* [Alarm Typ](#alarm-typ)
* [Script](#script)

Events sind Funktionen, die über Eingabe- und Ausgabewerte verfügen. Die Werte können intern mit der Funktion bearbeitet werden und anschließend weitergereicht werden. Events können aber auch ohne weitere Verarbeitung Signale oder andere Events auslösen. Es ist darauf zu achten, dass keine externen Abhängigkeiten bestehen, so dass sich Events beliebig zu Ketten aneinanderreihen lassen. Es muss nur darauf geachtet werden, dass die notwendigen Parameter korrekt definiert werden.

Innerhalb der Event-Ketten werden die Parameter der einzelnen Events *gesammelt*, so dass die Ausgabewerte für die Folgeevents auch wieder als Eingabeparameter zur Verfügung stehen. Standardmäßig werden *incomepath* und *filename* geliefert und können somit bereits vom ersten Event als Eingabewert genutzt werden.

# Events

## Standardansicht

Event wird immer dann ausgelöst, wenn die Standardansicht an die Clients gesendet wird.

## Observer Datei hinzugefügt

Die Verzeichnisüberwachung startet dieses Event, wenn eine neue Datei im Verzeichnis gefunden wurde. Das geschieht normalerweise immer dann, wenn eine neue Alarmdepesche per Fax eingeht und als Datei im *Income*-Verzeichnis abgelegt wird.

## Observer Datei gelöscht

Nach der Verarbeitung der Alarmdepesche wird die Datei aus dem *Income*-Verzeichnis gelöscht und dieses Event ausgelöst.

## Einsatz hinzugefügt

Wenn ein neuer Einsatz in eMonitor erzeugt wurde, wird dieses Event ausgelöst.

**Achtung:** Das Event wird erst ausgelöst, wenn der Einsatz den Status "aktiviert" erhält. Das passiert automatisch immer, wenn der Alarm per Depesche eingeht. Wenn manuell ein Einsatz angelegt wird, muss dieser explizit aktiviert werden.

## Einsatz Status geändert

Jedes Mal, wenn der Status eines Einsatzes geändert wird, wird das Event ausgelöst.

# Eventhandler

## MonitorServer

**Funktion:** sendet ein Ping an die Clients zur Aktualisierung der aktuell angezeigten Seite auf den Clients.

**Parameter:** keine


## Text Erkennung

**Funktion:** Startet bei Bedarf die Konvertierung der Eingabedatei zu einem Bildformat, das per OCR-Texterkennung ausgelesen wird. Der erkannte Text wird zurückgegeben.

**Parameter:**

 * Eingabe
   * path: *incomepath* - Pfad zur Datei, die verarbeitet werden soll
   * filename: *filename* - Dateiname der Datei, die verarbeitet werden soll
 * Ausgabe
   * text: *text* - Variable, in der der Ausgabewert, der erkannte Text, vom Event geliefert wird


## Textoptimierung

**Funktion:** Startet die Textoptimierung, die über den Administrationsbereich konfiguriert werden kann. Hier wird unter Anderem eine Textersetzung angestoßen, die oft falsch erkannte Buchstaben oder Worte korrigiert.

**Parameter:**

 * Eingabe
   * text: *text* - Variable, in der der Rohtext geliefert wird
 * Ausgabe
   * text: *text* - Variable, in der der Ausgabewert, der überarbeitete Text, vom Event geliefert wird


## Alarmerstellung

**Funktion:** Aus den vorliegenden Textinformationen wird ein eMonitor-Einsatz erzeugt und in der Datenbank gespeichert. Gleichzeitig wird ein weiteres Event *

**Parameter:**
 
 * Eingabe
   * text: *text* - Variable, in der die Textinformationen geliefert werden
 * Ausgabe
   * id: *id* - Variable, in der die ID des neu erstellten Einsatzes geliefert wird
   * fields: *fields* - Liste mit Feldname-Werte Tupeln zur weiteren Verarbeitung

## Drucken

**Funktion:** Sämtliche Einsätze mit Status *aktiviert* werden an den definierten Drucker geschickt. Das Layout, das gedruckt werden soll, kann dabei über Parameter in der Druckerdefinition erstellt werden.

**Parameter:**

 * Eingabe
   * printerid: *printerid* - Definition des Druckers bzw. Layout

## Alarm Typ

*todo*

## Script

*todo*
