---
layout: index
permalink: /install/windows/index.html
breadcrumb: Windows-Installation
---

### Windows Installation

#### Vorbereitungen:

Folgende Programme werden benötigt:

- **Python 2.x**: Python in der passenden Variante für Windows, am besten als 32-Bit Version. Die Installation sollte in einem Verzeichnis erfolgen, das keine Leerzeichen besitzt. Zusätzlich sollte der Pfad zur Python-Installation in der Windows Pfad-Variable eingetragen werden, so dass in der Konsole Python einfach gestartet werden kann über:

  > python

- **Git**: Git kann zur einfachen Quellcodeverwaltung verwendet werden. Das macht die Aktualisierung der Software wesentlich einfacher. Für windows gibt es verschiedene Varianten, ausreichend ist die Kommandozeilen-Variante, die sämtliche Befehle unterstützt. Nach der Installation sollte es möglich sein, dass man in der Kommandozeile keine Fehlermeldung bekommt, wenn man folgendes eingibt:

  > git

- **ImageMagick**: Für die Konvertierung von PDF-Dateien wird *ImageMagick* in Verbindung mit *GhostScript* (AGPL-Lizenz) benötigt. Der normale Weg ist die Konvertierung von *PDF* -> *PNG* und dann eine anschließende OCR-Texterkennung mit *Tesseract*. Sämtliche Programme liegen in verschiedenen Versionen für Windows vor. An der Stelle ist es wichtig, die korrekte Version für das Betriebssystem zu installieren (**32-Bit** bzw. **64-Bit**). Bei der Installation von ImageMagick und GhostScript sollte darauf geachtet werden, dass die Pfade zu den ausführbaren Dateien wieder in die Pfad-Variable von Windows aufgenommen werden. Anschließend kann man über die Konsole testen:

  > convert

- **Tesseract**: OCR-Software für die Texterkennung aus den Alarmdepechen/Faxen. Die passende Version herunterladen und anschließend den Pfad zur tesseract.exe in die Windows Pfad-Variable eintragen.

**Pfade:**

- ImageMagick: convert.exe http://www.imagemagick.org/script/binary-releases.php
- GhostView: gsprint.exe http://pages.cs.wisc.edu/~ghost/gsview/get50.htm
- GhostScript: http://www.ghostscript.com/download/gsdnld.html
- Tesseract: tesseract.exe http://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02-win32-portable.zip

#### Installation von eMonitor

Wenn diese Voraussetzungen erfüllt sind, kann mit der installation von eMonitor begonnen werden:

1. **Quellcode** über git laden oder den Download von github in ein Verzeichnis entpacken:

 > git clone https://github.com/seiferta/eMonitor.git emonitor
 > cd emonitor
 
 Anschließend sollte in dem Verzeichnis eine Datei *requirements.txt* zu finden sein.
 
2. **Installation der notwendigen Python Bibliotheken** über die Konsole mit dem Befehl (Sicherheitshalber Konsole mit Admin-Rechten starten):

  > pip install -r requirements.txt

3. Konfiguration:

 Im Basisverzeichnis liegt die Datei *emonitor.cfg.template*, die alle möglichen Konfigurationsparameter enthält. Diese 
 Datei kann als Vorlage für die Konfiguration benutzt werden und kopiert nach *emonitor.cfg* werden.

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
 eMonitor kann sowohl mit *SQLite* (Standard), als auch mit *MySQL* als Datenbank genutzt werden.  Für den normalen Einsatz reicht die SQLite-Version vollkommen aus. Für Profi-User kann auch ein MySQL-Server verwendet werden. Dafür sind weitere Python-Pakete erforderlich. Die Datenbank URI muss dazu in der Konfiguration angepasst werden.

4. **Starten von eMonitor**: Gestartet wird der Server über den Befehl

 > python run.py
 
 Anschließend kann die Oberfläche über den Browser erreicht werden unter der URL:
 
 http://localhost
 
 Falls in der Konfiguration ein alternatives Port gewählt wurde, muss die URL entsprechend um das Port ergänzt werden.
 
 Soll der eMonitor-Server im Hintergrund gestartet werden, kann das über folgenden Befehl in der Kommandozeile passieren:
 
 > pythonw run.py
 
 Sämtliche Befehle werden aus dem Basisverzeichnis der eMonitor-Quellen gestartet.


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
