# Einsatztyp

## Übersicht

In der oberen Liste werden alle definierten **Einsatztypen** aufgeführt. Für jedes FAX-Layout ist der passende FAX-Interpreter erfoderlich.

In der Liste der **FAX-Interpreter** werden die vorhandenen Interpreter aufgelistet. Dabei kann über das Upload-Formular am Ende der Seite ein weiterer Interpreter hochgeladen werden, der dann konfiguriert werden kann und als Einsatztyp genutzt werden kann. Der _Dummy_ sollte nicht zum Einsatz kommen, da er keine Funktionalität beinhaltet.

## Übersicht Details

Für jeden Interpreter gibt es verschiedene Bereiche, die jeweils mit einem Schlüsselwort eingeleitet werden. Wenn der Bereich im Alarm mit übernommen werden soll, dann muss ein Bereichssschlüssel angegeben werden. Zusätzlich kann noch eine Bearbeitungsmethode angegeben werden, die dne Textinhalt korrekt formatiert.

Bereiche können bearbeitet und gelöscht werden. In der Regel sollte es nicht erforderlich sein, an der Stelle Änderungen vorzunehmen, da die Interpreter auf die jeweilige Leitstelle angepasst wurden.

## Bearbeiten Einsatztypen

Für jeden Interpreter können verschiedenen Parameter bearbeitet werden:

* Typname: Name des Interpreters zur Unterscheidung
* Interpreter/Auswerter: Auswahl des Interpreters zur FAX-Auswertung
* Stichworte: Liste (zeilenweise) mit Worten, die auf dem FAX vorhanden sein müssen, dass der Interpreter genutzt wird
* Variablen: Innerhalb eines Auswerters können bestimmte Worte als Variablen deklariert werden, die anschließend mit Worten hinterlegt werden.
 Beispiel: Variable \_bma\_ wird im Text als *Brandmeldeanlage* genutzt und überprüft.
 Dabei können auch reguläre Ausdrücke verwendet werden.
 Beispiel: \_street\_ : *Straße|Platz|Weg*
