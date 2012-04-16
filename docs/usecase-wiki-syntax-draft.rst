
= UC 088 CAD Dokumente eines Materials bearbeiten =

**Scope:** PDMLink - SYstem

**Ebene:**  (blau - Meereshöhe)

**Story:**
  Ein Konstrukteur möchte eine Konstruktionsänderung durchführen und muss dazu
  CAD-Dokumente (Teile, Baugruppen, Zeichnungen) vom Typ MOD, ETZ, ZSB eines
  Materials (ADMPart) bearbeiten.
  
**Haupt Akteur:** Konstrukteur (Creator)

Stakeholder / Interessen
------------------------

QM-Manager
  möchte einen erkannten Konstruktionsfehler nachvollziehbar (mit Historie) nach
  den Regeln des Änderungs- und Archivierungsprozesses beheben lassen.

Produktmanager
  möchte ein Material nach Kosten oder Verwendbarkeit in einer Plattform
  nachvollziehbar nach den Regeln des Änderungsablaufs optimieren

Konstrukteur
  möchte die von der Änderung betroffenen PDMLink-DIS unter Einhaltung des
  festgelegten Änderungsablaufs mit minimalem Arbeitsaufwand zügig
  aktualisieren.

Firma
  möchte eine qualitativ hochwertiges Produkt bei geringen Kosten vermarkten und
  das Firmen-Know-How schützen.

Primäres Erfolgsszenario
------------------------

1 Dokumente suchen und zum Workspace hinzufügen
   Konstrukteur sucht die betroffenen Dokumente und fügt sie seinem
   Arbeitsvorrat (Workspace) hinzu. (-> UC 118 CAD Dokument suchen)

2 Dokumente Revisionieren
   Der Konstrukteur revisioniert (Statusänderung von 40 auf 10) die zu ändernden
   Dokumente, um diese bearbeiten zu können (-> UC 300 Dokument versionieren-)

3 Dokumente zur Bearbeitung sperren
   Der Konstrukteur sperrt die revisionierten Dokumente für sich zur exklusiven
   Bearbeitung (checkout).

4 Konstruktiv ändern
   Der Konstrukteur führt konstruktive Änderungen in Pro/E  durch.

5 Metadaten aktualisieren
   Der Konstrukteur aktualisiert die Metadaten/Attribute der Dokumente
   (Attribute-Manager). Dazu legt er eine neue Änderungszeile für seine
   erzeugten Versionen im Schriftkopf an und trägt die mit dem
   Konstruktionsauftrag erhaltene Änderungsnummer ein.
   (-> UC ??? Attribute-Manager-)

6 Modelcheck
   Der Konstrukteur führt eine Prüfung der Dokumente durch (Modelcheck).
   (-> UC ??? Modelcheck-)

7 Speichern/Checkin
   Der Konstrukteur speichert die Dokumente (Modelle und Zeichnungen) in PDMLink
   und löst die Sperre (Upload / Checkin).

8 Validieren und Iteration erzeugen
   Das System validiert die Attribut - Änderungen und:

   - legt eine neue Iteration der CAD-Dokumente an. (-> UC ???  Attribut-Validierung CAD Dokument-)
   - erzeugt eine Verknüpfung zum Material (ADMPart) für die erzeugte Revision
     -> siehe Verknüpfungsregeln

Fehlerbehandlung
----------------

1.1 Rechte für abhängige Dokumente fehlen
   Hinzufügen zum Arbeitsvorrat schlägt fehl, weil keine "extended-user" Rechte
   für abhängige Objekt bestehen.

   1.1.1 System meldet Fehler und die betroffenen Dokumente
   1.1.2 Konstrukteur kann die Bearbeitung nicht durchführen

6.1 Modelcheck meldet Fehler

   6.1.1 Konstrukteur behebt die Fehler im Dokument.
   6.1.2 Konstrukteur führt die Prüfung erneut durch.

8.1 Checkin schlägt fehl
   System meldet Fehler und die betroffenen Dokumente und bricht den Checkin -
   Vorgang für **alle** Dokumente ab

   8.1.2 Konstrukteur behebt die gemeldeten Fehler.
   8.1.1 Konstrukteur wiederholt UC ab Punkt 7.

Regeln
------

1. Hinzufügen zum WS funktioniert nur bei "extended-user" Berechtigung
2. Nur mit Creator Berechtigung
3. -7. Nur mit Creator Berechtigung
8. Regeln zur Verknüpfung ...

