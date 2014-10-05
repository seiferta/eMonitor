# Bildoptimierung

Das gelieferte Fax im PDF-Format kann über eine Umwandlung zu einem Bild gewandelt werden, das die OCR-Erknnung 
bearbeiten kann. Für die Konfiguration stehen folgende Parameter zur Verfügung:
* **Bildformat zur Texterkennung:** Es besteht die Auswahl zwischen *jpg* und *png*, tesseract kommt mit *png*-Bildern 
besser zurecht.
* **Aufruf der Bildkonvertierung:** Für die Bilderstellung können eine Reihe an Variablen und Parameter verwendet 
werden  

**Variablen:**

* **\[basepath\]:** Installationspfad von eMonitor
* **\[incomepath\]:** Pfad, der durch den Observer auf neue Dateien überwacht wird
* **\[filename\]:** Dateiname der neuen Datei, wird automatisch vom Observer geliefert
* **\[tmppath\]:** Temporäres Verzeichnis, das in den Grundeinstellungen konfiguriert wurde

Für die Umwandlung kommt standardmäßig *convert* von [ImageMagick](http://www.imagemagick.org/) zum Einsatz. Das liegt 
in unterschiedlichen Versionen vor und benötigt je nach Betriebssystemversion etwas unterschiedliche Parameter, um das 
beste Ergebnis zu erzielen:

* **32-Bit:**

    ```[basepath]/bin/convert/convert -depth 32 -density 250 [incomepath][filename] -quality 100 [tmppath]```
 
* **64-Bit:**

    ```[basepath]/bin/convert/convert -resize 200% -depth 32 -density 200 [incomepath][filename] -quality 100 [tmppath]```

Damit die Konvertierung von PDF-Dateien mit *convert* funktioniert, muss zusätzlich noch 
[GhostScript](http://www.ghostscript.com/) installiert werden.
