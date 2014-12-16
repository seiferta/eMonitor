Kartenobjekte-Definition
========================

In der Definition der Kartenobjekte stehen folgende Felder zur Verfügung:

- **Name:** Name des Objektes, z.B. Hydranten, dieser Name wird auch im Frontend für die Kartenebene verwendet

- **Ort/Stadt:** Es kann ausgewählt werden, für welchen Ort/welche Stadt die Kartenobjekte geladen werden sollen.

- **Kategorieschlüssel:** Liste mit Werten/regulären Ausdrücken, bei denen die Objekte automatisch beim Ausdruck auf
  der Karte mit aufgedruckt werden.

  | ``B[1-9]``
  | ``BMA``
    
  listet das Objekt bei allen Brand-Stufen und bei BMA Einsäzten
    
- **Tileserver bereitstellen:** Wenn gewählt, kann aus den Objekten ein Tile-Layer erzeugt werden, der im Frontend
  teiltransparent über die Karte gelegt werden kann (checkbox-Auswahl)
  Wenn die Option ausgewählt wurde, muss der Button *Tiles für Karte erzeugen* bei Änderungen angeklickt werden, da
  erst dann der Tile-Layer erzeugt wird.

- **Parameter:** Es stehen verschiedene Konfigurationen zur Auswahl, die neben den korrekten Filtern auch Methoden
  mitbringen, um die Objekte korrekt formatiert auf der Karte anzeigen zu können. Nach der Auswahl werden automatisch
  die Werte für den *Filter* und die *Attribute* eingefüllt.
  Aktuell sind folgende Vorlagen vorhanden:

  - Hydranten
  - Feuerwehrzufahrten

Auf der Übersichtsseite können eigene Formatierer hochgeladen werden, die dann in der Liste zur Auswahl stehen.

- **Filter:** Filter der Objekte aus OpenStreetMap
    
  ``[emergency="fire_hydrant"]``
    
- **Attribute:** Liste (zeilenweise) der zu kopierenden Attribute des Objektes

  | ``id``
  | ``lat``
  | ``lon``
  | ``fire_hydrant``
