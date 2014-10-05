# Ortsliste

Es können beliebig viele Orte definiert werden. Für jeden Ort können Straßenlisten direkt aus OpenStreetMap abgerufen 
werden. Zusätzlich kann die Standardeinheit und die Standardkarte für den Ort definiert werden.

## Ort bearbeiten

Für jeden Ort stehen folgende Parameter zur Verfügung:

* **Ortsname:** Name des Ortes, wie er auch im Frontend in der Straßenauswahl angezeigt werden soll.
* **Ortsteile:** Orte können in Ortsteile unterteilt werden, die einzelnen Straßen zugeordnet werden können. Ortsteile 
werden in einer Liste zeilenweise eingetragen.
* **Zuständige Einheit:** für jeden Ort kann die Standard-Einheit hinterlegt werden, die für diesen Ort zuständig ist.
* **Standardkarte:** Für den Ort kann eine Standardkarte gespeichert werden, die für den Ausdruck genutzt wird.
* **Ortsfarbe:** bisher nicht weiter genutzt
* **Standardort:** Ein Ort sollte als Standardort gespeichert werden. Dieser wird dann angenommen, wenn im keine 
gesonderte Klassifikation eingetragen wird und dieser Ort wird in der Straßenauswahl im Frontend als erstes angezeigt.
* **OpenStreetMap-Id:** ID von OpenStreetMap für das Ortsgebiet (optional)
* **OpenStreetMap-Ortsname:** Falls sich der Ortsname für die Anzeige im Frontend zu dem in OpenStreetMap unterscheiden
sollte, kann hier der Ortsname aus OpenStreetMap gespeichert werden. Das ist immer dann sinnvoll, wenn es sich um 
Ortsteile handelt, die anders angezeigt werden sollen.

In der Definition können auch alle Hausnummern geladen werden, die in OpenStreetMap für diesen Ort vorhanden sind.
Huasnummern können dabei folgendermaßen definiert weren:

    addr:street=XYZ-Straße
    addr:housenumber

Es müssen der Straßenname und die Hausnummer gespeichert sein.

    type=associatedStreet
    addr:housenumber
    
Es kann über eine Relation des Gebäudes zu einer Straße das Attribut *addr:housenumber* hinterlegt sein.

### Hausnummern aller Städte von OpenStreetMap laden

Es können alle Hausnummern der definierten Städte direkt von OpenStreetMap geladen werden. Das kann je nach Anzahl der 
definierten Orte länger dauern.

### Städte von OpenStreetMap laden

Wenn bereits der Kartenausschnitt definiert wurde, der über OpenStreetMap offline zur Verfügung stehen soll, kann 
eMonitor automatisch versuchen alle Orte/Städte innerhalb diese Ausschnittes zu ermitteln. Es wird dann eine Liste 
angezeigt, die alle gefundenen Städte auflistet, aus der die gewünschten per Auswahl automatisch in eMonitor importiert
werden können.  
Vorsicht: das kann je nach Größe des Kartenausschnittes länger dauern.
