---
layout: index
permalink: /faxchecker/
breadcrumb: Faxchecker
---

### Faxerkennung

Das Layout der Faxdepechen variiert von ILS zu ILS. Um felxibel auf die unterschiedlichen Layouts reagieren zu können, 
ist eine Programmierschnittstelle in eMonitor enthalten. Über diese Schnittstelle können die Feldinformationen angepasst an die 
Verarbeitung weitergeleitet werden. Standardmäßig sind folgende Layouts bereits umgesetzt und werden mitgeliefert:

- Beispiellayout ILS
- Feuerwehreinsatzzentrale München Land

#### Schnittstelle

Im Verzeichnis *emonitor/modules/alarms/inc/* können Python-Implementierungen der Klasse *AlarmFaxChecker* (emonitor/modules/alarms/alarmutils.py) 
hochgeladen werden. Diese Implementierungen können im Administrationsbereich eingebunden werden und beim Faxempfang für die Verarbeitung genutzt werden.

Dabei werden bei der Implementierung Stichworte definiert, die im Text vorkommen müssen, dass das System erkennt, dass es sich um ein Fax einer 
bestimmten Leitstelle handelt. Somit können unterschiedliche Faxdepechen mit unterschiedlichem Layout gleichzeitig verwendet werden.

```python
class ILSFaxChecker(AlarmFaxChecker):
    __name__ = 'ILS'
    __version__ = '0.1'
    
    ...
    sections[u'MITTEILER'] = (u'person', u'evalPerson')
    ...
    
    
    def evalPerson(fieldname, options="", **params):
        _str = ILSAlarmFaxChecker().fields[fieldname]
        # do something with the string and fill in the result field list
        ILSAlarmFaxChecker().fields['person'] = ('XYZ', 1)

```

##### Funktion

Der erkannte Text aus der Depeche wird mit der Definition der Layouts verglichen, das erste Layout, bei dem die Stichworte passen wird für die weitere 
Verarbeitung verwendet. Innerhalb der Implementierung der Layouts ist es dann möglich die Informationen auf die richtigen Felder des Einsatzes in 
eMonitor weiter zu reichen.

Die Depeche wird dabei in Sektionen eingeteilt, die über Stichworte oder Labels eingeleitet werden. Die Sektionen können dann über frei programmierbare 
Funktionen bearbeitet werden, so dass am Ende die korrekten Felder entstehen.

Beispiel:

 ```
 ---------------------- MITTEILER -----------------------
 Name         : Person XY            Rufnummer: 012345678
 --------------------- EINSATZORT -----------------------
 .....
 ```
 
 In der Implementierung wird dann der Inhalt ab *Name* bis zur neuen Zeile mit den *--* an die Methode *evalPerson* übergeben. Ziel wird es hier sein, die 
 Inhalte aus dem Feld *Name* und der *Rufnummer* an die eMonitor-Variable *person* weiter zu geben. Die Variable erwartet dabei ein Tupel aus dem Wert und 
 einem Index, im Beispiel 1. Damit wird gezeigt, dass der Wert für das Feld bearbeitet wurde. Ansonsten wird die *0* übergeben.
 
 Auf diese Art und Weise können sämtliche Felder bearbeitet werden und an eMonitor weitergereicht werden, der daraus einen Einsatz aufbaut.
 
 Weitere Informationen folgen...
 
