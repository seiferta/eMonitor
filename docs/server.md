---
layout: index
permalink: /server/index.html
breadcrumb: Server
---

### eMonitor-Server

Die eMonitor Software bietet eine Reihe unterschiedlicher Oberflächen:

#### Standardoberfläche

die Standardoberfläche ist über den Browser zu erreichen unter der Url http://localhost (opt. mit Portangabe).
Diese Oberfläche stellt den Standard dar und kann mit verschiedenen Modulen konfiguriert werden.

[**weitere Details**][1]

#### Administrationsoberfläche

die Administrationsoberfläche ist direkt über den Browser zu erreichen unter der Url http://localhost/admin (opt. mit Portangabe).
Der Administrationsbereich ist erst nach einer Authentifikation (Benutzername/Passwort Adminstrator/admin) zu erreichen. Hier können sämtliche Konfigurationen vorgenommen werden, um das System einzurichten.


[**weitere Details**][2]

#### Monitoroberfläche

die Monitoroberfläche ist über den Browser zu erreichen unter der Url http://localhost/monitor (opt. mit Portangabe). Bevor nicht mindestens ein Client über den Administrationsbereich definiert wurde, kann diese Oberfläche nicht angezeigt werden.

[**weitere Details**][3]

#### Schnittstellen

* **Faxerkennung:** für das jeweilige Fax-Layout der Alarmdepeche muss ggf. eine Anpassung der Erkennung der einzelnen Felder erfolgen. [**weitere Details**][4]
* **Eventdefinition:** Für die korrekte Verarbeitung der eingehenden Faxdepeschen ist über das Eventhandling der Ablauf zu konfigurieren. [**weitere Details**][5]


[1]: frontend
[2]: admin
[3]: monitor
[4]: ../faxchecker
[5]: ../eventhandler
