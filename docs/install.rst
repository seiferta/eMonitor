Installation (DE)
=================

Sämtliche Komponenten für eMonitor liegen für verschiedene Betriebssysteme vor und können somit auf nahezu jeder
Platform installiert werden. Nachfolgend ist die Installation für Linux und Windows-Systeme beschrieben.

Installation unter Linux
------------------------

Nach der Installation von Python 2.x sind folgende Schritte erforderlich:

1. Laden der Quellen von Github
::

 > git clone https://github.com/seiferta/eMonitor.git emonitor
 > cd emonitor
 > pip install -r requirements.txt

2. Installation von ImageMagick (Wird zur Umwandlung von PDF-Dateien nach PNG benötigt)
::

 > apt-get install imagemagick

3. Installation von ghostview (wird zur Umwandlung der PDF-Dateien benötigt)
::

 > apt-get install ghostview

4. Installation von Ghostscript (gsprint wird zum Ausdruck der PDF-Alarmansicht benötigt)
::

 > apt-get install ghostscript

5. Installation von tesseract (OCR-Software)
::

 > apt-get install tesseract-ocr tesseract-ocr-deu


Installation unter Windows
--------------------------

Nach der Installation von Python 2.x sind folgende Schritte erforderlich:
(Falls pip nicht direkt installiert werden kann, unter https://bootstrap.pypa.io/get-pip.py liegt ein Script, mit dem man pip direkt mit python installieren kann, eine Anleitung ist unter https://pip.pypa.io/en/latest/installing.html zu finden)

1. Laden der Quellen von Github
::

 > git clone https://github.com/seiferta/eMonitor.git emonitor
 > cd emonitor

Unter Windows kann man mit pip einige Python-Pakete nicht direkt installieren:

- Pillow: http://www.lfd.uci.edu/~gohlke/pythonlibs/#pillow
- Reportlab: http://www.lfd.uci.edu/~gohlke/pythonlibs/#reportlab

2. Anschließend folgt dann die Installation der restlichen Python-Abhängigkeiten mit pip
::

 > pip install -r requirements.txt

3. Folgende weitere Softwarepakete bzw. Teile davon werden noch benötigt:
- ImageMagick: convert.exe http://www.imagemagick.org/script/binary-releases.php
- GhostView: gsprint.exe http://pages.cs.wisc.edu/~ghost/gsview/get50.htm
- GhostScript: http://www.ghostscript.com/download/gsdnld.html
- Tesseract: tesseract.exe http://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02-win32-portable.zip

Installation als Windows-Service
````````````````````````````````

eMonitor kann unter Windows als Dienst installiert werden, der automatisch beim Starten des Rechners aktiviert wird.
Dazu sind ein paar Dinge zu beachten:

* Dateipfade dürfen keine Netzwerklaufwerke sein, die per Zuordnung einem Buchstaben zugeordnet sind. Es sind
  ausschließlich UNC-Pfade zu verwenden.

* Der Benutzer, unter dem der Dienst läuft, muss Zugriff auf die Verzeichnisse haben

Installation:
::

 > cd emonitor
 > python service.py install

Anschließend kann der Dienst über die Dienste-Verwaltung konfiguriert werden.

Konfiguration und Hilfe
-----------------------

Parameter für convert (PDF -> PNG)
::

 > 32-bit[basepath]/bin/convert/convert32.exe -depth 32 -density 250 [incomepath][filename] -quality 100 [tmppath]
 > 64-bit[basepath]/bin/convert/convert64.exe -resize 200% -depth 32 -density 200 [incomepath][filename] -quality 100 [tmppath]

Parameter für tesseract (OCR)
::

 > 32-bit[basepath]/bin/tesseract/tesseract.exe [incomepath][filename] [tmppath] -l deu -psm  6 quiet custom
 > 64-bit[basepath]/bin/tesseract/tesseract.exe [incomepath][filename] [tmppath] -l deu -psm 6 quiet custom
