Einsatz Konfiguration
=====================

In der Einsatzkonfiguration können grundlegende Einstellungen zum Einsatz-Modul erfolgen.

Einsatz-Felddefinition
----------------------

Für jede Einheit können Felder definiert werden, die in Abschnitte untergliedert sind. Diese Felder stehen im Frontend
bei der Definition der Einsätze zur Verfügung und werden auf den Auswertungen oder Einsatzzetteln abgedruckt. Folende
Abschnitte stehen zur Verfügung:

* Alarmierung:
  Dieser Abschnitt ermöglicht die Benennung verschiedener Alarmierungswege, z.B. Schleifen, Telefon, Funk etc.
  Dabei kann ein spezieller Syntax verwendet werden. [Details].

* Bericht:
  Bietet für den Einsatzzettel ein Texteingabefeld für einen Bericht.

* Fahrzeuge:
  Die Fahrzeuge, die für den Einsatz disponiert wurden, werden automatisch für den Einsatzzettel übernommen.

* Geräte/Material:
  Besondere Gerätschaften können benannt werden, die für den Einsatz beispielsweise abgerechnet werden können und
  deshalb explizit aufgeführt werden müssen.
  Dabei kann ein spezieller Syntax verwendet werden. [Details].

* Mannschaft:
  Die Mannschaft kann in verschiedenen Kategorien erfasst werden, z.B. PA-Träger, in Bereitschaft, Einsatzleiter
  In einer späteren Ausbaustufe ist geplant, dass in einer *erweiterten* Verwaltung jedes einzelne Mitglied erfasst
  werden kann.

* Sonstige Kräfte:
  Weitere Einsatzkräfte anderer Organisationen können an dieser Stelle erfasst werden, z.B. KBI, KBM, THW, Polizei,
  Rettungsdienst
  Dabei kann ein spezieller Syntax verwendet werden [Details]

* Zeiten:
  Sämtliche relevante Zeiten können erfasst werden, darunter Alarmzeit, Aus-Zeit, An-Zeit, Ein-Zeit und Einsatzende

Einsatz-Priorisierung
---------------------

Für jeden Status eines Alarms können Fahrzeuge definiert werden, die extra ausgewiesen werden sollen. Damit ist es
möglich, dass eine Bedarfsanalyse für ein bestimmtes Fahrzeug erzeugt wird. In der Einsatzübersicht ist bei mehreren
aktiven und offenen Einsätzen erkennbar, ob weitere Kräfte erforderlich werden.

Einsatz Abschließen
-------------------

Automatisch erzeugte Einsätze könenn nach einer vordefinierten Zeit automatisch durch eMonitor geschlossen werden.
Dadurch ist kein manueller Eingriff mehr notwendig, um Einsätze zu beenden und damit vom aktiven Display zu löschen.
Falls eine *0* eingegeben wird, erfolgt kein automatisches Schließen und der Einsatz bleibt aktiv. Als Zeiteinheit
werden Minuten angenommen

Einsatz Archivieren
-------------------

Geschlossene Einsätze können automatisch nach einer bestimmten Zeit (in Stunden) archiviert werden, dass sie nicht mehr
in der Liste im Frontend auftauchen. Falls eine *0* eingegeben wurde, erfolgt keine automatische Archivierung.
