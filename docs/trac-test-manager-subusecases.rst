UC020 Tests zum Testplan hinzufügen
===================================

Story
  Der Testmanager möchte Tests zu einem Testplan hinzufügen und diese
  einem oder mehreren Testern zuweisen. Die Tests liegen bereits in einem 
  vordefinierten Format vor und sollen referenziert werden.

**Hauptakteur:** Testmanager

**Scope:** Trac, TestPlan-Macro

Interessen / Stakeholder
------------------------

Testmanager
  möchte Tests zu einem Testplan hinzufügen.

Tester
  möchte sehen, welche Tests er bearbeiten muss.

Testmanager
  möchte gleich mehrere Tests auf einmal (Testsuiten) durch die Angabe von
  Pfaden oder regulären ausdrücken einem Tester zuordnen.

Primäres Erfolgsszenario
------------------------

2.1 Testmanager fügt Macro
    zum Listen der Testcases im Testplan (Wikipage) hinzu.

2.2 Testmanager referenziert Tests
    innerhalb des Macros über die Angabe eines Pfades oder einer ID

2.3 Testmanager wählt Tester aus
    über die Angabe einer Userid

2.4 Testmanager bestätigt die Änderung der Wikipage
    das Macro wird ausgeführt und listet die hinzugefügten Testcases
    in Wikinotation.

Erweiterungen
-------------

2.1.1 Zuweisung von Tests über reguläre Ausdrücke

2.1.2 Zuweisung von Testsuiten über ihren Pfad

2.2.1 Zuweisung von mehreren Testern oder Gruppen von Testern

Mögliches Trac-Macro zur Einbettung eines Testplans
---------------------------------------------------

::

  {{{
  #!TestPlan
  Id: TA14
  Testart: UsecaseTest 
  Build: DC-3.1.1
  Konfiguration: IE7-Win, FF-LUX
  Usecases: BaugruppenVerwalten, ObjekteSuchen

  Testcases/SaveAsEinerBaugruppe lmende
  Testcases/ErzeugenEinerBaugruppe lmende
  Testcases/Suchen/* mmuster
  }}}

UC030 Testcase erstellen
========================

Story
  Der Testmanager erstellt Testcases.

**Hauptakteur:** Testmanager

**Scope:** Trac mit TestManPlugin

Interessen / Stakeholder
------------------------

Testmanager
  möchte neue Testcases erstellen um diese in einen Testplan übernehmen zu 
  können.

Primäres Erfolgszenario
-----------------------

1 Testmanager wechselt in den Testbereich
  und erstellt einen neuen Testcase.

2 Testmanager trägt den Testcase mit Hilfe der vorgegebenen Testsyntax ein.

3 Testmanager speichert den Test und bekommt ihn angezeigt.

Fehler / Erweiterungen
----------------------

1.1 Der Testmanager wählt "Tests importieren" aus und importiert Tests aus einer
    vorhandenen Datei

3.1 Die Syntax ist fehlerhaft und der Testmanager bekommt den Testcase nicht in
    der gewünschten Form angezeigt

UC040 Testmanager startet den Testplan
======================================

Story
  Der Testmanager startet den Testplan und ermöglicht den Testern, noch nicht
  durchgeführte Tests zu wählen und auszuführen.

**Hauptakteur:** Testmanager

**Scope:** Trac mit TestManPlugin

Interessen / Stakeholder
------------------------

Testmanager
  möchte einen Testplan zum Termin starten und so den Testern ermöglichen, die
  Ihnen zugewiesenen Testcases oder von Ihnen ausgewählte durchführen zu
  können.

Vorbedingungen
--------------

- Testmanager hat den Testplan als Wikiseite erstellt und überprüft.

Primäres Erfolgszenario
-----------------------

1 Testmanager wechselt in den Testbereich
  wählt den vorher erstellten Testplan aus einer Liste noch nicht gestarteter
  Testpläne und startet diesen zur Ausführung.

2 Das TestManPlugin extrahiert die Testcases
  aus dem TestPlan-Macro und speichert diese mit der ID des Testplans im Status
  "nicht getestet".

3 Das TestManPlugin extrahiert die Testcaseaktionen
  durch Parsen der Testcases der gefundenen Testcaseliste und speichert diese im
  Status "nicht getestet".

4 Das System stellt eine Zusammenfassung 
  der auszuführenden Tests ähnlich wie bei der Auswertung dar. 

UC050 Tester wählt Tests und führt Testaktionen durch
=====================================================

Story
  Tester wählt Tests und führt die Aktionen nach der Beschreibung durch, für
  fehlgeschlagene oder nicht durchführbare Tests, hinterlegt er einen Kommentar
  oder öffnet ein Ticket.

**Hauptakteur:** Tester

**Scope:** Trac mit TestManPlugin

Interessen / Stakeholder
------------------------

Tester
  es gelten alle Testerinteressen aus dem Business-UsecaseTestDurchfuehren

Vorbedingungen
--------------

Testplan wurde mit UC040 gestartet.

Primäres Erfolgszenario
-----------------------

1 Tester wechselt in den Testbereich
  wählt dort einen Testcase aus einem vorher gestarteten Testplan und startet
  die Durchführung.

2 TestManPlugin listet alle gespeicherten TestcaseAktionen
  mit dem aktuellen Status und aktiviert die erste Aktion. Diese ist
  hervorgehoben und Zeigt die Details und das erwartete Ergebnis zur Aktion.

3 Tester führt aktive Aktion durch
  Er nutzt die Detailbeschreibung und kontrolliert das erwartete Ergebnis.
  Bei Übereinstimmung markiert er die Aktion als "durchgeführt".

4 Das TestManPlugin speichert
  die aktive Testcaseaktion als "durchgeführt" und aktiviert die nächste Aktion,
  bis alle Aktionen durchgeführt sind. Mit der lezten Aktion wird der Testcase
  als "durchgeführt" markiert.

Fehler / Erweiterungen
----------------------

3.1 Aktive Aktion wurde fehlerhaft getestet
  Das Ergebnis weicht vom erwarteten Ergebnis ab, der Tester markiert diese
  Aktion als "fehlgeschlagen".

  3.1.1 Tester erzeugt einen Kommentar
    mit der Fehlerbeschreibung zur Aktion, oder öffnet sofort ein Ticket, dessen
    Link dann im Kommentar abgelegt wird.

  3.1.2 TestManPlugin speichert die
    aktive Testaktion als "fehlgeschlagen" und aktiviert die nächste Aktion.

  3.1.3 Tester fährt mit der nächsten Aktion
    fort (falls möglich) oder bricht den Testcase ab, ohne weitere Aktionen
    durchzuführen.

3.2 Tester möchte zur aktiven Aktion Anmerkungen
  hinterlegen.

4.1 Mindestens eine der Testaktionen war fehlerhaft
  Das TestManPlugin speichert den Testcase als "zu überprüfen".

4.2 Tester möchte eine andere Testaktion aktivieren
  indem er diese anwählt, so kann er bereits durchgeführte Aktionen wiederholen
  oder bestimmte Aktionen überspringen.

4.3 Der Tester schließt den Testcase ab
  indem er den Status 'passed' oder 'failed' wählt.

