---
layout: index
permalink: /install/windows/index.html
---

### Windows Installation

Nach der Installation von Python 2.x sind folgende Schritte erforderlich:
(Falls pip nicht direkt installiert werden kann, unter https://bootstrap.pypa.io/get-pip.py liegt ein Script, mit dem  
man pip direkt mit python installieren kann, eine Anleitung ist unter https://pip.pypa.io/en/latest/installing.html zu 
finden)

1. Laden der Quellen von Github:

 > git clone https://github.com/seiferta/eMonitor.git emonitor
 
 > cd emonitor

Unter Windows kann man mit pip einige Python-Pakete nicht direkt installieren:

- Pillow: http://www.lfd.uci.edu/~gohlke/pythonlibs/#pillow
- Reportlab: http://www.lfd.uci.edu/~gohlke/pythonlibs/#reportlab

2. Anschließend folgt dann die Installation der restlichen Python-Abhängigkeiten mit pip:

 > pip install -r requirements.txt

3. Folgende weitere Softwarepakete bzw. Teile davon werden noch benötigt:
- ImageMagick: convert.exe http://www.imagemagick.org/script/binary-releases.php
- GhostView: gsprint.exe http://pages.cs.wisc.edu/~ghost/gsview/get50.htm
- GhostScript: http://www.ghostscript.com/download/gsdnld.html
- Tesseract: tesseract.exe http://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02-win32-portable.zip

4. Konfiguration:

Im Basisverzeichnis liegt die Datei *emonitor.cfg.template*, die alle möglichen Knfigurationsparameter enthält. Diese 
Datei kann als Vorlage für die Konfiguration benutzt werden und kopiert nach *emonitor.cfg*

Folgende Parameter müssen kontrolliert werden:

PORT = 80

- SQLALCHEMY_DATABASE_URI = 'sqlite:///emonitor.db' [**Beschreibung**][1]
- ADMIN_DEFAULT_PASSWORD = 'admin'
- PATH_DATA = './data/'
- PATH_INCOME = './data/income/'
- PATH_DONE = './data/done/'
- PATH_TMP = './data/tmp/'
- PATH_TILES = './data/tiles/'

**ACHTUNG:**
Für den Einsatz von eMonitor in Live-Betrieb sollte MySQL als Datenbank verwendet werden, da SQLite für diesen Zweck 
nicht geeignet ist. Dafür muss auf dem Server ein MySQL-Server installiert sein und eine passende Datenbank erzeugt 
worden sein. Anschließend muss noch die Variable *SQLALCHEMY_DATABASE_URI* entsprechend angepasst werden


#### Installation als Windows-Service

eMonitor kann unter Windows als Dienst installiert werden, der automatisch beim Starten des Rechners aktiviert wird.
Dazu sind ein paar Dinge zu beachten:

* Dateipfade dürfen keine Netzwerklaufwerke sein, die per Zuordnung einem Buchstaben zugeordnet sind. Es sind
  ausschließlich UNC-Pfade zu verwenden.

* Der Benutzer, unter dem der Dienst läuft, muss Zugriff auf die Verzeichnisse haben

Installation:

 > cd emonitor
 
 > python service.py install

Anschließend kann der Dienst über die Dienste-Verwaltung konfiguriert werden.

[1]: /install/database