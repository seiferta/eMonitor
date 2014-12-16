Monitorkonfiguration
====================

Es können beliebig viele Monitore definiert werden, die jeweils für die unterschiedlichen Trigger/Events im System 
verschiedene Darstellungen zeigen können. Für jeden Trigger/Event kann je Monitor *eine* Anzeige definiert werden.
(Die IDs beginnen bei 1)

Monitordefinition
-----------------

Für jeden Monitor können verschiedene Parameter konfiguriert werden:

- **Client-ID:** Nummer des Monitor, beginnend bei 1. Die Client-Software auf dem Monitor muss mit dieser ID gestartet
  werden, dass der Client angesprochen wird.
- **Name:** sprechender Name des Monitors, zur besseren Unterscheidung.
- **Monitorausrichtung:** Hoch- oder Querformat
- **Auflösung:** Auflösung in Pixel je Richtung (z.B. 1920x1080 für FullHD)
- **Raster:** Rasteranzahl in der Horizontalen bzw. Vertikalen (z.B. 9x6 für FullHD)

Layout bearbeiten
-----------------

Für dei Layout-Definition stehen folgende Parameter zur Verfügung:

- **Monitor:**
  Für jeden Monitor kann für jeden Trigger ein eigenes Layout definiert werden. Dafür steht in einer grafischen Ansicht
  im Rasermaß die *Widgets* zur Verfügung, das durch Anklicken auf den Monitor platziert werden können.
  Die Größe der Widgets kann beliebig verändert werden. Dazu hat jedes Widget an der rechten unteren Ecke ein Symbol,
  das angeklickt werden kann. Entfernt kann das Widget werden, indem man auf das *x* an der rechten oberen Ecke klickt.

- **Theme:** Für den Monitor kann ein Theme gewählt, werden. Dabei handelt es sich um CSS-Anpassungen, die auf die Größe
  und Position des Monitors abgestimmt werden können. Standardmäßig wird ein dunkles Theme verwendet.

- **Trigger:** Auswahl, welcher Trigger/Aktion die Anzeige des Layouts auslösen soll. Hier ist eine Mehrfachauswahl
  möglich. Bereits verwendete Aktionen für diesen Monitor werden dabei deaktiviert.

- **Mindestanzeigezeit:** für jedes Layout kann definiert werden, wie lange mindestens das Layout verwendet werden soll.
  Nach dieser Zeit kann eine Änderung des Layouts erfolgen. Das ist beispielsweise bei der Einsatzanzeige sinnvoll, wenn
  merhrere Einsätze aktiv sind. Nach der Mindestanzeigezeit erfolgt dann die Umschaltung zwischen den Einstätzen.

- **Maximalanzeigezeit:** Nach dieser Zeit wird das Layout zu einem beliebigen Layout automatisch umgeschaltet.

- **Folgelayout:** Falls eine Maximalanzeigezeit gewählt wurde, sollte auch ein Folgelayout konfiguriert sein, zu dem
  dann umgeschaltet werden kann. Ist keines vorhanden, bleibt die aktuelle Anzeige so lange erhalten, bis ein neuer
  Trigger ein neues Layout ausliefern lässt.
