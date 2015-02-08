Dokumentstruktur
================

Absatz
------

Ein Absatz wird in *reStructured Text* erstellt indem vor und nach dem Text je eine Leerzeile eingefügt werden.

Überschriften
-------------

Überschriften werden mit einem 7-bit-ASCII-Zeichen unterstrichen wie z.B.::

 = - ` : ' " ~ ^ _ * + # < >

Die Unterstreichung muss dabei mindestens so lang wie der Text der Überschrift sein.

Beispiel:

Überschrift 1
=============
Überschrift 2
-------------
Überschrift 3
`````````````
Überschrift 4
:::::::::::::

Diese differenzierte Textgliederung ist in *reStructured Text* mit einfachen Mitteln möglich::

 Überschrift 1
 =============
 Überschrift 2
 -------------
 Überschrift 3
 `````````````
 Überschrift 4
 :::::::::::::

Listen
======

*reStructured Text* ermöglicht mehrere Listentypen:

- Auflistungen;
- nummerierte Listen;
- Definitionslisten;
- Feldlisten;
- Optionslisten

wie auch deren Verschachtelung.

Auflistungen
------------

Für die Erstellung einer Auflistung wird vor dem Text entweder ``-``, ``*`` oder ``+`` gefolgt von einem Leerzeichen eingegeben::

 - Auflistungen
 - nummerierte Listen
 - Definitionslisten
 - Feldlisten
 - Optionslisten

Vor dem ersten und nach dem letzten Listeneintrag muss eine Leerzeile eingefügt werden.

Nummerierte Listen
------------------

#. Auflistungen;

#. nummerierte Listen;

#. Definitionslisten

hingegen setzen ein Zeichen mit einem anschließenden Punkt voraus z.B. ``#.``::

 #. Auflistungen

 #. nummerierte Listen

 #.  Definitionslisten

Definitionslisten
-----------------

Während der zu definierende Begriff als einzeilige Phrase geschreiben wird kann die Definition über mehrere Absätze gehen, z.B.::

 Begriff
  Definition

Dabei darf zwischen Begriff und Definition keine Leerzeile stehen.

Tabellen
========

+--------------------------------------------+
| Tabellenkonstruktion                       |
| mit *reStructured Text*                    |
+==============+==============+==============+
| Spalte 1     | Spalte 2     | Spalte 3     |
+--------------+--------------+--------------+
| Spalte 1     | Zelle über mehrere Spalten  |
+--------------+--------------+--------------+
| Spalte 1     | Zelle über   | Zelle über   |
+--------------+ mehrere      | mehrere      |
| Spalte 1     | Zeilen       | Zeilen       |
+--------------+--------------+--------------+

Diese Tabelle ist in *reStructured Text* so erstellt worden::

 +--------------------------------------------+
 | Tabellenkonstruktion                       |
 | mit *reStructured Text*                    |
 +==============+==============+==============+
 | Spalte 1     | Spalte 2     | Spalte 3     |
 +--------------+--------------+--------------+
 | Spalte 1     | Zelle über mehrere Spalten  |
 +--------------+--------------+--------------+
 | Spalte 1     | Zelle über   | Zelle über   |
 +--------------+ mehrere      | mehrere      |
 | Spalte 1     | Zeilen       | Zeilen       |
 +--------------+--------------+--------------+

Die senkrechte Linie kann auf *Windows* mit ``strg-alt-<`` und auf Macs mit ``alt-7`` erstellt werden. Wenn Tabellen mit *reStructured Text* angelegt werden sollen, ist darauf zu achten, dass in den Formularfeldern die Courier oder eine andere nicht-proportionale-Schrift verwendet wird.

Es gibt jedoch noch eine einfachere Schreibweise::

 =====  =====  ======
    Inputs     Output
 ------------  ------
   A      B    A or B
 =====  =====  ======
 False  False  False
 True   False  True
 False  True   True
 True   True   True
 =====  =====  ======

================
Textformatierung
================

+--------------------------------+----------------------------+--------------------------------------------+
| Code                           | Darstellung                | Anmerkung                                  |
+================================+============================+============================================+
| ``*Betonung*``                 | *Betonung*                 | Wird normalerweise kursiv dargestellt.     |
+--------------------------------+----------------------------+--------------------------------------------+
| ``**starke Betonung**``        | **starke Betonung**        | Wird normalerweise halbfett dargestellt.   |
+--------------------------------+----------------------------+--------------------------------------------+
| ````vorformatierter Text````   | ``vorformatierter Text``   | Wird normalerweise in nicht-proportionaler |
|                                |                            | Schrift dargestellt; Leerzeichen bleiben   |
|                                |                            | erhalten, Zeilenumbrüche jedoch nicht.     |
+--------------------------------+----------------------------+--------------------------------------------+

Escape
------

reStructuredText verwendet Backslashes (``\``) um Steuerzeichen darzustellen. Um einen Backslash darzustellen, müssen Sie also nur einen *escaped backslash* (``\\``) verwenden.

Die Darstellung von \*escaped*\  sieht in reStructured Text so aus::

 \*escaped*\

Ersetzungen
===========

Inhalte ersetzen und Einfügen von Unicode-Zeichen, aktuellem Datum, Klassen und  Tags.

Inhalte ersetzen
----------------

::

 .. |reST| replace:: reStructuredText

 |reST| erlaubt, komplexe Sachverhalte einfach darzustellen.

wird so dargestellt:

.. |reST| replace:: reStructuredText

|reST| erlaubt, komplexe Sachverhalte einfach darzustellen.

Und::

 |rest| erlaubt, komplexe Sachverhalte einfach darzustellen.

 .. |rest| replace:: eMonitor auf Github
 .. _|rest|: http://www.github.com/seiferta/emonitor

wird so dargestellt:

|rest|_ erlaubt, komplexe Sachverhalte einfach darzustellen.

.. |rest| replace:: eMonitor auf Github
.. _rest: http://www.github.com/seiferta/emonitor

Unicode-Zeichenkodierungen
--------------------------

::

 |copy| Veit Schiele, 2009

 .. |copy| unicode:: 0xA9

wird so dargestellt:

|copy| Veit Schiele, 2009

..  |copy| unicode:: 0xA9

Datum
-----

::

 .. |date| date:: %d. %m. %Y
 .. |time| date:: %H:%M

 Das Dokument wurde zuletzt verändert am |date| um |time| Uhr.

wird zu:

.. |date| date:: %d. %m. %Y
.. |time| date:: %H:%M

Das Dokument wurde zuletzt verändert am |date| um |time| Uhr.

Klassen
-------

::

 .. class:: landscape

 +----------------+----------------+
 | Attribut       | Wert           |
 +----------------+----------------+

.. class:: landscape

wird zu::

 <table class="landscape docutils">
     <tr><td>Attribut</td>
         <td>Wert</td>
     </tr>
 </table>

Tags
----

::

 .. role:: custom(emphasis)

 :custom:`text`

ergibt::

 <p><em>text</em></p>

.. s.a. http://docutils.sourceforge.net/docs/ref/rst/directives.html#directives-for-substitution-definitions
