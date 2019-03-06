---
layout: index
permalink: /install/image/index.html
breadcrumb: eMonitor Beispiel-Image
---

### eMonitor Beispiel-Image

Zum einfachen Test steht eine komplette eMonitor-Installation als VirtualBox vfd-Image zur Verfügung. Damit kann eMonitor ohne vorherigem Einrichtungsaufwand getestet werden.

#### Image Download und Nutzung

Unter [**dropbox**][1]{:target="_blank"} steht das gepackte Image zum Download bereit. (gepackt 1.6GB)

Nach dem Entpacken der Datei kann die *vfd-Datei* als Festplatte in einer virtuellen Maschine unter z.B. VirtualBox eingebunden werden.

#### Daten zum Image

- Betriebssystem: Ubuntu 16.04.2 LTS
- Python: 2.7.12
- Benutzername/Passwort: *emonitor/emonitor*
- Installationspfad: */srv/emonitor*
- eMonitor-Server starten per Script: */home/emonitor/run.sh*
- Datenverzeichnis: */home/emonitor/data*

Das Image ist voll eingerichtet und der Webserver ist über Port **8080** erreichbar. Zum Testen der Faxauswertung liegt im Home-Verzeichnis ein Beispielfax, das über den Admin-Bereich getestet werden kann.

#### eMonitor Update

eMonitor kann über *github* aktualisiert werden

 > git pull origin master


[1]: https://www.dropbox.com/s/zkt2r4i62owzayw/emonitor.tar.gz?dl=0
