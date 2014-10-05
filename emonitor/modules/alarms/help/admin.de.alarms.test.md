# Testverarbeitung

Um die korrekte Auswerung der FAXe zu testen, kann über eine Testverarbeitung ein Test gestartet werden, der die Schritte,
 die unter [Eventhandling](/admin/events) konfiguriert sind, nacheinander ausführt, aber am Ende keinen Einsatz in der Datenbank anlegt.

Es werden keine Meldungen an die Clients/Monitore geschickt.

### Datei hochladen

Lokale Beispieldatei auswählen und anschließend "Datei hochladen und verarbeiten" anklicken.

### Verarbeitung startet

Anschließend wird die automatische Verarbeitung der Datei gestartet und in Tabs werden die Ergebnisse der eizelnen
 Verarbeitungsschritte angezeigt.

Falls in einem Schritt Fehler auftreten, werden diese im Schritt auf dem Tab angezeigt. Als letzter Schritt sollte eine
 Liste aller Attribute, die für den Einsatz gefunden wurden, angezeigt werden.
