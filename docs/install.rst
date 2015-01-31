Installation (DE)
=================

Hier kommt die Anleitung für die Installation

Installation unter Linux
------------------------

Nach der Installation von Python 2.x und pip sind folgende Schritte erforderlich:

>>> git clone https://github.com/seiferta/eMonitor.git emonitorpip install -r requirements.txt

Installation von ImageMagick (Wird zur Umwandlung von PDF-Dateien nach PNG benötigt)

>>> apt-get install imagemagick

Installation von ghostview (wird zur Umwandlung der PDF-Dateien benötigt)

>>> apt-get install ghostview

Installation von Ghostscript (gsprint wird zum Ausdruck der PDF-Alarmansicht benötigt)

>>> apt-get install ghostscript

Installation von tesseract

>>> apt-get install tesseract-ocr tesseract-ocr-deu

Installation unter Windows
--------------------------

Nach der Installation von Python 2.x und pip sind folgende Schritte erforderlich:
(Falls pip nicht direkt installiert werden kann, unter https://bootstrap.pypa.io/get-pip.py liegt ein Script, mit dem man pip direkt mit python installieren kann, eine Anleitung ist unter https://pip.pypa.io/en/latest/installing.html zu finden)

>>> git clone https://github.com/seiferta/eMonitor.git emonitor

Unter Windows kann man mit pip einige Python-Pakete nicht direkt installieren:

- Pillow: http://www.lfd.uci.edu/~gohlke/pythonlibs/#pillow
- Reportlab: http://www.lfd.uci.edu/~gohlke/pythonlibs/#reportlab

Anschließend folgt dann die Installation der restlichen Python-Abhängigkeiten mit pip

>>> pip install -r requirements.txt

Folgende weitere Softwarepakete bzw. Teile davon werden noch benötigt:

- ImageMagick: convert.exe http://www.imagemagick.org/script/binary-releases.php
- GhostView: gsprint.exe http://pages.cs.wisc.edu/~ghost/gsview/get50.htm
- GhostScript: http://www.ghostscript.com/download/gsdnld.html
- Tesseract: tesseract.exe http://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02-win32-portable.zip
