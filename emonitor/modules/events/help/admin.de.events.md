# Event-Handling

Bestimmte Vorgänge in eMonitor erzeugen Events, die wiederum andere Aktionen auslösen können. Die auszulösenden 
Aktionen können frei definiert werden. Die Aktionen werden in der Reihenfolge ihrer Definition ausgeführt.

## Bearbeiten/Definition

Für ein Event kann aus einer Liste der möglichen **Event-Handler** der gewünschte ausgewählt werden. Jeder Handler hat 
dabei eine eigene Liste an Eingabe- und Ausgabe-Parametern, die konfiguriert werden müssen. Dabei kann entweder aus den 
bisher schon vorhandenen Parametern auswählen oder selber einen Wert eingeben.

Ausgabe-Parameter der vorangegangenen Aktionen können als Eingabe-Parameter der Folgeaktion gewähl werden. So können 
Parameter in einer Aktion erzeugt werden und durch weitere Aktionen verändert und weiterverarbeitet werden.
