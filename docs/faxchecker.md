---
layout: index
permalink: /faxchecker/
breadcrumb: Faxchecker
---

### Faxerkennung

Das Layout der Faxdepeschen variiert von ILS zu ILS. Um flexibel auf die unterschiedlichen Layouts reagieren zu können, 
ist eine Programmierschnittstelle in eMonitor enthalten. Über diese Schnittstelle können die Feldinformationen angepasst an die 
Verarbeitung weitergeleitet werden. 
Standardmäßig sind folgende Layouts bereits umgesetzt und werden mitgeliefert:

- Beispiellayout ILS
- Feuerwehreinsatzzentrale München Land

#### NEU: Universeller Faxchecker auf RegEx-Basis

Es hat sich gezeigt, dass eine flexiblere Lösung notwendig ist, die alleine über Felder angepasst werden kann. Daraus ist ein neuer Faxchecker entstanden, der über Reguläre 
Ausdrücke die einzelnen Felder definiert und daraus den Einsatz erstellt. Zusätzlich besteht die Möglichkeit, dass die Definition der Layouts durch Export/Import-Schnittstellen 
einfach ausgetauscht werden kann. Diese Schnittstelle ist aktuell getestet mit folgenden Layouts:

- [**Feuerwehreinsatzzentrale München Land**][1]

- [**Integrierte Leitstelle Oberland**][2]

- [**Integrierte Leitstelle Regensburg**][3]

- [**Integrierte Leitstelle Dresden**][4]

(Definitionen als Download)

Weitere Leitstellen können ergänzt werden und an dieser Stelle heruntergelden werden, wenn sie zur Verfügung gestellt werden)

#### Schnittstelle

Im Verzeichnis *emonitor/modules/alarms/inc/* können Python-Implementierungen der Klasse *AlarmFaxChecker* (emonitor/modules/alarms/alarmutils.py) 
hochgeladen werden. Diese Implementierungen können im Administrationsbereich hochgeladen und eingebunden werden und beim Faxempfang für die Verarbeitung genutzt werden.

Dabei werden bei der Implementierung Stichworte definiert, die im Text vorkommen müssen, dass das System erkennt, dass es sich um ein Fax einer 
bestimmten Leitstelle handelt. Somit können unterschiedliche Faxdepeschen mit unterschiedlichem Layout gleichzeitig verwendet werden.

```python
# implementation of faxchecker
class ILSFaxChecker(AlarmFaxChecker):
    __name__ = 'ILS'
    __version__ = '0.1'

    ...
    sections[u'MITTEILER'] = (u'person', u'evalPerson')
    sections[u'anderer text'] = (u'', u'')
    keywords = [u'Alarmschreiben', u'ILS']
    translations = AlarmFaxChecker.translations + [u'_bab_', u'_train_', u'_street_']
    ...

    @staticmethod
    def evalPerson(fieldname, options="", **params):
        _str = ILSAlarmFaxChecker().fields[fieldname]
        # do something with the string and fill in the result field list
        ILSAlarmFaxChecker().fields['person'] = ('XYZ', 1)
        
    
    def buildAlarmFromText(self, alarmtype, rawtext):
        values = {}
        if alarmtype:
            sections = alarmtype.getSections()
            sectionnames = dict(zip([s.name for s in sections], [s.key for s in sections]))
            sectionmethods = dict(zip([s.key for s in sections], [s.method for s in sections]))
            FezAlarmFaxChecker().fields['alarmtype'] = (alarmtype, 0)
        else:  # no matching alarmtype found
            return values
            
        # do something with the rawtext, e.g. split in sections
        for l in rawtext.split(u"\n"):
            ...
            
        return values
```

##### Funktion

Der erkannte Text aus der Depesche wird mit der Definition der Layouts verglichen, das erste Layout, bei dem die Stichworte (Variable *keywords*) passen wird für die weitere Verarbeitung verwendet. Innerhalb der Implementierung der Layouts ist es dann möglich die Informationen auf die richtigen Felder des Einsatzes in eMonitor weiter zu reichen.

Die Depesche wird dabei in Sektionen eingeteilt, die über Stichworte oder Labels eingeleitet werden. Dafür muss die Methode *buildAlarmFromText* implementiert werden, die als Rückgabewert ein Dctionary mit dem *Feld*-*Werte*-*Paar* liefert, bzw. leer ist, wenn nichts erkannt wurde. Die Sektionen können dann über frei programmierbare Funktionen bearbeitet werden, so dass am Ende die korrekten Felder entstehen. Der Name der Bearbeitungsfunktionen für die einzelnen Felder müssen dabei immer mit *eval* beginnen, dass sie als solche erkannt werden können. Die Sektionen können vorkonfiguriert in der Faxchecker-Klasse vorliegen, die Zuordnung aber auch über die Administrationsoberfläche bearbeitet werden. Bearbeitungsmethoden sind optional, falls ein leerer Feldname und eine leere Bearbeitungsmethode angegeben wird, wird der Textinhalt einer Sektion nicht weiterverarbeitet.


Beispiel:

 ```
 ---------------------- MITTEILER -----------------------
 Name         : Person XY            Rufnummer: 012345678
 --------------------- EINSATZORT -----------------------
 .....
 ```
 
 In der Implementierung wird dann der Inhalt ab *Name* bis zur neuen Zeile mit den *--* an die Methode *evalPerson* übergeben. Ziel wird es hier sein, die Inhalte aus dem Feld *Name* und der *Rufnummer* an die eMonitor-Variable *person* weiter zu geben. Die Variable erwartet dabei ein Tupel aus dem Wert und einem Index, im Beispiel 1. Damit wird gezeigt, dass der Wert für das Feld bearbeitet wurde. Ansonsten wird die *0* übergeben.
 
 Auf diese Art und Weise können sämtliche Felder bearbeitet werden und an eMonitor weitergereicht werden, der daraus einen Einsatz aufbaut.
 
 [1]: {{site.github.url}}/config/FEZ.cfg
 [2]: {{site.github.url}}/config/ILS_OB.cfg
 [3]: {{site.github.url}}/config/ILS_R.cfg
 [4]: {{site.github.url}}/config/ILS_DD.cfg
 