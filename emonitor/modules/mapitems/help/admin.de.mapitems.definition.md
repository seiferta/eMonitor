# Definition

In der Definition der Kartenobjekte stehen folgende Felder zur Verfügung:

* **Name:** Name des Objektes, z.B. Hydranten
* **Filter:** Filter der Objekte aus OpenStreetMap
    
    ```emergency="fire_hydrant"```
    
* **Attribute:** Liste (zeilenweise) der zu kopierenden Attribute des Objektes
    
    ```id```  
    ```lat```  
    ```lon```  
    ```fire_hydrant``` 
      
* **Kategorieschlüssel:** Liste mit Werten/regulären Ausdrücken, bei denen die Objekte automatisch beim Ausdruck auf 
der Karte mit aufgedruckt werden.
    
    ```B[1-9]```  
    ```BMA ```
    
    listet das Objekt bei allen Brand-Stufen und bei BAM Einstäzten
    
* **Parameter:** Formatvorlage, in die das Objekt eingebunden werden soll. Aktuell sind folgende Vorlagen vorhanden:
    * Hydranten
    * Feuerwehrzufahrten (ungenutzt)
    
* **Tileserver bereitstellen:** Wenn gewählt, wird aus den Objekten ein Tile-Layer erzeugt, der im Frontend 
teiltransparent über die Karte gelegt werden kann (checkbox-Auswahl)  

    Wenn die Option ausgewählt wurde, dann muss der Button *Tiles für Karte erzeugen* bei Änderungen angeklickt werden, da 
erst dann der Tile-Layer erzeugt wird.
