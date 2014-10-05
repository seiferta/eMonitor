# OCR-Parameter

Die Erkennung des Textes aus dem PDF wird standardmäßig mit [tesseract](http://code.google.com/p/tesseract-ocr/) 
durchgeführt. Für die Konfiguration stehen folgende Parameter zur Verfügung:

* **Datenformate:** Es kann eine Liste (zeilenweise) der möglichen Datenformate hinterlegt werden, die von der 
OCR-Software bearbeitet werden kann. Standardmäßig sind das *pdf, tiff, jpg*.
* **Aufruf der Textverarbeitung:** Hier kann der Aufrufstring angegeben werden, der die OCR-Erkennung auslöst. Dabei
sind folgende Variablen möglich:
    * **\[basepath\]:** Installationspfad von eMonitor
    * **\[incomepath\]:** Pfad, der durch den Observer auf neue Dateien überwacht wird
    * **\[filename\]:** Dateiname der neuen Datei, wird automatisch vom Observer geliefert
    * **\[tmppath\]:** Temporäres Verzeichnis, das in den Grundeinstellungen konfiguriert wurde

Wichtig ist, dass der Pfad zu tesseract korrekt angegeben wird. Tesseract kann beispielsweise unterhalb von eMonitor 
unter *bin/tesseract/* installiert werden. Daraus ergibt sich dann ein Aufruf:

    [basepath]/bin/tesseract/tesseract [incomepath][filename] [tmppath] -l deu -psm 6 quiet custom
    
tesseract nutzt dabei folgende Parameter:

    -l deu

Die Sprache für die Erkennung soll Deutsch sein, es wird das deutsche Wörterbuch verwendet.

    -psm 6

Tesseract kann verschiedene Layouts erkennen, *6* hat sich für die Erkennung der Faxe als am besten geeignet erwiesen.

    quit

Es werden die Ausgaben von tesseract unterdrückt

    custom

Das Benutzerwörterbuch wird ebenfalls unterstützt, das unter [OCR-Vokabular](/admin/textmod/ocrcustom) angegeben werden 
kann
