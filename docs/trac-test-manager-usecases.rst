==========================
Trac Test Manager Usecases
==========================

BUC001 Test durchführen
=======================

Story
  Der Testmanager möchte zur Vorbereitung von Tests, Testpläne aus
  exisitierenden Testcases erstellen und die Möglichkeit haben, diese Testern
  zuzuordnen.

**Hauptakteur:** Testmanager

Interessen / Stakeholder
------------------------

1 Testmanager
  möchte einfach Testpläne für die Durchführung von Tests vorbereiten.

2 Testmanager
  möchte Testcases innerhalb der Testpläne u.U. in Suiten organisieren oder
  bereits existierende Suiten in den Testplan übernehmen.

3 Testmanager
  möchte existierenden Testplänen eine SW-Version (Build) und eine oder mehrere
  Konfiguationen (z.B. IE8-Windows, Firefox-Linux) zuordnen können.

4 Testmanager
  möchte die in den Testplänen vorbereiteten Testcases oder Suiten einem oder
  mehreren Testern zuweisen können, um die Durchführung sicherzustellen,
  bestimmte Tests mehrfach testen zu lassen oder um die Testcases / Suiten nach
  Testerkompetenz zuordnen zu können.

5 Testmanager
  möchte zur Erzeugung bereits vorhandene Testpläne kopieren können,
  um bereits existierende in neuen (wiederholten Tests) wiederverwenden zu
  können.

6 Testmanager
  möchte einen Test zum Termin starten und so den Testern ermöglichen, die Ihnen
  zugewiesenen Tests oder von Ihnen ausgewählte durchführen zu können.

7 Testmanager
  möchte den Status eines laufenden Test nach offenen, gestarteten und bereits
  durchgeführten Testcases überprüfen können.

8 Testmanager
  möchte nach Abschluss des Tests, fehlgeschlagene Aktionen nachvollziehen und
  überprüfen und gegebenenfalls mit einem "durchgeführt" Status im Gegensatz zum
  Tester versehen, falls eine Fehlerbedienung oder ein anderer nicht mit der zu
  testenden Software in Verbindung stehender Grund vorlag. In diesem Fall möchte
  er einen Prüfkommentar hinterlegen.

9 Testmanager
  möchte nach Abschluss des Tests falls noch nicht geschehen, für
  fehlgeschlagene Testaktionen Tickets öffnen.

10 Testmanager 
  möchte einen Test nach Überprüfung/Korrektur abschließen und anschließend nach
  Aktionen, Testcases und erzeugten Tickets auswerten.

11 Tester
  möchte noch nicht durchgeführte Testcases eines Tests auswählen können, um
  diese durchzuführen. Dabei möchte er aus der Liste ihm zugewiesener, nicht
  zugewiesener und allen unterscheiden können.

12 Tester
  möchte zwischen den Schritten eines laufenden Tests springen können um diese
  z.B. wiederholen oder überspringen zu können.

13 Tester
  möchte für eine fehlgeschlagene Testaktion einen Kommentar hinterlegen oder
  falls er dazu berechtigt ist, sofort ein Ticket öffnen, in welchem die
  durchgeführten Testaktionen und der Testcase automatisch aufgeführt werden und
  er die Fehlersituation verständlich beschreiben kann.

Primärer Erfolgsablauf
----------------------

1 Testmanager erzeugt einen neuen Testplan
  (als Wiki-Seite) benennt ihn und legt das Datum, die zu testende SW-Version
  (Build), Konfigurationen etc. fest.

2 Testmanager wählt Testcases oder Suiten aus
  und ordnet sie dem Testplan zu.

3 Testmanager informiert die Tester
  über den bevorstehenden Test

4 Testmanager startet den Testplan
  und ermöglicht den Testern damit noch nicht durchgeführte Tests zu wählen.

5 Tester wählt Tests und führt die Aktionen
  nach der Beschreibung durch, für fehlgeschlagene oder nicht durchführbare
  Tests, hinterlegt er einen Kommentar oder öffnet ein Ticket.

6 Testmanager erhält Information über den aktuellen Zustand des Testplans
  Er kann sehen wie erfolgreich der Testplan war.

7 Testmanager überprüft/Korrigiert fehlgeschlagene Testcases
  in dem er die Tickets überprüft, Tickets erzeugt, Testergebnisse nachvollzieht
  und gegebenenfalls korrigiert und den Test mit einem Status fehlgeschlagen
  bzw. durchgeführt abschließt.

8 Testmanager wertet den Tests aus
  Dazu nutzt er das TestQuery - Macro, um Testcases, Testcaseaktionen grafisch
  darstellen zu können, er nutzt das TicketQuery-Macro um zum Test zugehörige
  Tickckets zu listen.

Erweiterungen
-------------

1.1 Der Testmanager möchte noch nicht vorhandene Tests importieren

2.1 Zuweisung von Testern

