Einsatzobjekte
==============

Als Einsatzobjekt können Gebäude oder Einrichtungen definiert werden, für die besondere Informationen vorliegen. Das 
können sein:

- **Objektname:** Name, unter dem das Objekt bekannt ist
- **Straße und Hausnummer:** Genaue Adresse
- **Einsatzobjekttyp:** Auswahlliste mit Typen, die hinterlegt werden können
  `Typen-Definition </admin/alarmobjects/types>`_
- **Einsatzplan:** Nummer des Einsatzplanes der hinterlegt wurde
- **aktiv:** Nur aktive Objekte werden im Frontend zur Auswahl angeboten
- **Brandmeldeanlagennummer:** Nummer der Brandmeldeanlage
- **Bemerkung:** Freitextfeld für die Bemerkung
- **Kartenposition:** Auf der Karte kann die Position des Einsatzobjektes bestimmt werden. Automatisch wird anhand der
  Adresse die Position zu bestimmen. Manueller Engriff ist jederzeit möglich.

Diese Informationen sind in Tabs organisiert:

- **Basisdaten**
  Basisdaten zum Einsatzobjekt

- **Erweiterte Informationen**
  Zusätzliche Informationen, die in der `Felder-Definition </admin/alarmobjects/fields>`_ erzeugt wurden.

- **Ausrückeordnung**
  Für jedes Einsatzobjekt kann *eine* Ausrückeordnung definiert werden, die für alle Alarmstichworte herangezogen wird
  und die Definition der AAO für das Stichwort überschreibt.
- **Dateien zum Einsatzobjekt**
  Es können beliebig viele Dateien hinterlegt werden, die über das Frontend zum Download bereit stehen.
